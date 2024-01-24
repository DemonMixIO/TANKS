import pygame

import config
from map import playmap
from resources import load_image

screen_bound = pygame.Rect(0, 0, *config.screen_size)


class Object(pygame.sprite.Sprite):

    def in_bounds(self):
        return screen_bound.contains(self.rect)

    def __init__(self, x, y, *group, sprite="default.png", pilot=(0, 0), pilot_pixel=False, scale=(-1, -1), **kwargs):
        super().__init__(*group)
        self.scale = scale
        if self.scale != (-1, -1):
            self.source_image = pygame.transform.scale(load_image(sprite), scale)
        else:
            self.source_image = load_image(sprite)
        self.image = self.source_image
        self.pilot_pixel = pilot_pixel
        self.pilot = pilot
        self.rect = self.image.get_rect()
        self.float_position = pygame.Vector2(0, 0)
        self.moveto(x, y)
        self.is_visible = True
        self.update_rect()

    def set_image(self, sprite="default.png", scale=(-1, -1)):
        self.scale = scale
        if self.scale != (-1, -1):
            self.source_image = pygame.transform.scale(load_image(sprite), scale)
        else:
            self.source_image = load_image(sprite)
        self.image = self.source_image

    def moveto(self, x, y):
        if not self.pilot_pixel:
            self.float_position.x = x - self.image.get_width() * self.pilot[0]
            self.float_position.y = y - self.image.get_height() * self.pilot[1]
        else:
            self.float_position.x = x - self.pilot[0]
            self.float_position.y = y - self.pilot[1]
        self.update_rect()

    def get_pilot(self):
        if not self.pilot_pixel:
            return pygame.Vector2(self.rect.x + self.image.get_width() * self.pilot[0],
                                  self.rect.y + self.image.get_height() * self.pilot[1])
        else:
            return pygame.Vector2(self.rect.x + self.pilot[0], self.rect.y + self.pilot[1])

    def simple_move(self, dx, dy):
        self.float_position.x += dx
        self.float_position.y += dy
        self.update_rect()

    def update(self):
        if self.is_visible:
            self.update_rect()

    def update_rect(self):
        self.rect.x = round(self.float_position.x)
        self.rect.y = round(self.float_position.y)
        # print(self.rect)

    def move(self, dx, dy):
        self.rect = self.rect.move(dx, dy)

    def death_on_out_bounds(self):
        if not self.in_bounds():
            self.destroy()

    def destroy(self):
        self.kill()
        del self


class GravityObject(Object):

    def __init__(self, x, y, *group, sprite="default.png", kinematic=False, **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.falling_speed = 0
        self.kinematic = kinematic
        self.is_move = False

    def update(self):
        super().update()
        if not self.kinematic:
            self.falling()

    def falling(self):
        if not self.on_ground():
            self.falling_speed -= config.gravity / config.fps
        elif self.on_ground():
            self.falling_speed = 0

        if self.falling_speed < 0 and playmap.check_ground_top(self.rect):
            self.falling_speed = 0

        if playmap.check_in_ground(self.rect):
            self.falling_speed = -1
        self.simple_move(0, self.falling_speed)

    def physics_move(self, dx, dy):
        if (dx > 0 and playmap.can_move_right(self.rect) or dx < 0 and playmap.can_move_left(
                self.rect)) and self.in_bounds():
            self.float_position.x += dx
            self.update_rect()
            self.is_move = True

        self.float_position.y += dy

    def on_ground(self) -> bool:
        return playmap.check_on_ground(self.rect)

    def check_ground_contact(self):
        return playmap.check_in_ground_around(self.rect) or playmap.check_on_ground_around(self.rect)
