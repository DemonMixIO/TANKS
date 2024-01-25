import math
import time
from typing import Union, Tuple

import pygame.draw

import config
from Objects.base import Object, AnimatedObject
from Objects.weapon import weapons
from resources import load_image


class Icon(Object):
    def __init__(self, x, y, *group, sprite="default.png", name="", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.name = name


class Marker(Object):
    def __init__(self, x, y, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.up = False
        self.start_vec = pygame.Vector2(x, y)
        self.end_vec = self.start_vec + pygame.Vector2(0, -20)
        self.timer = time.time()

    def set_pos(self, x, y):
        self.up = False
        self.start_vec = pygame.Vector2(x, y)
        self.moveto(self.start_vec.x, self.start_vec.y)


class SinObject(Object):
    def __init__(self, x, y, *group, sprite="default.png", amplitude=1, speed=3, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.amplitude = amplitude
        self.speed = speed

    def update(self):
        self.moveto(self.rect.centerx,
                    self.rect.centery + math.sin(time.time() * self.speed) * self.amplitude)
        super().update()


class UI:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)

    def draw(self, screen):
        pass

    def update(self):
        pass

    def moveto(self, x, y):
        self.pos = pygame.Vector2(x, y)

    def move(self, dx, dy):
        self.pos += pygame.Vector2(dx, dy)


class Panel(UI):
    def __init__(self, x, y, width, height, color, border_radius=4):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.color = color
        self.border_radius = border_radius

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos.x, self.pos.y, self.width, self.height),
                         border_radius=self.border_radius)

    def update(self):
        pass


# class Button:

class WeaponPanel(Panel):
    def __init__(self, x, y, width, height, color, x_open, y_open, ui_pool):
        super().__init__(x, y, width, height * len(weapons), color)
        self.open = False
        self.end = False
        self.close_vec = pygame.Vector2(x, y)
        self.open_vec = pygame.Vector2(x_open, y_open)
        self.speed = 10
        self.time_animate = 0.5
        self.timer = 0
        self.select = 0
        self.ui_pool = ui_pool
        self.weapons = [Icon(self.pos.x, self.pos.y + n * 64, self.ui_pool, name=k, sprite=v["ui_sprite"]) for
                        n, (k, v)
                        in enumerate(weapons.items())]
        self.selected = Icon(self.pos.x, self.pos.y + self.select * 64, self.ui_pool, name="select",
                             sprite="ui/selected.png")

    def close_open(self):
        self.open = not self.open
        self.timer = time.time()

    def update(self):

        if (self.open and self.open_vec == self.pos) or (not self.open and self.close_vec == self.pos):
            self.end = True
        else:
            self.end = False
        if not self.end:
            self.pos = pygame.Vector2(pygame.math.lerp(self.close_vec.x if self.open else self.open_vec.x,
                                                       self.open_vec.x if self.open else self.close_vec.x,
                                                       (time.time() - self.timer) / self.time_animate if
                                                       (time.time() - self.timer) / self.time_animate <= 1 else 1),
                                      pygame.math.lerp(self.close_vec.y if self.open else self.open_vec.y,
                                                       self.open_vec.y if self.open else self.close_vec.y,
                                                       (time.time() - self.timer) / self.time_animate if
                                                       (time.time() - self.timer) / self.time_animate <= 1 else 1))
        for n, icon in enumerate(self.weapons):
            icon.moveto(self.pos.x, self.pos.y + n * 64)
        self.selected.moveto(self.pos.x, self.pos.y + self.select * 64)

    def current_weapon(self):
        return weapons[self.name_current_weapon()]

    def name_current_weapon(self):
        return self.weapons[self.select].name

    def set_weapon_by_name(self, name):
        for n, icon in enumerate(self.weapons):
            if icon.name == name:
                self.select = n
                break

    def select_weapon(self, pos):
        for n, icon in enumerate(self.weapons):
            if icon.rect.collidepoint(pos):
                self.select = n
                break


class BulletMarker(AnimatedObject):
    def __init__(self, x, y, *group, sprite="default.png", **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.active = False

    def set_bullet_pos(self, x, y):
        if not config.screen_rect.collidepoint(x, y):
            self.active = True

            if x < 0 and y < 0:
                self.set_frame(0)
            elif x < 0 and y > config.screen_size[1]:
                self.set_frame(6)
            elif x > config.screen_size[0] and y < 0:
                self.set_frame(2)
            elif x > config.screen_size[0] and y > config.screen_size[1]:
                self.set_frame(8)
            elif x < 0:
                self.set_frame(3)
            elif x > config.screen_size[0]:
                self.set_frame(5)
            elif y < 0:
                self.set_frame(1)
            elif y > config.screen_size[1]:
                self.set_frame(7)
        else:
            self.active = False
        pos_x, pos_y = x, y
        if x < 0:
            pos_x = 10
        if x > config.screen_size[0]:
            pos_x = config.screen_size[0] - 10
        if y < 0:
            pos_y = 10
        if y > config.screen_size[1]:
            pos_y = config.screen_size[1] - 10
        self.moveto(pos_x, pos_y)
