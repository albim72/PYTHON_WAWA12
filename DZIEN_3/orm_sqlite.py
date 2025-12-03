import sqlite3
from typing import get_type_hints, Any

# === METAKLASA: buduje mini-ORM na podstawie adnotacji typów ===
class ModelMeta(type):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace)

        # Dziedziczenie pól z baz
        fields: dict[str, type] = {}
        for base in bases:
            fields.update(getattr(base, "__fields__", {}))

        # Własne adnotacje
        ann = namespace.get("__annotations__", {})
        fields.update(ann)

        cls.__fields__ = fields                 # np. {"id": int, "name": str, "active": bool}
        cls.__table__ = name.lower()            # np. "usermodel"
        return cls


class BaseModel(metaclass=ModelMeta):
    # Dla demo: baza w pamięci; możesz zmienić na "metaclasses_demo.db"
    __connection = sqlite3.connect(":memory:")
    __connection.row_factory = sqlite3.Row

    @classmethod
    def connection(cls) -> sqlite3.Connection:
        return BaseModel.__connection

    # Mapowanie typów Pythona na typy SQLite
    @classmethod
    def _python_to_sql(cls, py_type: type) -> str:
        if py_type is int or py_type is bool:
            return "INTEGER"
        if py_type is float:
            return "REAL"
        return "TEXT"

    @classmethod
    def create_table(cls) -> None:
        cols: list[str] = []
        for name, typ in cls.__fields__.items():
            col_type = cls._python_to_sql(typ)
            if name == "id":
                col_def = f"{name} INTEGER PRIMARY KEY"
            else:
                col_def = f"{name} {col_type}"
            cols.append(col_def)

        sql = f"CREATE TABLE IF NOT EXISTS {cls.__table__} ({', '.join(cols)})"
        print("SQL:", sql)
        cls.connection().execute(sql)
        cls.connection().commit()

    @classmethod
    def drop_table(cls) -> None:
        sql = f"DROP TABLE IF EXISTS {cls.__table__}"
        print("SQL:", sql)
        cls.connection().execute(sql)
        cls.connection().commit()

    def save(self) -> None:
        # zbieramy pola z obiektu
        fields: dict[str, Any] = {k: getattr(self, k) for k in self.__fields__.keys()}
        columns = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))
        values = list(fields.values())

        sql = f"INSERT INTO {self.__table__} ({columns}) VALUES ({placeholders})"
        print("SQL:", sql, "| values:", values)
        self.connection().execute(sql, values)
        self.connection().commit()

    @classmethod
    def all(cls) -> list["BaseModel"]:
        sql = f"SELECT * FROM {cls.__table__}"
        print("SQL:", sql)
        cur = cls.connection().execute(sql)
        rows = cur.fetchall()

        result: list[BaseModel] = []
        for row in rows:
            obj = cls.__new__(cls)  # pomijamy __init__
            for k in cls.__fields__.keys():
                setattr(obj, k, row[k])
            result.append(obj)
        return result


# === 7. PRZYKŁAD: model oparty na metaklasie i sqlite3 ===
class UserModel(BaseModel):
    id: int
    name: str
    active: bool


if __name__ == "__main__":
    # Czyści tabelę (dla demo)
    UserModel.drop_table()
    # Tworzy tabelę na podstawie adnotacji typów
    UserModel.create_table()

    # Tworzymy i zapisujemy rekordy
    u1 = UserModel()
    u1.id = 1
    u1.name = "Martyna"
    u1.active = True
    u1.save()

    u2 = UserModel()
    u2.id = 2
    u2.name = "Marcin"
    u2.active = False
    u2.save()

    print("Wyniki all():")
    for u in UserModel.all():
        print("->", u.id, u.name, u.active, type(u))
