
# advanced_properties.py
# Zestaw 4 bardzo zaawansowanych przykładów użycia @property i descriptorów.

from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
import time
from typing import Any, Callable, List, Generic, TypeVar

# 1) Property jako warstwa domenowa (konto bankowe)
class Account:
    def __init__(self, balance_cents: int = 0):
        if balance_cents < 0:
            raise ValueError("Initial balance cannot be negative.")
        self._balance_cents = int(balance_cents)

    @property
    def balance(self) -> Decimal:
        return (Decimal(self._balance_cents) / Decimal("100")).quantize(Decimal("0.01"))

    @balance.setter
    def balance(self, value):
        value_dec = Decimal(str(value))
        if value_dec < 0:
            raise ValueError("Balance cannot be negative.")
        cents = int((value_dec * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        self._balance_cents = cents

    @property
    def is_empty(self) -> bool:
        return self._balance_cents == 0

    def deposit(self, amount):
        amount_dec = Decimal(str(amount))
        if amount_dec <= 0:
            raise ValueError("Deposit must be positive.")
        self.balance = self.balance + amount_dec

    def withdraw(self, amount):
        amount_dec = Decimal(str(amount))
        if amount_dec <= 0:
            raise ValueError("Withdrawal must be positive.")
        if amount_dec > self.balance:
            raise ValueError("Not enough funds.")
        self.balance = self.balance - amount_dec


# 2) Property lazy + cache + invalidation
class LazyModel:
    def __init__(self, loader: Callable[[], Any]):
        self._loader = loader
        self._data_cache = None
        self._loaded_at = None

    @property
    def data(self):
        if self._data_cache is None:
            print("Loading data...")
            self._data_cache = self._loader()
            self._loaded_at = time.time()
        return self._data_cache

    @property
    def loaded_at(self):
        return self._loaded_at

    def invalidate(self):
        self._data_cache = None
        self._loaded_at = None


# 3) Property triggering events (Observer pattern)
T = TypeVar("T")
class ObservableValue(Generic[T]):
    def __init__(self, initial: T):
        self._value = initial
        self._observers: List[Callable[[T, T], None]] = []

    def subscribe(self, callback: Callable[[T, T], None]):
        self._observers.append(callback)

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_value: T):
        old_value = self._value
        if old_value == new_value:
            return
        self._value = new_value
        for callback in self._observers:
            callback(old_value, new_value)


# 4) Custom descriptor (property++)
class BoundedNumber:
    def __init__(self, *, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.__dict__.get(self._name, None)

    def __set__(self, instance, value):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{self._name} must be int or float")
        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self._name} must be >= {self.min_value}")
        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self._name} must be <= {self.max_value}")
        instance.__dict__[self._name] = value


class Engine:
    horsepower = BoundedNumber(min_value=50, max_value=2000)
    displacement = BoundedNumber(min_value=0.5, max_value=10.0)

    def __init__(self, horsepower, displacement):
        self.horsepower = horsepower
        self.displacement = displacement
