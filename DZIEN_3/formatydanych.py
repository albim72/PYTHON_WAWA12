import json
from typing import Any

class User:
    def __init__(self, id:int, name: str,  active:bool) -> None:
        self.id = id
        self.name = name
        self.active = active

    @classmethod
    def from_dict(cls, data:dict[str, Any]) -> "User":
        if "id" not in data or "name" not in data:
            raise ValueError("Missing required fields: id, name.")
        return cls(
            id = int(data["id"]),
            name = str(data["name"].strip()),
            active = bool(data.get("active", True)),
        )

    @classmethod
    def from_json(cls, json_str:str) -> "User":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_db_rows(cls, row: tuple[Any, ...]) -> "User":
        return cls(id = row[0], name = row[1], active = bool(row[2]))

u1 = User.from_json('{"id": 1, "name": "John"}')
u2 = User.from_db_rows((1, "John", 1))
u3 = User.from_dict({"id": 2, "name": "Jane", "active": False})

print(u1.__dict__,u2.__dict__,u3.__dict__)
print(type(u1),type(u2),type(u3))
