
# advanced_metaclasses.py
# Kompletny zestaw 7 zaawansowanych zadań + rozwiązań dla metaklas.

from __future__ import annotations

# ============================================================
# 1) RegistryMeta – automatyczne rejestrowanie klas
# ============================================================

registry = {}

class RegistryMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        if name != "BaseRegistry":  # by nie rejestrować klasy bazowej
            registry[name] = cls
        return cls

class BaseRegistry(metaclass=RegistryMeta):
    pass


# ============================================================
# 2) RequireMethodMeta – wymuszenie obecności metody run()
# ============================================================

class RequireMethodMeta(type):
    def __new__(mcls, name, bases, namespace):
        if name != "BaseRequire":
            if "run" not in namespace:
                raise TypeError(f"Class {name} must define method run().")
        return super().__new__(mcls, name, bases, namespace)

class BaseRequire(metaclass=RequireMethodMeta):
    def run(self): ...


# ============================================================
# 3) AutoLoggedMeta – dekorowanie wszystkich metod
# ============================================================

def logged(fn):
    def wrapper(*args, **kwargs):
        print(f"[LOG] calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

class AutoLoggedMeta(type):
    def __new__(mcls, name, bases, namespace):
        new_ns = {}
        for k, v in namespace.items():
            if callable(v) and not k.startswith("__"):
                new_ns[k] = logged(v)
            else:
                new_ns[k] = v
        return super().__new__(mcls, name, bases, new_ns)


# ============================================================
# 4) AutoInitMeta – generowanie __init__ na podstawie adnotacji
# ============================================================

class AutoInitMeta(type):
    def __new__(mcls, name, bases, namespace):
        annotations = namespace.get("__annotations__", {})

        def __init__(self, *args, **kwargs):
            if len(args) > len(annotations):
                raise TypeError("Too many positional arguments")
            for (field_name, field_type), value in zip(annotations.items(), args):
                setattr(self, field_name, value)
            for field_name, field_type in annotations.items():
                if field_name in kwargs:
                    setattr(self, field_name, kwargs[field_name])

        namespace["__init__"] = __init__
        return super().__new__(mcls, name, bases, namespace)


# ============================================================
# 5) SingletonMeta – poprawny singleton z obsługą dziedziczenia
# ============================================================

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


# ============================================================
# 6) StructFactoryMeta – generowanie pól i metod z definicji __fields__
# ============================================================

class StructFactoryMeta(type):
    def __new__(mcls, name, bases, namespace):
        fields = namespace.get("__fields__", {})
        def __init__(self, **kwargs):
            for field, typ in fields.items():
                if field not in kwargs:
                    raise TypeError(f"Missing field: {field}")
                value = kwargs[field]
                if not isinstance(value, typ):
                    raise TypeError(f"{field} must be {typ}")
                setattr(self, field, value)
        namespace["__init__"] = __init__

        def as_dict(self):
            return {f: getattr(self, f) for f in fields}
        namespace["as_dict"] = as_dict

        return super().__new__(mcls, name, bases, namespace)


# ============================================================
# 7) ModelMeta – mini ORM na metaklasach
# ============================================================

class ModelMeta(type):
    models = {}

    def __new__(mcls, name, bases, namespace):
        annotations = namespace.get("__annotations__", {})
        cls = super().__new__(mcls, name, bases, namespace)
        if name != "BaseModel":
            ModelMeta.models[name] = cls
            cls.__fields__ = annotations
        return cls

    def create_table(cls):
        fields = ", ".join(f"{name} {ModelMeta.python_to_sql(t)}"
                           for name, t in cls.__fields__.items())
        print(f"CREATE TABLE {cls.__name__} ({fields});")

    @staticmethod
    def python_to_sql(t):
        return {
            int: "INT",
            float: "REAL",
            str: "TEXT",
        }.get(t, "TEXT")

    def all(cls):
        print(f"SELECT * FROM {cls.__name__};  -- mock")
        return []

class BaseModel(metaclass=ModelMeta):
    pass

def save(self):
    values = ", ".join(repr(getattr(self, f)) for f in self.__fields__)
    print(f"INSERT INTO {self.__class__.__name__} VALUES ({values});")

BaseModel.save = save
