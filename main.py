import itertools
import sys
import time
import pygame

import config
from Objects.base import GravityObject
from Objects.tank import Tank
from Objects.weapon import Bullet
from map import playmap

clock = pygame.time.Clock()
pygame.init()

shoot_press_time = 0
shoot = False

# INPUT
is_pressed = [False, False, False, False, False]  # left, right, up, down, space

screen = pygame.display.set_mode(config.screen_size)

tanks_pool = pygame.sprite.Group()
bullets_pool = pygame.sprite.Group()
cur_bullet = {"class_bullet": Bullet, "pilot": (0.5, 0.5), "sprite": "bullets/blank.png", "duration": True}
tanks = [Tank(450, 100, tanks_pool, sprite="tanks/red.png"),
         Tank(600, 100, tanks_pool, sprite="tanks/yellow.png", color=(255, 255, 0)), ]
tanks_cycle = itertools.cycle(tanks)
cur_tank = next(tanks_cycle)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = True
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = True
            if event.key == pygame.K_UP:
                is_pressed[2] = True
            if event.key == pygame.K_DOWN:
                is_pressed[3] = True
            if event.key == pygame.K_SPACE:
                if cur_bullet["duration"]:
                    is_pressed[4] = True
                    shoot = False
                    shoot_press_time = time.time()
                else:
                    cur_tank.shoot(10)
            if event.key == pygame.K_TAB:
                cur_tank = next(tanks_cycle)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                is_pressed[0] = False
            if event.key == pygame.K_RIGHT:
                is_pressed[1] = False
            if event.key == pygame.K_UP:
                is_pressed[2] = False
            if event.key == pygame.K_DOWN:
                is_pressed[3] = False
            if event.key == pygame.K_SPACE:
                is_pressed[4] = False
                if not shoot and cur_tank.can_control:
                    cur_tank.shoot(10 * (time.time() - shoot_press_time), bullets_pool, tanks, **cur_bullet)
                    cur_tank = next(tanks_cycle)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                playmap.remove_circle(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 25)
    if is_pressed[4] and cur_bullet["duration"]:
        if time.time() - shoot_press_time >= 1:
            if not shoot and cur_tank.can_control:
                cur_tank.shoot(10, bullets_pool, tanks, **cur_bullet)
                is_pressed[4] = False
                shoot = True
                cur_tank = next(tanks_cycle)
    else:
        if is_pressed[0]:
            cur_tank.player_move(-0.7, 0)
        if is_pressed[1]:
            cur_tank.player_move(+0.7, 0)
        if is_pressed[2]:
            cur_tank.turn(1)
        if is_pressed[3]:
            cur_tank.turn(-1)

    playmap.draw_map(screen)

    tanks_pool.update()
    tanks_pool.draw(screen)

    bullets_pool.update()
    bullets_pool.draw(screen)
    # draw barrel

    font = pygame.font.Font('data/font/pixel.ttf', 24)

    for tank in tanks_pool.sprites():
        rot = pygame.Vector2(10, 0).rotate(-tank.angle)
        pygame.draw.line(screen, tank.color, tank.rect.center, tank.rect.center + rot)

        health = font.render(str(tank.health), False, tank.color)
        screen.blit(health,
                    (tank.rect.centerx - health.get_width() // 2, tank.rect.top - 10 - health.get_height() // 2,))

    if not shoot and cur_bullet["duration"] and is_pressed[4]:
        for i in range(1, int((time.time() - shoot_press_time) * 100), 10):
            if i > 100:
                break
            rot = pygame.Vector2(-10, 0).rotate(180 - cur_tank.angle)
            pygame.draw.circle(screen, (255, 255 * (100 - i) * 0.01, 0),
                               cur_tank.rect.center + rot + rot * i // 10, 1 + (i // 10))

    clock.tick(config.fps)
    pygame.display.flip()
