
Advanced Decorators Package
===========================

Ten pakiet zawiera plik `advanced_decorators.py` z implementacją 4
zaawansowanych dekoratorów do Pythona:

1) @logged     – logowanie wywołań (sync + async)
2) @retry      – ponawianie operacji z backoffem
3) @ensure     – prosty "design by contract"
4) @ttl_cache  – cache z czasem życia (TTL) i LRU

Jak używać:
-----------

from advanced_decorators import logged, retry, ensure, ttl_cache

Szczegółowe komentarze i przykłady użycia są w samym pliku .py.
