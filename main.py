import itertools
import random
import sys
import time
import pygame

import config
from Objects.base import GravityObject
from Objects.particles import Leaf
from Objects.tank import Tank
from Objects.ui import WeaponPanel
from Objects.weapon import Bullet, weapons, TimeFireBullet
from colors import *
from map import playmap

clock = pygame.time.Clock()
pygame.init()

screen = pygame.display.set_mode(config.screen_size)

health_font = pygame.font.Font('data/font/rus.ttf', 24)
timer_font = pygame.font.Font('data/font/rus.ttf', 20)
wind_font = pygame.font.Font('data/font/rus.ttf', 24)
info_font = pygame.font.Font('data/font/rus.ttf', 30)
weapon_font = pygame.font.Font('data/font/rus.ttf', 24)

shoot_press_time = 0
shoot = False
is_shoot = False

shoot_timer = 2

tanks_pool = pygame.sprite.Group()
bullets_pool = pygame.sprite.Group()
leaf_pool = pygame.sprite.Group()
fire_pool = pygame.sprite.Group()
ui_pool = pygame.sprite.Group()

# UI
info_text = ""
show_info_text = False
info_timer = 2
start_info_timer = 0

weapon_panel = WeaponPanel(screen.get_width(), screen.get_height() // 2, 64, 64, pygame.Color('#222034'),
                           screen.get_width() - 64 - 20, screen.get_height() // 2, ui_pool)

wind = random.randrange(-5, 5)

# INPUT
is_pressed = [False, False, False, False, False]  # left, right, up, down, space

cur_bullet = weapon_panel.current_weapon()
tanks = [Tank(450, 100, tanks_pool, sprite="tanks/red.png", color=tank_red_color),
         Tank(600, 100, tanks_pool, sprite="tanks/yellow.png", color=tank_yellow_color), ]
tanks_cycle = itertools.cycle(tanks)
cur_tank = next(tanks_cycle)


def shooting(force):
    global cur_tank, wind, is_shoot
    cur_tank.shoot(force, bullets_pool, tanks, wind, fire_pool=fire_pool, timer=shoot_timer, **cur_bullet)
    cur_tank = next(tanks_cycle)
    is_shoot = True


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not is_shoot and event.type == pygame.KEYDOWN:
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
                    shooting(10)
            if event.key == pygame.K_TAB:
                cur_tank = next(tanks_cycle)
            if event.unicode.isdigit() and 1 <= int(event.unicode) <= 3:
                start_info_timer = time.time()
                shoot_timer = int(event.unicode)
                info_text = f"Задержка для снаряда установлена: {shoot_timer} сек"
                show_info_text = True

        if not is_shoot and event.type == pygame.KEYUP:
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
                    shooting(10 * (time.time() - shoot_press_time))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if weapon_panel.end:
                    weapon_panel.select_weapon(pygame.mouse.get_pos())
                    cur_bullet = weapon_panel.current_weapon()
                    weapon_panel.close_open()
            if event.button == 3:
                weapon_panel.close_open()
    if not is_shoot:
        if is_pressed[4] and cur_bullet["duration"]:
            if time.time() - shoot_press_time >= 1:
                if not shoot and cur_tank.can_control:
                    is_pressed[4] = False
                    shoot = True
                    shooting(10)
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
    if len(leaf_pool.sprites()) < 20:
        Leaf(random.randrange(0, config.screen_size[0]), 0, leaf_pool)
    for leaf in leaf_pool:
        leaf.wind = wind

    leaf_pool.update()
    leaf_pool.draw(screen)

    tanks_pool.update()
    tanks_pool.draw(screen)

    bullets_pool.update()
    bullets_pool.draw(screen)

    fire_pool.update()
    fire_pool.draw(screen)
    # draw barrel

    for tank in tanks_pool.sprites():
        rot = pygame.Vector2(10, 0).rotate(-tank.angle)
        pygame.draw.line(screen, tank.color, tank.rect.center, tank.rect.center + rot)

        health = health_font.render(str(tank.health), False, tank.color)
        screen.blit(health,
                    (tank.rect.centerx - health.get_width() // 2, tank.rect.top - 10 - health.get_height() // 2))

    if not is_shoot and not shoot and cur_bullet["duration"] and is_pressed[4]:
        for i in range(1, int((time.time() - shoot_press_time) * 100), 10):
            if i > 100:
                break
            rot = pygame.Vector2(-10, 0).rotate(180 - cur_tank.angle)
            pygame.draw.circle(screen, (255, 255 * (100 - i) * 0.01, 0),
                               cur_tank.rect.center + rot + rot * i // 10, 1 + (i // 10))
    for bullet in bullets_pool.sprites():
        if isinstance(bullet, TimeFireBullet):
            timer_boom = timer_font.render(str(bullet.get_time()), False, timer_boom_color)
            screen.blit(timer_boom,
                        (bullet.rect.left - timer_boom.get_width() - 5, bullet.rect.top - timer_boom.get_height() - 5))

    if is_shoot and len(bullets_pool.sprites()) == 0:
        is_shoot = False
        wind = random.randrange(-5, 5)
    if show_info_text:
        if time.time() - start_info_timer < info_timer:
            info = info_font.render(info_text, False, info_color)
            screen.blit(info,
                        (screen.get_width() // 2 - info.get_width() // 2, 0))
        else:
            show_info_text = False

    # UI
    wind_text = wind_font.render(str(wind), False, wind_color)
    screen.blit(wind_text, (screen.get_width() - 50 - wind_text.get_width(), 0))

    weapon_panel.update()
    weapon_panel.draw(screen)

    ui_pool.update()
    ui_pool.draw(screen)

    clock.tick(config.fps)
    pygame.display.flip()
