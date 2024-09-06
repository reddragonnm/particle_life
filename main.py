import pygame as pg
from math import sqrt
from random import choice, uniform


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def __rmul__(self, other):
        return Vector(self.x * other, self.y * other)

    def get_tuple(self):
        return self.x, self.y

    def get_mag(self):
        return sqrt(self.x**2 + self.y**2)

    def get_normalised(self):
        return self * (1 / self.get_mag())


class Particle:
    def __init__(self, pos, vel, col):
        self.pos = pos
        self.vel = vel
        self.col = col

        self.old_acc = Vector(0, 0)
        self.acc = Vector(0, 0)

        self.size = 5
        self.r_max = 100

    def draw(self, screen):
        pg.draw.circle(screen, self.col, self.pos.get_tuple(), self.size)

    def update_pos(self, dt, screen_size):
        self.pos += self.vel * dt + 0.5 * self.acc * dt * dt

        if self.pos.x > screen_size:
            self.pos.x = 0
        elif self.pos.x < 0:
            self.pos.x = screen_size

        if self.pos.y > screen_size:
            self.pos.y = 0
        elif self.pos.y < 0:
            self.pos.y = screen_size

    def compute_acc(self, other):
        dist = (other.pos - self.pos).get_mag()
        direction = (other.pos - self.pos).get_normalised()

        close_thresh = self.size * 3

        attraction = 0
        if dist < close_thresh:
            attraction = (1 / close_thresh) * dist + (-1)
        elif dist < (self.r_max + close_thresh) / 2:
            pass

        return direction * attraction

    def update_acc(self, particles):
        self.old_acc = self.acc
        self.acc = Vector(0, 0)

        for p in particles:
            if p is not self:
                self.acc += self.compute_acc(p)

        self.vel += (self.old_acc + self.acc) * 0.5 * dt


if __name__ == "__main__":
    win_size = 800

    pg.init()
    screen = pg.display.set_mode((win_size, win_size))
    clock = pg.time.Clock()

    running = True
    dt = 0.1

    particles = []
    colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255))

    while running:
        screen.fill((0, 0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                particles.append(
                    Particle(
                        Vector(*pos),
                        Vector(uniform(-1, 1), uniform(-1, 1)),
                        choice(colors),
                    )
                )

        for particle in particles:
            particle.update_pos(dt, win_size)

        for particle in particles:
            particle.update_acc(particles)
            particle.draw(screen)

        clock.tick()
        dt = 100 / clock.get_fps() if clock.get_fps() != 0 else dt

        pg.display.update()

    pg.quit()
