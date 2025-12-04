from __future__ import annotations
from typing import Callable, Iterable, List, Any
from functools import wraps
import math


# ==============================
# 1. Funkcyjny "infrastrukturalny" kawałek
# ==============================

def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Funkcyjna kompozycja: compose(f, g, h)(x) == f(g(h(x))).
    """
    def inner(x: Any) -> Any:
        for f in reversed(funcs):
            x = f(x)
        return x
    return inner


# Dekorator do oznaczania kroków w pipeline
def pipeline_step(func: Callable) -> Callable:
    """
    Dekorator oznaczający metodę/funkcję jako krok pipeline.

    Metaklasa będzie szukać atrybutu __is_step__ == True.
    """
    func.__is_step__ = True  # type: ignore[attr-defined]

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__is_step__ = True  # przenosimy flagę na wrapper
    return wrapper


# ==============================
# 2. Prosta hierarchia wyjątków
# ==============================

class SignalError(Exception):
    """Bazowy wyjątek dla operacji na sygnale."""


class EmptySignalError(SignalError):
    """Rzucany, gdy próbujemy liczyć statystyki na pustym sygnale."""


# ==============================
# 3. Klasa domenowa: Signal (OOP + property)
# ==============================

class Signal:
    """
    Reprezentacja sygnału 1D (lista floatów).
    Zawiera property do statystyk, które liczone są leniwie.
    """

    def __init__(self, samples: Iterable[float]):
        self._samples: List[float] = list(float(x) for x in samples)
        if not self._samples:
            raise EmptySignalError("Sygnał nie może być pusty.")

        self._mean: float | None = None
        self._std: float | None = None

    @property
    def samples(self) -> List[float]:
        """Dostęp do próbek sygnału (niemutowalna kopia do świata zewnętrznego)."""
        # jeśli chcesz twardą niemutowalność – zwróć tuple(self._samples)
        return list(self._samples)

    @property
    def mean(self) -> float:
        """Średnia sygnału – liczona leniwie i cachowana."""
        if self._mean is None:
            self._mean = sum(self._samples) / len(self._samples)
        return self._mean

    @property
    def std(self) -> float:
        """Odchylenie standardowe sygnału (populacyjne)."""
        if self._std is None:
            m = self.mean
            var = sum((x - m) ** 2 for x in self._samples) / len(self._samples)
            self._std = math.sqrt(var)
        return self._std

    @property
    def quality(self) -> str:
        """
        Prosta kategoryzacja jakości sygnału na podstawie std.
        EXTRA: użyjemy tego później przy pattern matchingu.
        """
        if self.std < 0.1:
            return "flat"
        elif self.std < 1.0:
            return "stable"
        else:
            return "noisy"

    def __repr__(self) -> str:
        return f"Signal(n={len(self._samples)}, mean={self.mean:.3f}, std={self.std:.3f})"


# ==============================
# 4. Metaklasa do automatycznego zbierania kroków pipeline
# ==============================

class PipelineMeta(type):
    """
    Metaklasa, która:
    - w momencie tworzenia klasy,
    - zbiera wszystkie metody oznaczone @pipeline_step,
    - zapamiętuje ich kolejność w atrybucie __steps__.

    Dzięki temu każda klasa pipeline ma deklaratywną definicję kroków.
    """

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, dict(namespace))

        steps: list[str] = []

        # Zbieramy kroki z klas bazowych (dziedziczenie pipeline'u)
        for base in bases:
            if hasattr(base, "__steps__"):
                steps.extend(getattr(base, "__steps__"))

        # Dodajemy kroki z tej klasy
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and getattr(attr_value, "__is_step__", False):
                steps.append(attr_name)

        cls.__steps__ = steps  # type: ignore[attr-defined]
        return cls


# ==============================
# 5. Pipeline sygnału – OOP + funkcje + meta + property + EXTRA
# ==============================

class SignalPipeline(metaclass=PipelineMeta):
    """
    Pipeline przetwarzania sygnału:
    - ma listę kroków zebranych przez metaklasę,
    - udostępnia metodę run/process,
    - można go wywołać jak funkcję (__call__),
    - każdy krok to metoda oznaczona @pipeline_step,
      która przyjmuje i zwraca obiekt Signal.
    """

    def __init__(self, name: str = "default"):
        self.name = name

    @property
    def steps(self) -> List[str]:
        """Nazwy kroków pipeline'u, w kolejności wykonania."""
        return list(self.__steps__)  # type: ignore[attr-defined]

    def run(self, signal: Signal) -> Signal:
        """
        Uruchamia pipeline na podanym sygnale.
        """
        current = signal
        print(f"[Pipeline {self.name}] starting with:", current)

        for step_name in self.__steps__:  # type: ignore[attr-defined]
            step = getattr(self, step_name)
            print(f"[Pipeline {self.name}] -> step: {step_name}")
            current = step(current)
            print(f"[Pipeline {self.name}]    result:", current)

        print(f"[Pipeline {self.name}] finished.")
        return current

    def __call__(self, signal: Signal) -> Signal:
        """Dzięki temu pipeline działa jak funkcja."""
        return self.run(signal)

    # --- KROKI PIPELINE'U (OOP + funkcyjnie w środku) ---

    @pipeline_step
    def center(self, signal: Signal) -> Signal:
        """
        Odejmuje średnią od sygnału (centracja).
        To jest czysta operacja funkcjonalna: bierze Signal -> zwraca nowy Signal.
        """
        centered = [x - signal.mean for x in signal.samples]
        return Signal(centered)

    @pipeline_step
    def limit_amplitude(self, signal: Signal) -> Signal:
        """
        Ogranicza amplitudę do [-3, 3] (hard clipping).
        """
        limited = [max(-3.0, min(3.0, x)) for x in signal.samples]
        return Signal(limited)

    @pipeline_step
    def smooth(self, signal: Signal) -> Signal:
        """
        Proste wygładzanie: średnia z okna 3-próbkowego.
        """
        xs = signal.samples
        if len(xs) < 3:
            return signal  # za mało próbek, zostawiamy

        smoothed = []
        for i in range(len(xs)):
            left = xs[i - 1] if i > 0 else xs[i]
            right = xs[i + 1] if i < len(xs) - 1 else xs[i]
            smoothed.append((left + xs[i] + right) / 3.0)
        return Signal(smoothed)

    @pipeline_step
    def classify_quality(self, signal: Signal) -> Signal:
        """
        EXTRA: krok, który nic nie zmienia w danych,
        ale używa property `quality` do logicznej klasyfikacji sygnału.
        """
        match signal.quality:
            case "flat":
                print("   [quality] sygnał jest prawie płaski (flat)")
            case "stable":
                print("   [quality] sygnał jest stabilny")
            case "noisy":
                print("   [quality] sygnał jest hałaśliwy")
            case _:
                print("   [quality] nieznana jakość sygnału")
        return signal


# ==============================
# 6. Demo: OOP + funkcyjnie + meta + property + EXTRA
# ==============================

if __name__ == "__main__":
    import random

    # Tworzymy syntetyczny sygnał: sinusoida + szum
    xs = []
    for i in range(100):
        base = math.sin(i / 10)
        noise = random.uniform(-0.5, 0.5)
        xs.append(base + noise)

    sig = Signal(xs)

    pipeline = SignalPipeline(name="basic")
    print("Kroki pipeline:", pipeline.steps)

    # Możemy zbudować funkcję czysto funkcyjną na bazie metod pipeline'u:
    # (extra: kompozycja funkcji)
    functional_version = compose(
        pipeline.classify_quality,
        pipeline.smooth,
        pipeline.limit_amplitude,
        pipeline.center,
    )

    print("\n=== OOP styl (pipeline(sig)) ===")
    result1 = pipeline(sig)

    print("\n=== Funkcyjny styl (compose(...)(sig)) ===")
    result2 = functional_version(sig)

    print("\nPorównanie wyników:")
    print("result1:", result1)
    print("result2:", result2)
