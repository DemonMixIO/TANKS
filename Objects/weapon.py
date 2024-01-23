import math

import numpy as np
import pygame

from Objects.base import GravityObject
from map import playmap
from resources import load_image


class Bullet(GravityObject):
    def __init__(self, x, y, *group, sprite="bullets/blank.png", radius=25, ground_contact=True, duration=True, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.radius = radius
        self.owner = None
        self.is_visible = True
        self.ground_contact = ground_contact
        self.source_image = load_image(sprite)
        self.active = False
        self.horizontal_speed = 5
        self.direction = 1
        self.rotation = 0
        self.duration = duration

    def update(self):
        if self.is_visible:
            self.physics_move(self.horizontal_speed, 0)
            if self.ground_contact and self.check_ground_contact():
                self.explosion()
            self.angle_bullet()
            super().update()
        if not self.in_bounds():
            self.kill()
            del self

    def shoot(self, speed, angle, owner=None):
        self.owner = owner
        self.is_visible = True
        self.active = True
        self.falling_speed = -speed * math.sin(math.radians(angle))
        self.horizontal_speed = speed * math.cos(math.radians(angle))
        # print(self.falling_speed, self.horizontal_speed)

    def angle_bullet(self):
        vect = pygame.Vector2(self.horizontal_speed, self.falling_speed)
        if vect.x == 0 or math.sqrt(vect.x ** 2 + vect.y ** 2) == 0:
            self.rotation = 0
        else:
            try:
                self.rotation = -np.sign(self.falling_speed) * math.degrees(math.acos(
                    (vect.x ** 2) / (math.sqrt(vect.x ** 2 + vect.y ** 2) * vect.x)))
            except ZeroDivisionError:
                print(vect.x, math.sqrt(vect.x ** 2 + vect.y ** 2))
                self.rotation = 0
        self.image = pygame.transform.rotate(self.source_image, self.rotation)

    def explosion(self):
        print("Expolosion")
        playmap.remove_circle(*self.rect.center, self.radius)
        self.kill()
        del self
