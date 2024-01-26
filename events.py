import pygame

SHOWMARKER = pygame.USEREVENT + 1021
END = pygame.USEREVENT + 1023
START = pygame.USEREVENT + 1024
LOGO1 = pygame.USEREVENT + 1025
LOGO2 = pygame.USEREVENT + 1026
LOGO3 = pygame.USEREVENT + 1027
LOGO3 = pygame.USEREVENT + 1027
TAP_FOR_START = pygame.USEREVENT + 1028
PREMOVE = pygame.USEREVENT + 1029
MOVE = pygame.USEREVENT + 1030
NEXT_TANK = pygame.USEREVENT + 1031
DAMAGE = pygame.USEREVENT + 1032
SELFDAMAGE = pygame.USEREVENT + 1033
WIN = pygame.USEREVENT + 1034
PRE_NEXT_TANK = pygame.USEREVENT + 1035

premove_event = pygame.event.Event(PREMOVE)
move_event = pygame.event.Event(MOVE)
next_tank_event = pygame.event.Event(NEXT_TANK)
damage_event = pygame.event.Event(DAMAGE)
selfdamage_event = pygame.event.Event(SELFDAMAGE)
win_event = pygame.event.Event(WIN)
pre_next_tank_event = pygame.event.Event(PRE_NEXT_TANK)
