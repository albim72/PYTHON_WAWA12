from __future__ import annotations
from typing import Any, List, Tuple
import datetime as dt


class HistoryMeta(type):
    """Metaklasa, która wstrzykuje:
       - __setattr__ z logowaniem zmian
       - history() – zwraca listę zmian
       - rewind(step) – cofa obiekt do wybranego kroku
    """

    def __new__(mcls, name, bases, namespace):
        # Oryginalne __setattr__, jeśli istnieje
        orig_setattr = namespace.get("__setattr__", None)

        def __setattr__(self, key: str, value: Any):
            # Inicjalizacja historii przy pierwszym użyciu
            if not hasattr(self, "_history"):
                super(cls, self).__setattr__("_history", [])  # pomijamy __setattr__ z metaklasy

            timestamp = dt.datetime.now().isoformat(timespec="seconds")
            # Zapisujemy: (czas, nazwa pola, stara wartość, nowa wartość)
            old_value = getattr(self, key, None)
            self._history.append((timestamp, key, old_value, value))

            # delegacja do oryginalnego __setattr__ (jeśli było) lub domyślnego
            if orig_setattr and key not in ("_history",):
                orig_setattr(self, key, value)
            else:
                super(cls, self).__setattr__(key, value)

        def history(self) -> List[Tuple[str, str, Any, Any]]:
            """Zwraca listę zmian: (timestamp, field, old, new)."""
            return list(getattr(self, "_history", []))

        def rewind(self, step: int) -> None:
            """Cofa obiekt do stanu zadanego kroku (indeks w historii)."""
            if not hasattr(self, "_history"):
                return
            if step < 0 or step >= len(self._history):
                raise IndexError("Invalid history step")

            # Odtwarzamy obiekt od zera
            # 1. Zapisujemy aktualną historię
            changes = list(self._history)
            # 2. Czyścimy stan obiektu (poza historią)
            for key in list(self.__dict__.keys()):
                if key != "_history":
                    delattr(self, key)
            # 3. Odtwarzamy zmiany do danego kroku włącznie
            super(cls, self).__setattr__("_history", [])
            for ts, key, old, new in changes[: step + 1]:
                super(cls, self).__setattr__(key, new)
                self._history.append((ts, key, old, new))

        namespace["__setattr__"] = __setattr__
        namespace["history"] = history
        namespace["rewind"] = rewind

        cls = super().__new__(mcls, name, bases, namespace)
        return cls


# === Przykładowa klasa korzystająca z magii HistoryMeta ===

class Player(metaclass=HistoryMeta):
    def __init__(self, name: str):
        self.name = name
        self.hp = 100
        self.x = 0
        self.y = 0


if __name__ == "__main__":
    p = Player("Marcin")
    p.hp -= 10          # dostaje obrażenia
    p.x = 5
    p.y = 7
    p.hp += 20          # leczy się

    print("Aktualny stan:", vars(p))
    print("\nHistoria zmian:")
    for i, entry in enumerate(p.history()):
        print(i, entry)

    print("\nRewind do kroku 1 (tuż po pierwszej zmianie hp):")
    p.rewind(1)
    print("Stan po rewind:", vars(p))
