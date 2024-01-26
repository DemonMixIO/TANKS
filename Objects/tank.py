import math

import numpy as np
import pygame

import config
from Objects.base import GravityObject
from Objects.weapon import weapons
from resources import load_image


class Tank(GravityObject):
    def __init__(self, x, y, *group, sprite="default.png", can_control=True, color=(255, 0, 0),
                 death_sprite="default.png", engine_sound="data/sounds/engine1.wav", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)

        self.can_control = can_control
        self.angle = 0
        self.color = color
        self.health = 100
        self.cur_weapon = list(weapons.keys())[0]
        self.death_sprite = load_image(death_sprite)
        self.engine_sound = engine_sound
        self.horizontal_speed = 0

    def set_cur_weapon(self, cur_weapon_name):
        self.cur_weapon = cur_weapon_name

    def damage(self, damage, vect=(0, 0)):
        self.health -= damage
        self.horizontal_speed = vect[0]
        self.falling_speed = -vect[1]
        if self.health <= 0:
            self.image = self.death_sprite
            self.health = 0
            self.can_control = False

    def check_death(self):
        return self.health <= 0

    def update(self):
        if self.horizontal_speed != 0:
            print(self.horizontal_speed)
        if self.on_ground():
            self.horizontal_speed += -np.sign(self.horizontal_speed) * 5 / config.fps
        else:
            self.horizontal_speed += -np.sign(self.horizontal_speed) * 1 / config.fps
        if abs(self.horizontal_speed) < 0.1:
            self.horizontal_speed = 0
        self.physics_move(self.horizontal_speed, 0)
        if not self.in_bounds():
            self.health = 0
        super().update()

    def player_move(self, dx, dy):
        if self.can_control:
            self.physics_move(dx, dy)

    def turn(self, angle):
        if 0 <= self.angle + angle <= 180:
            self.angle += angle

    def shoot(self, speed, bullet_pool, tanks, wind, fire_pool, timer, class_bullet, **data):
        rot = pygame.Vector2(8, 0).rotate(-self.angle)
        bul = class_bullet(self.rect.centerx + rot.x, self.rect.centery + rot.y, bullet_pool, **data)
        bul.shoot(speed, self.angle, tanks, wind, owner=self, fire_pool=fire_pool, timer=timer)
