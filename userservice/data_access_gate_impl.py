from dataclasses import dataclass, InitVar
from dataclasses_json import dataclass_json
from typing import Dict, Optional, MutableMapping
from asyncio import Lock
from contextlib import contextmanager
from sortedcontainers import SortedDict
from .data_access_gate_interface import DataAccessGateInterface, DBUserList
from .user_types import User, DBUser, UserId


#class UsersDB(SortedDict, MutableMapping[UserId, User]):
#    pass


UsersDB = MutableMapping[UserId, User]
UsersReverseDB = Dict[User, UserId]


@dataclass_json
@dataclass
class DB:
    """
    Trivial DB
    """
    users: UsersDB
    next_user_id: UserId


class DataStorage(DataAccessGateInterface):
    """
    Simplified impl. of DataStorageInterface
    """

    def __init__(self, db: DB):
        self._db = db
        # SortedDict is necessary in order to enable optimised batch iteration
        if not isinstance(self._db.users, SortedDict):
            self._db.users = SortedDict(self._db.users)
        self._by_name = {val: key for key, val in self._db.users.items()}
        self._lock = Lock()

    @contextmanager
    def _next_id(self) -> UserId:
        yield self._db.next_user_id
        self._db.next_user_id += 1

    async def get(self, user_id: UserId) -> Optional[DBUser]:
        async with self._lock:
            user = self._db.users.get(user_id, None)
            return DBUser.from_base(user_id=user_id, user=user) if user else None

    async def add(self, user: User) -> Optional[UserId]:
        async with self._lock:
            if user in self._by_name:
                return None

            with self._next_id() as next_user_id:
                self._by_name[user] = next_user_id
                self._db.users[next_user_id] = user
                return next_user_id

    async def update(self, dbuser: DBUser) -> Optional[User]:
        async with self._lock:
            prev_user: User = self._db.users.get(dbuser.user_id, None)
            if prev_user is None:
                return None

            user: User = dbuser.to_base()
            self._by_name[user] = dbuser.user_id
            self._db.users[dbuser.user_id] = user

            return prev_user

    async def delete(self, user_id: UserId) -> Optional[User]:
        async with self._lock:
            user = self._db.users.pop(user_id, None)
            if user is None:
                return None

            self._by_name.pop(user)

            return user

    async def iterate(self, count: Optional[int] = 10) -> DBUserList:
        next_user_id: UserId = 0
        while True:
            batch = DBUserList([])

            async with self._lock:
                for user_id, user in self._db.users.irange(minimum=next_user_id):
                    batch.users.append(DBUser.from_base(user_id=user_id, user=user))

                    if len(batch.users) >= count:
                        break

            batch_len = len(batch.users)
            if batch_len == 0:
                return

            yield batch

            if batch_len < count:
                return

            next_user_id = batch.users[-1].user_id + 1

    async def size(self) -> UserId:
        async with self._lock:
            return len(self._db.users)
