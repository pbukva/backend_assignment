from dataclasses import dataclass, asdict, field
from dataclasses_json import dataclass_json, config
from typing import NewType, List


#UserId = NewType('UserId', int)
#UserName = NewType('UserName', str)
#Email = NewType('Email', str)
UserId = int
UserName = str
Email = str


@dataclass_json
@dataclass
class User:
    name: UserName
    email: Email

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


@dataclass_json
@dataclass
class DBUser(User):
    user_id: UserId = field(metadata=config(field_name="id"))

    @classmethod
    def from_base(cls, user_id: UserId, user: User):
        return cls(user_id=user_id, **asdict(user))

    def to_base(self) -> User:
        return User(name=self.name, email=self.email)


@dataclass_json
@dataclass
class DBUserList:
    users: List[DBUser]
