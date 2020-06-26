from dataclasses import dataclass, asdict
from dataclasses_json import dataclass_json
from typing import NewType, List


UserId = NewType('UserId', int)
UserName = NewType('UserName', str)
Email = NewType('Email', str)


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
    id: UserId

    @classmethod
    def from_base(cls, id:UserId, user: User):
        return cls(id=id, **asdict(user))


@dataclass_json
@dataclass
class DBUserList(List[DBUser]):
    pass
