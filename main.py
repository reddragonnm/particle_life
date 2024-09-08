import pygame as pg
import numpy as np

colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255))
attraction_table = np.random.random((len(colors), len(colors))) * 2 - 1

win_size = 800

pg.init()
screen = pg.display.set_mode((win_size, win_size))

show_debug = False


class Particle:
    def __init__(self, pos, vel, col):
        self.pos = pos
        self.vel = vel
        self.col = col

        self.size = 2
        self.r_max = self.size * 50

    def draw(self):
        if show_debug:
            pg.draw.circle(screen, (0, 0, 0, 0), self.pos, self.r_max, 2)

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

        close_thresh = self.size * 15

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

        if show_debug and dist < mp * 2:
            c = 255 * abs(attraction_factor)
            pg.draw.line(screen, (c, c, c), self.pos, other.pos, 1)

        return direction * attraction * 10

    def update_vel(self, particles, dt):
        acc = np.array([0.0, 0.0])

        for p in particles:
            if p is not self:
                acc += self.compute_acc(p)

        mu = 0.7
        self.vel = self.vel * mu + acc * dt


running = True
dt = 0.2

particles = []


while running:
    screen.fill((0, 0, 0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            pos = np.array(pg.mouse.get_pos(), np.float64)

            r = 50
            col = np.random.randint(0, len(colors))

            for r in range(50, 0, -20):
                for angle in range(0, 360, 20):
                    particles.append(
                        Particle(
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
                    )

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                show_debug = not show_debug

    for particle in particles:
        particle.update_pos(dt)
        particle.update_vel(particles, dt)
        particle.draw()

    pg.display.update()

pg.quit()
