from dataclasses import dataclass, InitVar
from dataclasses_json import dataclass_json
from typing import Dict, Optional
from asyncio import Lock
from contextlib import contextmanager
from sortedcontainers import SortedDict
from .data_access_gate_interface import DataAccessGateInterface, DBUserList
from .user_types import User, DBUser, UserId, UserName, Email


_UsersDB = Dict[UserId, User]
_UsersNameDB = Dict[User, UserId]


@dataclass_json
@dataclass
class _DB:
    """
    Trivial DB
    """
    store: SortedDict
    next_user_id: UserId
    by_name: InitVar[_UsersNameDB] = None

    def __post_init__(self, by_name: _UsersNameDB):
        self.by_name = { val: key for key, val in self.store.items() }


class DataStorage(DataAccessGateInterface):
    """
    Simplified impl. of DataStorageInterface
    """

    def __init__(self, db: _DB):
        self._db = db
        self._lock = Lock()

    @contextmanager
    def _next_id(self) -> UserId:
        yield self._db.next_user_id
        self._db.next_user_id += 1

    async def get(self, next_user_id: UserId) -> DBUser:
        async with self._lock:
            user = self._db.store.get(next_user_id, None)
            return DBUser.from_base(next_user_id=next_user_id, user=user) if user else None

    async def add(self, user: User) -> UserId:
        async with self._lock:
            if user in self._db.by_name:
                return None

            with self._next_id() as next_user_id:
                self._db.by_name[user] = next_user_id
                self._db.store[next_user_id] = user
                return next_user_id

    async def update(self, user: DBUser) -> UserId:
        async with self._lock:
            next_user_id = self._db.by_name.get(user, None)
            if next_user_id is None:
                return None

            self._db.by_name[user] = next_user_id
            self._db.store[next_user_id] = user

    async def delete(self, next_user_id: UserId) -> User:
        async with self._lock:
            user = self._db.store.pop(next_user_id, None)
            if user is None:
                return None

            self._db.by_name.pop(user)

            return user

    async def iterate(self, count: Optional[int] = 10) -> DBUserList:
        next_user_id: UserId = 0
        while True:
            batch: DBUserList = []

            async with self._lock:
                for next_user_id, user in self._db.store.irange(minimum=next_user_id):
                    batch.append(DBUser.from_base(next_user_id, user))

                    if len(batch) >= count:
                        break

            batch_len = len(batch)
            if batch_len == 0:
                return

            yield batch

            if batch_len < count:
                return

            next_user_id = batch[-1].next_user_id + 1

    async def size(self) -> UserId:
        async with self._lock:
            return len(self._db.store)
