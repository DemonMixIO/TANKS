import os
import random

import pygame

pygame.mixer.init()
click_sound = pygame.mixer.Sound('data/sounds/click.ogg')
throwpowerup_sound = pygame.mixer.Sound('data/sounds/throwpowerup.wav')
throwreliase_sound = pygame.mixer.Sound('data/sounds/throwreliase.wav')
fire_damage_sound = pygame.mixer.Sound('data/sounds/flame_loop.wav')
start_game_sound = pygame.mixer.Sound('data/sounds/cow_moo.wav')
timer_tick = pygame.mixer.Sound('data/sounds/timertick.wav')
timer_tick.set_volume(0.7)
engine_sounds = ['data/sounds/engine1.wav', 'data/sounds/engine2.wav', 'data/sounds/engine3.wav']
default_powerup_sound = 'data/sounds/throwpowerup.wav'
default_release_sound = 'data/sounds/throwreliase.wav'
engine_sound = pygame.mixer.Sound('data/sounds/engine1.wav')


def powerup_sound(path):
    global throwpowerup_sound
    throwpowerup_sound = pygame.mixer.Sound(path)
    throwpowerup_sound.play()


def powerup_sound_stop():
    throwpowerup_sound.stop()


def release_sound(path):
    global throwreliase_sound
    throwreliase_sound = pygame.mixer.Sound(path)
    throwreliase_sound.play()


def play_menu_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load("data/music/menu.mp3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(loops=-1)


def play_game_music():
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load("data/music/battle.mp3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(loops=-1)


def play_loading_music():
    pygame.mixer.music.load('data/music/bg.mp3')
    pygame.mixer.music.play(-1)


def play_victory_music():
    pygame.mixer.music.load(os.path.join("data/music/victory", random.choice(victory_music)))
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1)


fired = False


def play_fire_sounds():
    global fired
    if not fired:
        fired = True
        fire_damage_sound.set_volume(0.4)
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


def play_speech(directory, text):
    speech_sound = pygame.mixer.Sound(
        os.path.join("data/sounds/speech", directory, speech_situation.get(text)).lower())
    speech_sound.play()


speeches = [{"name": "Русские", "dir": "russian"},
            {"name": "Французы", "dir": "french"},
            {"name": "Быдло", "dir": "redneck"},
            {"name": "Шотландцы", "dir": "scots"},
            {"name": "Фины", "dir": "fins"},
            {"name": "Придурки", "dir": "goofer"},
            {"name": "Ирланцы", "dir": "irish"},
            {"name": "Алкаши", "dir": "drunk"},
            {"name": "Англичане", "dir": "english"},
            {"name": "Американцы", "dir": "american"},
            ]

speech_situation = {
    "amazing": "amazing.wav",
    "boring": "boring.wav",
    "brilliant": "brilliant.wav",
    "bummer": "bummer.wav",
    "bungee": "bungee.wav",
    "byebye": "byebye.wav",
    "collect": "collect.wav",
    "comeonthen": "comeonthen.wav",
    "coward": "coward.wav",
    "dragonpunch": "dragonpunch.wav",
    "drop": "drop.wav",
    "excellent": "excellent.wav",
    "fatality": "fatality.wav",
    "fire": "fire.wav",
    "fireball": "fireball.wav",
    "firstblood": "firstblood.wav",
    "flawless": "flawless.wav",
    "goaway": "goaway.wav",
    "grenade": "grenade.wav",
    "hello": "hello.wav",
    "hurry": "hurry.wav",
    "illgetyou": "illgetyou.wav",
    "incoming": "incoming.wav",
    "jump1": "jump1.wav",
    "jump2": "jump2.wav",
    "justyouwait": "justyouwait.wav",
    "kamikaze": "kamikaze.wav",
    "laugh": "laugh.wav",
    "leavemealone": "leavemealone.wav",
    "missed": "missed.wav",
    "nooo": "nooo.wav",
    "ohdear": "ohdear.wav",
    "oinutter": "oinutter.wav",
    "ooff1": "ooff1.wav",
    "ooff2": "ooff2.wav",
    "ooff3": "ooff3.wav",
    "oops": "oops.wav",
    "orders": "orders.wav",
    "ouch": "ouch.wav",
    "ow1": "ow1.wav",
    "ow2": "ow2.wav",
    "ow3": "ow3.wav",
    "perfect": "perfect.wav",
    "revenge": "revenge.wav",
    "runaway": "runaway.wav",
    "stupid": "stupid.wav",
    "takecover": "takecover.wav",
    "traitor": "traitor.wav",
    "uh": "uh-oh.wav",
    "victory": "victory.wav",
    "watchthis": "watchthis.wav",
    "whatthe": "whatthe.wav",
    "wobble": "wobble.wav",
    "yessir": "yessir.wav",
    "youllregretthat": "youllregretthat.wav",
}

victory_music = [
    "disco king.wav",
    "egypt.wav",
    "fast-snore.wav",
    "fatsynth.wav",
    "finland.wav",
    "flush.wav",
    "france.wav",
    "funny-fall.wav",
    "funny-machine.wav",
    "funskool.wav",
    "georgia.wav",
    "germany.wav",
    "gong.wav",
    "russia.wav",
]
