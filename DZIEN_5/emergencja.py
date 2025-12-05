import random
import math
from dataclasses import dataclass
from typing import List

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

WIDTH = 80
HEIGHT = 40

@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x - other.x, self.y - other.y)

    def __truediv__(self, k: float) -> "Vec2":
        return Vec2(self.x / k, self.y / k)

    def __mul__(self, k: float) -> "Vec2":
        return Vec2(self.x * k, self.y * k)

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def normalized(self) -> "Vec2":
        l = self.length()
        if l == 0:
            return Vec2(0, 0)
        return self / l


@dataclass
class Boid:
    pos: Vec2
    vel: Vec2


def random_boid() -> Boid:
    return Boid(
        pos=Vec2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT)),
        vel=Vec2(random.uniform(-1, 1), random.uniform(-1, 1)),
    )


def limit_speed(v: Vec2, max_speed: float) -> Vec2:
    if v.length() > max_speed:
        return v.normalized() * max_speed
    return v


def step_boids(boids: List[Boid],
               neighbor_radius: float = 8.0,
               sep_strength: float = 0.05,
               align_strength: float = 0.05,
               coh_strength: float = 0.01,
               max_speed: float = 1.5) -> None:
    new_vels: List[Vec2] = []

    for i, b in enumerate(boids):
        neighbours = []
        for j, other in enumerate(boids):
            if i == j:
                continue
            if (other.pos - b.pos).length() < neighbor_radius:
                neighbours.append(other)

        if not neighbours:
            new_vels.append(b.vel)
            continue

        # separation
        sep_force = Vec2(0, 0)
        for n in neighbours:
            diff = b.pos - n.pos
            dist = diff.length()
            if dist > 0 and dist < neighbor_radius / 2:
                sep_force = sep_force + diff.normalized() / dist

        # alignment
        avg_vel = Vec2(0, 0)
        for n in neighbours:
            avg_vel = avg_vel + n.vel
        avg_vel = avg_vel / len(neighbours)
        align_force = (avg_vel - b.vel)

        # cohesion
        center = Vec2(0, 0)
        for n in neighbours:
            center = center + n.pos
        center = center / len(neighbours)
        coh_force = (center - b.pos)

        dv = (sep_force * sep_strength +
              align_force * align_strength +
              coh_force * coh_strength)

        new_v = b.vel + dv
        new_v = limit_speed(new_v, max_speed)
        new_vels.append(new_v)

    for b, v in zip(boids, new_vels):
        b.vel = v
        b.pos = Vec2(
            (b.pos.x + b.vel.x) % WIDTH,
            (b.pos.y + b.vel.y) % HEIGHT
        )


def run_animation(n_boids: int = 40, steps: int = 1000):
    boids = [random_boid() for _ in range(n_boids)]

    fig, ax = plt.subplots()
    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_aspect("equal")
    ax.set_title("Emergentne stado (boids) – lokalne reguły, globalny porządek")

    xs = [b.pos.x for b in boids]
    ys = [b.pos.y for b in boids]
    scatter = ax.scatter(xs, ys)

    def update(frame):
        step_boids(boids)
        xs = [b.pos.x for b in boids]
        ys = [b.pos.y for b in boids]
        scatter.set_offsets(list(zip(xs, ys)))
        return scatter,

    anim = FuncAnimation(fig, update, frames=steps, interval=40, blit=True)
    plt.show()


if __name__ == "__main__":
    run_animation()
