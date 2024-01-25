import math
import random
import time

import numpy as np
import pygame

import config
from Objects.base import GravityObject
from map import playmap
from resources import load_image
from sounds import explosion_sound, play_fire_sounds


def count_damage(epicenter: pygame.Vector2, point: pygame.Vector2, radius: int, max_damage: int):
    dist = abs(point.distance_to(epicenter))
    if dist > radius:
        return 0
    x = abs(point.distance_to(epicenter) / radius)
    return int(2 ** (-x) * max_damage)


def full_damage(epicenter: pygame.Vector2, point: pygame.Vector2, radius: int, max_damage: int):
    dist = abs(point.distance_to(epicenter))
    if dist > radius:
        return 0
    return max_damage


class Bullet(GravityObject):

    def __init__(self, x, y, *group, sprite="bullets/blank.png", radius=25, ground_contact=True, duration=True,
                 max_damage=35, sound="data/sounds/explosion.wav", player_dmg_sound="data/sounds/explosion.wav",
                 **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.sound = sound
        self.player_dmg_sound = player_dmg_sound
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
        self.wind = 0

    def falling(self):
        self.falling_speed -= config.gravity / config.fps
        self.simple_move(0, self.falling_speed)

    def update(self):
        if self.is_visible:
            self.horizontal_speed += self.wind / config.fps
            self.simple_move(self.horizontal_speed, 0)
            if self.start and not self.rect.colliderect(self.owner.rect):
                self.start = False
            tank_contact = False
            if not self.start:
                for tank in self.tanks:
                    if tank.rect.colliderect(self.rect):
                        self.explosion()
                        tank_contact = True
                        break
            if self.in_bounds() and not tank_contact and self.ground_contact and self.check_ground_contact():
                self.explosion()
            self.angle_bullet()
            super().update()
        self.death_on_out_bounds()

    def death_on_out_bounds(self):
        if self.rect.centery > config.screen_size[1]:
            self.destroy()

    def shoot(self, speed, angle, tanks, wind, owner=None, **kwargs):
        self.owner = owner
        self.wind = wind
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

    def damaging(self):
        playmap.remove_circle(*self.rect.center, self.radius)
        for tank in self.tanks:
            tank.damage(count_damage(pygame.Vector2(self.rect.center), pygame.Vector2(tank.rect.center), self.radius,
                                     self.max_damage))

    def explosion(self):
        explosion_sound(self.sound)
        self.damaging()
        self.destroy()


class FireBullet(Bullet):
    def __init__(self, x, y, *group, sprite="bullets/fire_blank.png", flame_sound="data/sounds/flame_loop.wav",
                 player_flame_sound="data/sounds/flame_user_attack.wav", fire_pool=None, fire_count=20, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.fire_pool = fire_pool
        self.fire_count = fire_count
        self.flame_sound = flame_sound
        self.player_flame_sound = player_flame_sound

    def shoot(self, speed, angle, tanks, wind, owner=None, fire_pool=None, **kwargs):
        super().shoot(speed, angle, tanks, wind, owner)
        self.fire_pool = fire_pool
        print(self.fire_pool)

    def explosion(self):
        self.damaging()
        explosion_sound(self.sound)
        for i in range(self.fire_count):
            fire = Fire(self.rect.center[0] + random.randrange(-4, 4), self.rect.center[1] + random.randrange(-4, 4),
                        self.fire_pool, sound=self.flame_sound, player_dmg_sound=self.player_flame_sound)
            fire.shoot(speed=random.random(), angle=random.randrange(0, 180), tanks=self.tanks, wind=self.wind,
                       owner=self.owner)
        self.destroy()


class Fire(Bullet):
    def __init__(self, x, y, *group, sprite="bullets/fire.png", radius=2, max_damage=1, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, radius=radius, max_damage=max_damage, **kwargs)
        self.count_explosion = 5

    def update(self):
        self.image = pygame.transform.rotate(self.source_image, random.randrange(0, 4) * 90)
        if self.on_ground():
            self.falling_speed = -1
            self.horizontal_speed *= 0.2
            self.count_explosion -= 1
            self.explosion()
        super().update()

    def damaging(self):
        playmap.remove_circle(*self.rect.center, self.radius)
        for tank in self.tanks:
            dmg = full_damage(pygame.Vector2(self.rect.center), pygame.Vector2(tank.rect.center), self.radius + 5,
                              self.max_damage)
            tank.damage(dmg)
            if dmg != 0:
                self.count_explosion = 0
                explosion_sound(self.player_dmg_sound)

    def explosion(self):
        self.damaging()
        if self.count_explosion <= 0:
            self.destroy()


class TimeFireBullet(FireBullet):
    def __init__(self, x, y, *group, sprite="bullets/fire.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.timer = 0
        self.explosion_time = 0

    def shoot(self, speed, angle, tanks, wind, owner=None, fire_pool=None, timer=1):
        super().shoot(speed, angle, tanks, wind, owner, fire_pool)
        self.timer = time.time()
        self.explosion_time = timer

    def get_time(self):
        return self.explosion_time - round(time.time() - self.timer)

    def update(self):
        super().update()
        if time.time() - self.timer >= self.explosion_time:
            self.explosion()


weapons = {"Разрывной": {"class_bullet": Bullet, "pilot": (0.5, 0.5), "sprite": "bullets/blank.png", "duration": True,
                         "ui_sprite": "ui/icons/blank.png"},
           "Огненный снаряд": {"class_bullet": FireBullet, "pilot": (0.5, 0.5), "sprite": "bullets/fire_blank.png",
                               "duration": True, "radius": 10, "max_damage": 10,
                               "ui_sprite": "ui/icons/fire_blank.png"},
           "Огненный снаряд с таймером": {"class_bullet": TimeFireBullet, "pilot": (0.5, 0.5),
                                          "sprite": "bullets/time_fire_blank.png",
                                          "duration": True, "radius": 10, "max_damage": 10, "fire_count": 25,
                                          "ui_sprite": "ui/icons/time_fire_blank.png",
                                          "sound": "data/sounds/fire_bullet_air.wav"}

           }
