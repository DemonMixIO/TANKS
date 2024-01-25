import pygame

pygame.mixer.init()
click_sound = pygame.mixer.Sound('data/sounds/click.ogg')
throwpowerup_sound = pygame.mixer.Sound('data/sounds/throwpowerup.wav')
throwreliase_sound = pygame.mixer.Sound('data/sounds/throwreliase.wav')
fire_damage_sound = pygame.mixer.Sound('data/sounds/flame_loop.wav')
start_game_sound = pygame.mixer.Sound('data/sounds/cow_moo.wav')

engine_sounds = ['data/sounds/engine1.wav', 'data/sounds/engine2.wav', 'data/sounds/engine3.wav']
engine_sound = pygame.mixer.Sound('data/sounds/engine1.wav')


def play_menu_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load("data/music/menu.mp3")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(loops=-1)


def play_game_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load("data/music/battle.mp3")
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(loops=-1)


def play_loading_music():
    pygame.mixer.music.load('data/music/bg.mp3')
    pygame.mixer.music.play(-1)


fired = False


def play_fire_sounds():
    global fired
    if not fired:
        fired = True
        fire_damage_sound.set_volume(0.1)
        fire_damage_sound.play(-1)


def stop_fire_sound():
    global fired
    fired = False
    fire_damage_sound.stop()


move = False


def play_engine_sounds(path):
    global move, engine_sound
    if not move:
        move = True
        engine_sound = pygame.mixer.Sound(path)
        engine_sound.set_volume(0.1)
        engine_sound.play(-1)


def stop_engine_sound():
    global move
    move = False
    engine_sound.stop()


def explosion_sound(path):
    explosion = pygame.mixer.Sound(path)
    explosion.set_volume(0.5)
    explosion.play()
