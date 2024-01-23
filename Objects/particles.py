import random

import pygame

import config
from Objects.base import GravityObject, Object


class Leaf(Object):
    def __init__(self, x, y, *group, sprite="decor/leaf.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.wind = 0
        self.angle = random.randrange(-5, 5)
        self.rotation = 0
        self.start = True

    def update(self):
        self.simple_move(self.wind, 5)
        self.rotation += self.angle
        self.image = pygame.transform.rotate(self.source_image, self.rotation)
        super().update()
        if self.start and self.in_bounds():
            self.start = False
        if not self.start:
            self.death_on_out_bounds()

