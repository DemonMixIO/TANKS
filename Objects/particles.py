import random

import pygame

import config
from Objects.base import GravityObject, Object


class Leaf(Object):
    def __init__(self, x, y, *group, sprite="decor/leaf.png", wind=0, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.wind = wind
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


class Fountain(Leaf, GravityObject):
    def __init__(self, x, y, *group, sprite="bullet/fire.png", falling_speed=0, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        super(Leaf, self).__init__(x, y, *group, sprite=sprite, **kwargs)
        self.falling_speed = falling_speed

    def falling(self):
        self.falling_speed -= config.gravity / config.fps
        self.simple_move(0, self.falling_speed)

    def update(self):
        self.simple_move(self.wind, 0)
        self.falling()
        if self.rect.top > config.screen_size[1]:
            self.destroy()
