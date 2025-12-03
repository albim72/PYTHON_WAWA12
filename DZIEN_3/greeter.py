from typing import Protocol

class Greeter(Protocol):
    def greet(self, name: str) -> str: ...

class Person:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"

class AI:
    def greet(self, name: str) -> str:
        return "I don't know!"

def welcome(entity:Greeter, name: str) -> str:
    return entity.greet(name)

print(welcome(Person(), "Alice"))
print(welcome(AI(), "Bob"))
