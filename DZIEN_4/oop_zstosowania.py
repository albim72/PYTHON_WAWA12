from __future__ import annotations
from typing import Iterable, Iterator, Any
import math


class VectorError(Exception):
    """Bazowy wyjątek dla operacji na wektorach."""


class VectorDimensionError(VectorError):
    """Błąd wymiaru wektora (np. operacje na niezgodnych wektorach)."""


class VectorTypeError(VectorError):
    """Błąd typu (np. nieprawidłowe argumenty do konstruktora)."""


class Vector2D(tuple):
    """
    Własny typ krotki reprezentujący wektor 2D.

    Dziedziczy po `tuple`, więc:
    - jest niemutowalny,
    - można go używać jako klucz w dict, element seta itd.
    """

    # Dzięki temu pattern matching zadziała jak: case Vector2D(x, y)
    __match_args__ = ("x", "y")

    __slots__ = ()

    def __new__(cls, x: float, y: float) -> "Vector2D":
        # Walidacja typów wejściowych
        if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
            raise VectorTypeError(
                f"Vector2D oczekuje liczb (int/float), otrzymano: x={type(x)}, y={type(y)}"
            )
        # Tworzymy prawdziwą krotkę (tuple.__new__)
        return super().__new__(cls, (float(x), float(y)))

    # Wygodne aliasy pól
    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    # EXTRA: klasa pomocnicza do tworzenia z iterowalnych danych
    @classmethod
    def from_iterable(cls, it: Iterable[Any]) -> "Vector2D":
        """
        Tworzy Vector2D z dowolnego iterowalnego o długości 2.
        Rzuca VectorTypeError przy złej długości.
        """
        seq = list(it)
        if len(seq) != 2:
            raise VectorDimensionError(
                f"Vector2D.from_iterable oczekuje dokładnie 2 elementów, otrzymano {len(seq)}"
            )
        return cls(seq[0], seq[1])

    # Wygodne metody wektorowe
    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vector2D":
        """Zwraca wektor znormalizowany (długość = 1)."""
        l = self.length()
        if l == 0:
            raise VectorError("Nie można znormalizować wektora zerowego.")
        return Vector2D(self.x / l, self.y / l)

    def dot(self, other: "Vector2D") -> float:
        """Iloczyn skalarny."""
        if not isinstance(other, Vector2D):
            raise VectorTypeError(f"Iloczyn skalarny z obiektem typu {type(other)} jest niedozwolony.")
        return self.x * other.x + self.y * other.y

    # Przeciążenie operatorów
    def __add__(self, other: "Vector2D") -> "Vector2D":
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        if not isinstance(other, Vector2D):
            return NotImplemented
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Vector2D":
        return self.__mul__(scalar)

    def __iter__(self) -> Iterator[float]:
        # zwracamy iterator jak zwykła krotka
        return super().__iter__()

    def __repr__(self) -> str:
        return f"Vector2D(x={self.x:.3f}, y={self.y:.3f})"


# --- Demo użycia ---

if __name__ == "__main__":
    v1 = Vector2D(3, 4)
    v2 = Vector2D.from_iterable([1, -2])

    print("v1:", v1, "len:", v1.length())
    print("v2:", v2)

    print("v1 + v2 =", v1 + v2)
    print("v1 - v2 =", v1 - v2)
    print("2 * v1 =", 2 * v1)
    print("dot(v1, v2) =", v1.dot(v2))

    # EXTRA: pattern matching
    match v1:
        case Vector2D(x, y) if x > 0 and y > 0:
            print(f"v1 leży w I ćwiartce: x={x}, y={y}")
        case Vector2D(_, _):
            print("v1 jest poprawnym wektorem, ale nie w I ćwiartce.")

    # EXTRA: obsługa własnych błędów
    try:
        bad = Vector2D("abc", 10)
    except VectorTypeError as e:
        print("Złapany błąd typu wektora:", e)

    try:
        wrong = Vector2D.from_iterable([1, 2, 3])
    except VectorDimensionError as e:
        print("Złapany błąd wymiaru:", e)
