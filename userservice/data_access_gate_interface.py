from abc import ABC, abstractmethod
from .user_types import UserId, User, DBUser, DBUserList


class DataAccessGateInterface(ABC):
    @abstractmethod
    async def get(self, id: UserId) -> DBUser:
        """"""

    @abstractmethod
    async def add(self, user: User) -> UserId:
        """"""

    @abstractmethod
    async def update(self, user: DBUser) -> UserId:
        """"""

    @abstractmethod
    async def delete(self, id: UserId) -> User:
        """"""

    @abstractmethod
    async def iterate(self) -> DBUserList:
        """"""

    @abstractmethod
    async def size(self) -> UserId:
        """"""
