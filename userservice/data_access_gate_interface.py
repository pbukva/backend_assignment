from abc import ABC, abstractmethod
from typing import Optional
from .user_types import UserId, User, DBUser, DBUserList


class DataAccessGateInterface(ABC):
    @abstractmethod
    async def get(self, id: UserId) -> Optional[DBUser]:
        """"""

    @abstractmethod
    async def add(self, user: User) -> Optional[UserId]:
        """"""

    @abstractmethod
    async def update(self, user: DBUser) -> Optional[User]:
        """"""

    @abstractmethod
    async def delete(self, id: UserId) -> Optional[User]:
        """"""

    @abstractmethod
    async def iterate(self) -> DBUserList:
        """"""

    @abstractmethod
    async def size(self) -> UserId:
        """"""
