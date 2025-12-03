from typing import Protocol, runtime_checkable, TextIO


@runtime_checkable
class Readable(Protocol):
    def read(self, size: int = -1) -> str:
        ...


@runtime_checkable
class Writable(Protocol):
    def write(self, data: str) -> int:
        ...
    def flush(self) -> None:
        ...


@runtime_checkable
class FileLike(Readable, Writable, Protocol):
    """Strukturalny interfejs pliku tekstowego."""

    def close(self) -> None:
        ...


def copy_file(src: Readable, dst: Writable, chunk_size: int = 4096) -> int:
    """
    Kopiuje dane z obiektu 'src' do 'dst' w kawałkach.
    Nie zakłada, że to są prawdziwe pliki – ważne jest tylko API (Protocol).
    """
    total = 0
    while True:
        chunk = src.read(chunk_size)
        if not chunk:
            break
        total += dst.write(chunk)
    dst.flush()
    return total


# ======= PRZYKŁADOWE IMPLEMENTACJE =======

class InMemoryFile:
    """Prosty 'plik' w pamięci, zgodny z FileLike."""

    def __init__(self, initial: str = ""):
        self._buffer = initial
        self._pos = 0

    # Readable
    def read(self, size: int = -1) -> str:
        if size < 0:
            result = self._buffer[self._pos:]
            self._pos = len(self._buffer)
            return result
        else:
            end = self._pos + size
            result = self._buffer[self._pos:end]
            self._pos = end
            return result

    # Writable
    def write(self, data: str) -> int:
        # dopisujemy na koniec
        self._buffer += data
        return len(data)

    def flush(self) -> None:
        pass  # tu nic nie trzeba robić

    # FileLike
    def close(self) -> None:
        pass

    def get_value(self) -> str:
        return self._buffer


class LoggingWriter:
    """
    Dekorator, który opakowuje Writable i loguje co jest zapisywane.
    Pokazuje, że Protocol może opisać również warstwy pośrednie.
    """

    def __init__(self, inner: Writable):
        self._inner = inner

    def write(self, data: str) -> int:
        print(f"[LOG] zapisuję {len(data)} bajtów")
        return self._inner.write(data)

    def flush(self) -> None:
        self._inner.flush()


# ======= DEMO =======

if __name__ == "__main__":
    # 1) Kopiowanie między prawdziwymi plikami
    with open("input.txt", "w", encoding="utf-8") as f:
        f.write("To jest test protokołów i obsługi plików.\nDruga linia.\n")

    with open("input.txt", "r", encoding="utf-8") as src, \
         open("output.txt", "w", encoding="utf-8") as real_dst:

        # Owijamy realny plik loggerem, który też spełnia Writable
        dst = LoggingWriter(real_dst)

        print("isinstance(src, FileLike):", isinstance(src, FileLike))
        print("isinstance(dst, Writable):", isinstance(dst, Writable))

        bytes_written = copy_file(src, dst)
        print("Skopiowano znaków:", bytes_written)

    # 2) Kopiowanie z pliku do 'pliku' w pamięci
    with open("input.txt", "r", encoding="utf-8") as src2:
        mem_file = InMemoryFile()
        copy_file(src2, mem_file)
        print("\nZawartość InMemoryFile:")
        print(mem_file.get_value())
