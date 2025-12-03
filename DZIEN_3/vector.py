from typing import Protocol

class VectorLike(Protocol):
    x:float
    y:float

class Point:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y

class Velocity:
    def __init__(self, vx:float, vy:float):
        self.x = vx
        self.y = vy

def length(v: VectorLike) -> float:
    return (v.x**2 + v.y**2) ** 0.5

print(length(Point(3,4)))
print(length(Velocity(5,12)))
