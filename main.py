import asyncio
import copy
import itertools
import json
import os
import random
import sys
import time
import shutil

import pygame_gui
from PIL import Image
from pygame_gui.windows import UIFileDialog

import config
from Objects.base import GravityObject, Object
from Objects.particles import Leaf
from Objects.tank import Tank
from Objects.ui import WeaponPanel, Marker, Panel
from Objects.weapon import Bullet, weapons, TimeFireBullet
from colors import *
from map import playmap

SHOWMARKER = pygame.USEREVENT + 1021
END = pygame.USEREVENT + 1023
START = pygame.USEREVENT + 1024

in_menu = True
start_game = False
opening_file = False

clock = pygame.time.Clock()
pygame.init()

screen = pygame.display.set_mode(config.screen_size)
manager = pygame_gui.UIManager(config.screen_size)

health_font = pygame.font.Font('data/font/rus.ttf', 24)
timer_font = pygame.font.Font('data/font/rus.ttf', 20)
wind_font = pygame.font.Font('data/font/rus.ttf', 24)
info_font = pygame.font.Font('data/font/rus.ttf', 30)
weapon_font = pygame.font.Font('data/font/rus.ttf', 24)
map_info_font = pygame.font.Font('data/font/rus.ttf', 24)

shoot_press_time = 0
shoot = False
is_shoot = False

shoot_timer = 2

tanks_pool = pygame.sprite.Group()
bullets_pool = pygame.sprite.Group()
leaf_pool = pygame.sprite.Group()
fire_pool = pygame.sprite.Group()
ui_pool = pygame.sprite.Group()
marker_pool = pygame.sprite.Group()

# UI
info_text = ""
show_info_text = False
info_timer = 2
start_info_timer = 0

weapon_panel = WeaponPanel(screen.get_width(), screen.get_height() // 2, 64, 64, pygame.Color('#222034'),
                           screen.get_width() - 64 - 20, screen.get_height() // 2, ui_pool)

visible_marker = False
marker = Marker(0, 0, marker_pool, sprite="ui/marker.png", pilot=(0.5, 0.5))
# PHYSICS
wind = random.randrange(-5, 5)

# INPUT
is_pressed = [False, False, False, False, False]  # left, right, up, down, space

cur_bullet = weapon_panel.current_weapon()
tanks_colors = [("tanks/red.png", tank_red_color), ("tanks/green.png", tank_green_color),
                ("tanks/orange.png", tank_orange_color), ("tanks/purple.png", tank_purple_color),
                ("tanks/blue.png", tank_blue_color), ("tanks/yellow.png", tank_yellow_color),
                ]
tanks = []
cnt_spawn = 3
cnt_lives = cnt_spawn

tanks_cycle = None
cur_tank = None

# MENU OBJECTS
menu_pool = pygame.sprite.Group()

logo = Object(screen.get_width() // 2, 0, menu_pool, sprite="ui/logo/logo.png", pilot=(0.5, 0))
minimap_panel = Panel(screen.get_width() // 5 - 128, screen.get_height() // 3 - 71, 256, 142, pygame.Color("black"))

maps = []


def spawn_tanks():
    tanks_pool.empty()
    tanks.clear()
    global cnt_lives, tanks_cycle, cur_tank
    tanks_shuffle = copy.deepcopy(tanks_colors)
    random.shuffle(tanks_colors)
    step = (screen.get_width() - 200) // cnt_spawn
    cnt_lives = cnt_spawn
    for idx in range(cnt_spawn):
        tanks.append(
            Tank(100 + step * idx, random.randrange(100, 300), tanks_pool, sprite=tanks_shuffle[idx][0],
                 color=tanks_shuffle[idx][1]))
    tanks_cycle = itertools.cycle(tanks)
    cur_tank = next(tanks_cycle)


def load_maps():
    global maps
    with open("data/maps/maps.json") as map_data:
        maps = json.load(map_data)["maps"]


load_maps()
cur_map_index = 0
minimap = Object(screen.get_width() // 5, screen.get_height() // 3, menu_pool, sprite=maps[cur_map_index]["dir"],
                 pilot=(0.5, 0.5), scale=(256, 142))

prev_map = Object(minimap.rect.left - 20, screen.get_height() // 3, menu_pool, sprite="ui/prev_map.png",
                  pilot=(1, 0.5))
next_map = Object(minimap.rect.right + 20, screen.get_height() // 3, menu_pool, sprite="ui/next_map.png",
                  pilot=(0, 0.5))

load_button = Object(screen.get_width() // 5, minimap.rect.bottom + 50, menu_pool, sprite="ui/load_map.png",
                     pilot=(0.5, 0))

start_button = Object(screen.get_width() // 2, int(screen.get_height() * (3 / 4)), menu_pool, sprite="ui/start.png",
                      pilot=(0.5, 0.5))


def load_user_map(file_name):
    im = Image.open(file_name)
    im = im.resize(config.screen_size)
    cur_time = int(time.time())
    im.save(f"data/maps/{cur_time}{os.path.basename(file_name).split('/')[-1]}")
    maps.append({"name": f"Польз. {os.path.basename(file_name).split('/')[-1].split('.')[0]}",
                 "dir": f"maps/{cur_time}{os.path.basename(file_name).split('/')[-1]}"})
    global opening_file
    opening_file = False
    save_map()


def save_map():
    with open('data/maps/maps.json', 'w') as map_data:
        json.dump({"maps": maps}, map_data, ensure_ascii=False)
        map_data.close()


def select_next_map():
    global cur_map_index
    cur_map_index += 1
    if cur_map_index >= len(maps):
        cur_map_index = 0
    update_map()


def select_prev_map():
    global cur_map_index
    cur_map_index -= 1
    if cur_map_index < 0:
        cur_map_index = len(maps) - 1
    update_map()


def update_map():
    minimap.set_image(maps[cur_map_index]["dir"], (256, 142))


def hide_marker():
    global visible_marker
    marker.is_visible = False


def show_marker():
    marker.set_pos(cur_tank.rect.centerx, cur_tank.rect.centery - 40)
    global visible_marker
    marker.is_visible = True


def shooting(force):
    global cur_tank, wind, is_shoot
    cur_tank.shoot(force, bullets_pool, tanks, wind, fire_pool=fire_pool, timer=shoot_timer, **cur_bullet)
    cur_tank = next(tanks_cycle)
    is_shoot = True


def restore_params():
    global info_text, show_info_text, is_pressed
    info_text = ""
    show_info_text = False
    is_pressed = [False, False, False, False, False]  # left, right, up, down, space


is_running = True

while is_running:
    time_delta = clock.tick(config.fps) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            pygame.quit()
            sys.exit()

        if not in_menu:
            if event.type == SHOWMARKER:
                show_marker()
            if event.type == pygame.KEYDOWN:
                hide_marker()
            if event.type == END:
                in_menu = True
            if cnt_lives != 1:
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
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not start_game and not opening_file:
                        if prev_map.rect.collidepoint(pygame.mouse.get_pos()):
                            select_prev_map()
                        if next_map.rect.collidepoint(pygame.mouse.get_pos()):
                            select_next_map()
                        if start_button.rect.collidepoint(pygame.mouse.get_pos()):
                            start_game = True
                            playmap.set_image(maps[cur_map_index]["dir"])
                            pygame.time.set_timer(START, 2000, 1)
                        if load_button.rect.collidepoint(pygame.mouse.get_pos()):
                            opening_file = True
                            file_selection = UIFileDialog(
                                rect=pygame.Rect(screen.get_width() // 3, screen.get_height() // 3,
                                                 int(screen.get_width() * (2 / 3)), int(screen.get_height() * (2 / 3))),
                                manager=manager,
                                allowed_suffixes={"png"})
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == file_selection.ok_button:
                    load_user_map(file_selection.current_file_path)
                    opening_file = False
                if event.ui_element in (file_selection.cancel_button, file_selection.close_window_button):
                    opening_file = False
            if event.type == START:
                in_menu = False
                start_game = False
                restore_params()
                spawn_tanks()
            manager.process_events(event)
    if not in_menu:
        if cnt_lives != 1:

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
            if not tank.check_death():
                rot = pygame.Vector2(10, 0).rotate(-tank.angle)
                pygame.draw.line(screen, tank.color, tank.rect.center, tank.rect.center + rot)

                health = health_font.render(str(tank.health), False, tank.color)
                screen.blit(health,
                            (
                                tank.rect.centerx - health.get_width() // 2,
                                tank.rect.top - 10 - health.get_height() // 2))

        if cnt_lives != 1:
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
                                (bullet.rect.left - timer_boom.get_width() - 5,
                                 bullet.rect.top - timer_boom.get_height() - 5))

            if is_shoot and len(bullets_pool.sprites()) == 0:
                is_shoot = False
                wind = random.randrange(-5, 5)
                show_marker()
            if show_info_text:
                if time.time() - start_info_timer < info_timer:
                    info = info_font.render(info_text, False, info_color)
                    screen.blit(info,
                                (screen.get_width() // 2 - info.get_width() // 2, 0))
                else:
                    show_info_text = False

            cnt_lives = 0
            for tank in tanks:
                if not tank.check_death():
                    cnt_lives += 1
            if cnt_lives <= 1:
                pygame.time.set_timer(END, 5000, 1)

        # UI
        wind_text = wind_font.render(str(wind), False, wind_color)
        screen.blit(wind_text, (screen.get_width() - 50 - wind_text.get_width(), 0))

        weapon_panel.update()
        weapon_panel.draw(screen)

        ui_pool.update()
        ui_pool.draw(screen)

        if marker.is_visible:
            marker.set_pos(cur_tank.rect.centerx, cur_tank.rect.centery - 40)
            marker_pool.update()
            marker_pool.draw(screen)

        if cur_tank.check_death():
            cur_tank = next(tanks_cycle)
    else:

        pygame.draw.rect(screen, menu_background, (0, 0, screen.get_width(), screen.get_width()))
        minimap_panel.draw(screen)

        menu_pool.update()
        menu_pool.draw(screen)

        map_text = map_info_font.render(maps[cur_map_index]["name"], False, white)
        screen.blit(map_text, (
            screen.get_width() // 5 - map_text.get_width() // 2, minimap.rect.bottom + 20 - map_text.get_height() // 2))

        manager.update(time_delta)
        manager.draw_ui(screen)
    pygame.display.flip()
