
"""
advanced_decorators.py
----------------------

Zestaw 4 zaawansowanych dekoratorów do Pythona, które możesz pokazać
na szkoleniu lub wykorzystać produkcyjnie.

Dekoratory:
1) @logged       – zaawansowane logowanie z czasem wykonania i obsługą wyjątków
2) @retry        – ponawianie operacji z backoffem (sync + async)
3) @ensure       – prosta implementacja "design by contract"
4) @ttl_cache    – cache z czasem życia wpisów (TTL)

Kod jest w pełni samodzielny, bez zewnętrznych zależności.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import logging
import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable, Iterable, Mapping, Type, TypeVar, ParamSpec, Concatenate, Optional

P = ParamSpec("P")
R = TypeVar("R")


# ================================================================
# 1) @logged – dekorator logujący wywołania funkcji (sync + async)
# ================================================================

def logged(
    *,
    level: int = logging.INFO,
    logger: logging.Logger | None = None,
    log_args: bool = True,
    log_result: bool = True,
    log_exceptions: bool = True,
    log_execution_time: bool = True,
    slow_threshold: float | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Zaawansowany dekorator logujący przebieg funkcji.

    Funkcjonalności:
    - działa zarówno dla funkcji synchronicznych, jak i asynchronicznych
    - loguje argumenty, wynik oraz wyjątki
    - mierzy czas wykonania i (opcjonalnie) ostrzega o "wolnych" wywołaniach
    - używa functools.wraps do zachowania metadanych funkcji

    Parametry:
    - level            – poziom logowania (np. logging.INFO, logging.DEBUG)
    - logger           – obiekt loggera; jeśli None, używa modułowego loggera
    - log_args         – czy logować argumenty wejściowe
    - log_result       – czy logować wartość zwracaną
    - log_exceptions   – czy logować wyjątki
    - log_execution_time – czy logować czas wykonania
    - slow_threshold   – jeśli podane, loguje ostrzeżenie, gdy czas > threshold
    """

    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        is_coroutine = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            bound = inspect.signature(func).bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if log_args:
                logger.log(level, "Calling async %s(%s)", func.__qualname__, bound.arguments)

            try:
                result = await func(*args, **kwargs)
            except Exception:
                if log_exceptions:
                    logger.exception("Exception in async %s", func.__qualname__)
                raise
            else:
                duration = time.perf_counter() - start
                if log_execution_time:
                    logger.log(level, "Async %s completed in %.4fs", func.__qualname__, duration)
                if slow_threshold is not None and duration > slow_threshold:
                    logger.warning("Async %s is slow: %.4fs > %.4fs", func.__qualname__, duration, slow_threshold)
                if log_result:
                    logger.log(level, "Async %s returned %r", func.__qualname__, result)
                return result

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()
            bound = inspect.signature(func).bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if log_args:
                logger.log(level, "Calling %s(%s)", func.__qualname__, bound.arguments)

            try:
                result = func(*args, **kwargs)
            except Exception:
                if log_exceptions:
                    logger.exception("Exception in %s", func.__qualname__)
                raise
            else:
                duration = time.perf_counter() - start
                if log_execution_time:
                    logger.log(level, "%s completed in %.4fs", func.__qualname__, duration)
                if slow_threshold is not None and duration > slow_threshold:
                    logger.warning("%s is slow: %.4fs > %.4fs", func.__qualname__, duration, slow_threshold)
                if log_result:
                    logger.log(level, "%s returned %r", func.__qualname__, result)
                return result

        return async_wrapper if is_coroutine else sync_wrapper  # type: ignore[return-value]

    return decorator


# ==========================================================
# 2) @retry – ponawianie operacji z backoffem (sync + async)
# ==========================================================

def retry(
    exceptions: Iterable[Type[BaseException]] = (Exception,),
    *,
    attempts: int = 3,
    delay: float = 0.1,
    backoff: float = 2.0,
    max_delay: float | None = None,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Dekorator ponawiający wywołanie funkcji w razie wystąpienia błędów.

    Funkcjonalności:
    - obsługa funkcji sync i async
    - eksponencjalny backoff
    - limit prób i (opcjonalnie) maksymalnego opóźnienia
    - logowanie kolejnych prób i ostatniego wyjątku

    Parametry:
    - exceptions – krotka/iterable typów wyjątków, które mają być retry'owane
    - attempts   – maksymalna liczba prób
    - delay      – pierwsze opóźnienie (w sekundach)
    - backoff    – współczynnik mnożenia opóźnienia (np. 2.0 → 0.1, 0.2, 0.4, 0.8, ...)
    - max_delay  – górne ograniczenie opóźnienia, jeśli ustawione
    - logger     – opcjonalny logger
    """

    exc_tuple = tuple(exceptions)
    if logger is None:
        logger = logging.getLogger(__name__)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        is_coroutine = asyncio.iscoroutinefunction(func)

        async def _async_call(*args: P.args, **kwargs: P.kwargs) -> R:
            current_delay = delay
            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exc_tuple as e:  # type: ignore[misc]
                    if attempt == attempts:
                        logger.error(
                            "Async %s failed after %d attempts – raising.",
                            func.__qualname__,
                            attempts,
                        )
                        raise
                    logger.warning(
                        "Async %s attempt %d/%d failed with %r. Retrying in %.3fs...",
                        func.__qualname__,
                        attempt,
                        attempts,
                        e,
                        current_delay,
                    )
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    if max_delay is not None:
                        current_delay = min(current_delay, max_delay)
            # Formalnie unreachable:
            raise RuntimeError("retry: internal async logic error")

        def _sync_call(*args: P.args, **kwargs: P.kwargs) -> R:
            current_delay = delay
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exc_tuple as e:  # type: ignore[misc]
                    if attempt == attempts:
                        logger.error(
                            "%s failed after %d attempts – raising.",
                            func.__qualname__,
                            attempts,
                        )
                        raise
                    logger.warning(
                        "%s attempt %d/%d failed with %r. Retrying in %.3fs...",
                        func.__qualname__,
                        attempt,
                        attempts,
                        e,
                        current_delay,
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    if max_delay is not None:
                        current_delay = min(current_delay, max_delay)
            raise RuntimeError("retry: internal sync logic error")

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return await _async_call(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return _sync_call(*args, **kwargs)

        return async_wrapper if is_coroutine else sync_wrapper  # type: ignore[return-value]

    return decorator


# =======================================================
# 3) @ensure – prosty "design by contract" dla funkcji
# =======================================================

def ensure(
    *,
    pre: Callable[Concatenate[P], bool] | None = None,
    post: Callable[Concatenate[R, P], bool] | None = None,
    pre_message: str = "Precondition failed",
    post_message: str = "Postcondition failed",
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Dekorator realizujący prosty "design by contract":

    - precondition (pre) – warunek na argumenty wejściowe
    - postcondition (post) – warunek na wynik i argumenty

    Jeśli warunek nie jest spełniony, rzucany jest AssertionError.
    Dzięki temu możesz formalizować oczekiwania wobec funkcji.

    Przykład:
        @ensure(
            pre=lambda x, y: x >= 0 and y >= 0,
            post=lambda result, x, y: result >= x and result >= y
        )
        def max_plus_one(x, y):
            return max(x, y) + 1
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        is_coroutine = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if pre is not None and not pre(*args, **kwargs):
                raise AssertionError(pre_message)
            result = await func(*args, **kwargs)
            if post is not None and not post(result, *args, **kwargs):
                raise AssertionError(post_message)
            return result

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if pre is not None and not pre(*args, **kwargs):
                raise AssertionError(pre_message)
            result = func(*args, **kwargs)
            if post is not None and not post(result, *args, **kwargs):
                raise AssertionError(post_message)
            return result

        return async_wrapper if is_coroutine else sync_wrapper  # type: ignore[return-value]

    return decorator


# ===========================================================
# 4) @ttl_cache – cache z czasem życia wpisów (TTL) + LRU
# ===========================================================

def ttl_cache(
    *,
    ttl: float,
    maxsize: int = 128,
    typed: bool = False,
    time_fn: Callable[[], float] = time.monotonic,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Dekorator cache'ujący wyniki funkcji z czasem życia (TTL).

    Funkcjonalności:
    - TTL (time-to-live): wynik jest ważny tylko przez podany czas
    - mechanizm LRU: ograniczenie liczby wpisów w cache
    - obsługa różnych typów argumentów (podobnie jak w functools.lru_cache)
    - prosty, ale czytelny kod – można pokazać na szkoleniu jako przykład
      zaawansowanego dekoratora opartego o closure i OrderedDict.

    Parametry:
    - ttl      – czas życia wpisu w sekundach
    - maxsize  – maksymalna liczba wpisów w cache
    - typed    – jeśli True, różnicuje cache po typach argumentów
    - time_fn  – funkcja zwracająca aktualny czas (dla testowalności)
    """

    def make_key(args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> tuple[Any, ...]:
        """
        Tworzy klucz cache zgodny z logiką:
        - argumenty pozycyjne + nazwane
        - opcjonalne rozróżnienie typów (typed=True)
        """
        key_parts: list[Any] = list(args)
        if kwargs:
            # sortujemy po nazwach, aby kolejność w wywołaniu nie miała znaczenia
            for k, v in sorted(kwargs.items()):
                key_parts.append((k, v))
        if typed:
            key_parts.extend(type(a) for a in args)
            key_parts.extend(type(v) for _, v in sorted(kwargs.items()))
        return tuple(key_parts)

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        cache: "OrderedDict[tuple[Any, ...], tuple[float, R]]" = OrderedDict()

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal cache
            now = time_fn()
            key = make_key(args, kwargs)

            # Sprzątanie starych wpisów "przy okazji"
            to_delete: list[tuple[Any, ...]] = []
            for k, (t_inserted, _) in cache.items():
                if now - t_inserted > ttl:
                    to_delete.append(k)
                else:
                    # OrderedDict – jeśli napotkamy świeży wpis,
                    # kolejne są jeszcze młodsze -> można przerwać.
                    break
            for k in to_delete:
                cache.pop(k, None)

            if key in cache:
                # Przeniesienie na koniec – implementacja LRU
                t_inserted, value = cache.pop(key)
                cache[key] = (t_inserted, value)
                return value

            # Brak w cache – obliczamy
            result = func(*args, **kwargs)
            cache[key] = (now, result)

            # Jeśli przekroczyliśmy maxsize – usuwamy najstarszy wpis
            if len(cache) > maxsize:
                cache.popitem(last=False)

            return result

        # Dodajemy metody pomocnicze do wrappera – to dobry "zaawansowany" pattern
        def cache_clear() -> None:
            """Czyści cały cache."""
            cache.clear()

        def cache_info() -> dict[str, Any]:
            """Zwraca podstawowe dane o stanie cache."""
            return {
                "size": len(cache),
                "maxsize": maxsize,
                "ttl": ttl,
                "items": list(cache.keys()),
            }

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_info = cache_info    # type: ignore[attr-defined]

        return wrapper

    return decorator


# ===========================================================
# DEMO – przykładowe użycie (może być pokazane na szkoleniu)
# ===========================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    @logged(level=logging.DEBUG, slow_threshold=0.2)
    def demo_logged(x: int, y: int) -> int:
        time.sleep(0.1)
        return x + y

    @retry(attempts=3, delay=0.1, backoff=2.0)
    def demo_retry(should_fail_times: int, _state={"counter": 0}) -> str:  # type: ignore[misc]
        _state["counter"] += 1
        if _state["counter"] <= should_fail_times:
            raise RuntimeError("Temporary failure")
        return "OK"

    @ensure(
        pre=lambda x: x >= 0,
        post=lambda result, x: result >= x,
    )
    def demo_ensure(x: int) -> int:
        return x + 1

    @ttl_cache(ttl=1.0, maxsize=4)
    def demo_ttl(x: int) -> int:
        print(f"Computing demo_ttl({x})")
        return x * x

    print("demo_logged:", demo_logged(2, 3))

    print("demo_retry:", demo_retry(should_fail_times=2))

    print("demo_ensure:", demo_ensure(10))

    print("First call ttl:", demo_ttl(5))
    print("Second call ttl (cached):", demo_ttl(5))
    time.sleep(1.1)
    print("Third call ttl (expired):", demo_ttl(5))
