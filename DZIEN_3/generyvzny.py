from typing import Generic,Protocol,TypeVar


T = TypeVar('T')
class Repository(Protocol[T]):
    def add(self,item:T)->None:...
    def get_all(self) -> list[T]:...

class MemoryRepo(Generic[T]):
    def __init__(self):
        self._data:list[T] = []
    def add(self,item:T)->None:
        self._data.append(item)
    def get_all(self) -> list[T]:
        return self._data

def process(repo:Repository[int]):
    repo.add(11)
    repo.add(18)
    repo.add(22)
    return repo.get_all()
print(process(MemoryRepo[int]()))
