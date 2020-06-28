from dataclasses import dataclass, asdict, field
from dataclasses_json import dataclass_json, config
from typing import NewType, List


UserId = int
UserName = str
Email = str


@dataclass_json
@dataclass
class User:
    name: UserName
    email: Email

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: 'User') -> bool:
        return self.email == other.email


@dataclass_json
@dataclass
class DBUser(User):
    user_id: UserId = field(metadata=config(field_name="id"))

    @classmethod
    def from_base(cls, user_id: UserId, user: User) -> 'DBUser':
        return cls(user_id=user_id, **asdict(user))

    def to_base(self) -> User:
        return User(name=self.name, email=self.email)


@dataclass_json
@dataclass
class DBUserList:
    users: List[DBUser]
