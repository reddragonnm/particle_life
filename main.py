import pygame as pg
import numpy as np

colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255))
attraction_table = np.random.random((len(colors), len(colors))) * 2 - 1

win_size = 800

pg.init()
screen = pg.display.set_mode((win_size, win_size))
clock = pg.time.Clock()


class Boundary:
    def __init__(self, center, half_dim):
        self.center = center
        self.half_dim = half_dim

    def contains_particle(self, particle):
        return (
            self.center[0] - self.half_dim
            < particle.pos[0]
            < self.center[0] + self.half_dim
            and self.center[1] - self.half_dim
            < particle.pos[1]
            < self.center[1] + self.half_dim
        )

    def intersects(self, other):
        self_min = self.center - self.half_dim
        self_max = self.center + self.half_dim

        other_min = other.center - other.half_dim
        other_max = other.center + other.half_dim

        return np.all(self_min < other_max) and np.all(self_max > other_min)


class QuadTree:
    def __init__(self, boundary):
        self.capacity = 4
        self.particles = []

        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None

        self.boundary = boundary

    def insert(self, particle):
        if not self.boundary.contains_particle(particle):
            return

        if len(self.particles) < self.capacity and self.nw is None:
            self.particles.append(particle)
            return

        if self.nw is None:
            self.subdivide()

        self.nw.insert(particle)
        self.ne.insert(particle)
        self.sw.insert(particle)
        self.se.insert(particle)

    def subdivide(self):
        center = self.boundary.center
        half_dim = self.boundary.half_dim

        self.nw = QuadTree(Boundary(center - half_dim / 2, half_dim / 2))
        self.se = QuadTree(Boundary(center + half_dim / 2, half_dim / 2))

        self.ne = QuadTree(
            Boundary(center + [half_dim / 2, -half_dim / 2], half_dim / 2)
        )
        self.sw = QuadTree(
            Boundary(center + [-half_dim / 2, half_dim / 2], half_dim / 2)
        )

        for p in self.particles:
            self.nw.insert(p)
            self.ne.insert(p)
            self.sw.insert(p)
            self.se.insert(p)
        self.particles.clear()

    def query(self, boundary):
        particles_in_range = []

        if not self.boundary.intersects(boundary):
            return particles_in_range

        for particle in self.particles:
            if boundary.contains_particle(particle):
                particles_in_range.append(particle)

        if self.nw is None:
            return particles_in_range

        particles_in_range.extend(self.nw.query(boundary))
        particles_in_range.extend(self.ne.query(boundary))
        particles_in_range.extend(self.sw.query(boundary))
        particles_in_range.extend(self.se.query(boundary))

        return particles_in_range

    def clear(self):
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None
        self.particles = []


quad = QuadTree(Boundary(np.array([win_size / 2, win_size / 2]), win_size / 2))


class Particle:
    def __init__(self, pos, vel, col):
        self.pos = pos
        self.vel = vel
        self.col = col

        self.size = 1
        self.r_max = self.size * 50

    def draw(self):
        pg.draw.circle(screen, colors[self.col], self.pos, self.size)

    def update_pos(self, dt):
        self.pos += self.vel * dt

        if self.pos[0] > win_size:
            self.pos[0] = win_size
            self.vel[0] *= -1
        elif self.pos[0] < 0:
            self.pos[0] = 0
            self.vel[0] *= -1

        if self.pos[1] > win_size:
            self.pos[1] = win_size
            self.vel[1] *= -1
        elif self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] *= -1

    def compute_acc(self, other):
        dist = np.linalg.norm(other.pos - self.pos) + self.size / 10
        direction = (other.pos - self.pos) * (1 / dist)

        close_thresh = self.size * 20

        attraction = 0
        attraction_factor = attraction_table[self.col][other.col]
        mp = (self.r_max + close_thresh) / 2

        if dist < close_thresh:
            attraction = (dist / close_thresh) - 1
        elif dist < mp:
            attraction = (attraction_factor / (mp - close_thresh)) * (
                dist - close_thresh
            )
        elif dist < mp * 2:
            attraction = attraction_factor - (
                (attraction_factor / (self.r_max - mp)) * (dist - mp)
            )

        return direction * attraction * 10

    def update_vel(self, dt):
        acc = np.array([0.0, 0.0])

        for p in quad.query(Boundary(self.pos, self.r_max)):
            if p is not self:
                acc += self.compute_acc(p)

        mu = 0.7
        self.vel = self.vel * mu + acc * dt


running = True
dt = 0.1

particles = []
i = 0


while running:
    screen.fill((0, 0, 0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            pos = np.array(pg.mouse.get_pos(), np.float64)

            r = 50
            col = i % 3
            i += 1

            for r in range(50, 0, -20):
                for angle in range(0, 360, 20):
                    p = Particle(
                        pos
                        + r
                        * np.array(
                            [
                                np.cos(angle * np.pi / 180),
                                np.sin(angle * np.pi / 180),
                            ]
                        ),
                        np.array([0.0, 0.0]),
                        col,
                    )

                    particles.append(p)

                    quad.insert(p)

    quad.clear()
    for p in particles:
        quad.insert(p)

    for particle in particles:
        particle.update_pos(dt)
        particle.update_vel(dt)
        particle.draw()

    clock.tick()
    pg.display.set_caption(f"FPS: {int(clock.get_fps())}")
    pg.display.update()

pg.quit()
