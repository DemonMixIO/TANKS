import pygame

from Objects.base import GravityObject


class Tank(GravityObject):
    def __init__(self, x, y, *group, sprite="default.png", can_control=True, color=(255, 0, 0),  **kwargs):
        super().__init__(x, y, *group, sprite=sprite, **kwargs)
        self.can_control = can_control
        self.angle = 0
        self.color = color

    def player_move(self, dx, dy):
        if self.can_control:
            self.physics_move(dx, dy)

    def turn(self, angle):
        if 0 <= self.angle + angle <= 180:
            self.angle += angle
        print(self.angle)

    def shoot(self, speed, bullet_pool, class_bullet, **data):
        print("shoot")
        rot = pygame.Vector2(8, 0).rotate(-self.angle)
        bul = class_bullet(self.rect.centerx + rot.x, self.rect.centery + rot.y, bullet_pool, **data)
        bul.shoot(speed, self.angle)
