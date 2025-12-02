
# advanced_dataclasses.py
# Cztery zaawansowane przykłady użycia dataclasses w Pythonie.

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import json
import math

# 1) Podstawowy model danych
@dataclass
class User:
    id: int
    name: str
    is_active: bool = True


# 2) Walidacja w __post_init__ + default_factory
@dataclass
class Product:
    name: str
    price: float
    quantity: int = 1
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price must be non-negative")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.name = self.name.strip()


# 3) Obiekt niezmienny + pole wyliczane
@dataclass(frozen=True)
class Vector2D:
    x: float
    y: float
    magnitude: float = field(init=False)

    def __post_init__(self):
        mag = math.sqrt(self.x**2 + self.y**2)
        object.__setattr__(self, "magnitude", mag)


# 4) Dataclass jako model JSON/słownik + metody pomocnicze
@dataclass
class Person:
    name: str
    age: int
    city: str

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(data: dict):
        return Person(**data)

    @staticmethod
    def from_json(payload: str):
        return Person(**json.loads(payload))
