
"""Demo and tests for advanced_properties.py

This script imports the four examples:
- Account
- LazyModel
- ObservableValue
- Engine (with BoundedNumber descriptor)

and runs small illustrative tests for each, printing results to stdout.
"""

from __future__ import annotations

import time
from decimal import Decimal

from advanced_properties import Account, LazyModel, ObservableValue, Engine


def test_account() -> None:
    print("\n=== Test: Account (property as domain layer) ===")
    acc = Account(balance_cents=1500)  # 15.00
    print("Initial balance:", acc.balance, "is_empty:", acc.is_empty)

    acc.deposit(Decimal("25.50"))
    print("After deposit 25.50:", acc.balance)

    acc.withdraw(10)
    print("After withdraw 10:", acc.balance)

    print("Trying to set negative balance (should raise)...")
    try:
        acc.balance = -5
    except ValueError as e:
        print("Caught expected ValueError:", e)


def test_lazy_model() -> None:
    print("\n=== Test: LazyModel (lazy property with cache + invalidate) ===")

    def loader():
        print("loader() called – simulating expensive operation...")
        time.sleep(0.1)
        return {"items": [1, 2, 3]}

    model = LazyModel(loader)

    print("First access to data (should call loader):")
    d1 = model.data
    print("data:", d1, "loaded_at:", model.loaded_at)

    print("Second access to data (should use cache, no loader call):")
    d2 = model.data
    print("data:", d2, "loaded_at:", model.loaded_at)

    print("Invalidating cache and reading again (loader called again):")
    model.invalidate()
    d3 = model.data
    print("data:", d3, "loaded_at:", model.loaded_at)


def test_observable_value() -> None:
    print("\n=== Test: ObservableValue (property triggering events) ===")

    obs = ObservableValue[int](0)

    def logger(old, new):
        print(f"[logger] {old} -> {new}")

    def alert_if_big(old, new):
        if new >= 10:
            print(f"[alert] value reached {new} (>= 10)")

    obs.subscribe(logger)
    obs.subscribe(alert_if_big)

    print("Setting value to 5:")
    obs.value = 5

    print("Setting value to 12:")
    obs.value = 12

    print("Setting value to 12 again (no change, no callbacks expected):")
    obs.value = 12


def test_engine() -> None:
    print("\n=== Test: Engine (BoundedNumber descriptor / property++) ===")

    engine = Engine(horsepower=150, displacement=2.0)
    print("Initial engine:", "hp=", engine.horsepower, "L=", engine.displacement)

    print("Setting horsepower to 500 (valid):")
    engine.horsepower = 500
    print("hp=", engine.horsepower)

    print("Trying to set displacement to 'abc' (should raise TypeError):")
    try:
        engine.displacement = "abc"  # type: ignore[assignment]
    except TypeError as e:
        print("Caught expected TypeError:", e)

    print("Trying to set horsepower to 10 (below min, should raise ValueError):")
    try:
        engine.horsepower = 10
    except ValueError as e:
        print("Caught expected ValueError:", e)


def main() -> None:
    test_account()
    test_lazy_model()
    test_observable_value()
    test_engine()


if __name__ == "__main__":
    main()
