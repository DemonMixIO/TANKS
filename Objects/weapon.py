import math

import numpy as np
import pygame

from Objects.base import GravityObject
from map import playmap
from resources import load_image


def count_damage(epicenter: pygame.Vector2, point: pygame.Vector2, radius: int, max_damage: int):
    dist = abs(point.distance_to(epicenter))
    if dist > radius:
        return 0
    x = abs(point.distance_to(epicenter) / radius)
    return int(2 ** (-x) * max_damage)


class Bullet(GravityObject):
    def __init__(self, x, y, *group, sprite="bullets/blank.png", radius=25, ground_contact=True, duration=True,
                 max_damage=35, **kwargs):
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
        self.tanks = []
        self.start = True
        self.max_damage = max_damage

    def update(self):
        if self.is_visible:
            self.physics_move(self.horizontal_speed, 0)
            if self.start and not self.rect.colliderect(self.owner.rect):
                self.start = False
            tank_contact = False
            if not self.start:
                for tank in self.tanks:
                    if tank.rect.colliderect(self.rect):
                        self.explosion()
                        tank_contact = True
                        break
            if not tank_contact and self.ground_contact and self.check_ground_contact():
                self.explosion()
            self.angle_bullet()
            super().update()
        if not self.in_bounds():
            self.kill()
            del self

    def shoot(self, speed, angle, tanks, owner=None):
        self.owner = owner
        self.tanks = tanks
        self.is_visible = True
        self.active = True
        self.start = True
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
        for tank in self.tanks:
            tank.damage(count_damage(pygame.Vector2(self.rect.center), pygame.Vector2(tank.rect.center), self.radius,
                                     self.max_damage))
        self.kill()
        del self
