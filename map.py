import PIL
import numpy as np
import pygame
from PIL import Image, ImageDraw
from PIL.Image import Transpose
import matplotlib.pyplot as plt
import config


class Map:
    image: Image
    mask: Image
    mask_arr: np.array

    def set_image(self, image_path: str, mask_path: str):
        self.image = Image.open(image_path).transpose(Transpose.TRANSPOSE)
        self.mask = Image.open(mask_path).convert("L").transpose(Transpose.TRANSPOSE)
        self.mask_arr = np.array(self.mask)

    def __init__(self):
        pass

    def draw_map(self, screen):
        res = Image.new("RGB", self.image.size, "BLACK")
        tmp = self.image.copy()
        tmp.putalpha(self.mask)
        res.paste(tmp, (0, 0), mask=tmp)
        res = res.convert("RGB")
        surf = pygame.surfarray.make_surface(np.array(res))
        screen.blit(surf, (0, 0))

    def remove_circle(self, y, x, radius):
        draw = ImageDraw.Draw(self.mask)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=0)
        self.mask_arr = np.array(self.mask)
        pygame.display.update()

    def check_on_ground(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.left:rect.right, rect.bottom:rect.bottom + 1])

    def check_left_ground(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.left:rect.left + 1, rect.top:rect.bottom])

    def check_right_ground(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.right:rect.right + 1, rect.top:rect.bottom])

    def check_in_ground(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.left:rect.right, rect.bottom - 1:rect.bottom])

    def can_move_right(self, rect: pygame.Rect, limit=0.4) -> bool:
        return np.mean(np.array(self.mask)[rect.right:rect.right + 1, rect.top:rect.bottom]) < limit * 255

    def can_move_left(self, rect: pygame.Rect, limit=0.4) -> bool:
        return np.mean(np.array(self.mask)[rect.left - 1:rect.left, rect.top:rect.bottom]) < limit * 255

    def check_ground_top(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.left:rect.right, rect.top: rect.top + 1])

    def check_in_ground_around(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.left:rect.right, rect.top:rect.bottom])

    def check_on_ground_around(self, rect: pygame.Rect) -> bool:
        return np.any(np.array(self.mask)[rect.left - 1:rect.right + 1, rect.top - 1:rect.bottom + 1])

    def get_tan_on_ground(self, rect: pygame.Rect) -> np.array:
        ground_slice = np.array(self.mask)[rect.left - 1:rect.right + 1, rect.top - 1:rect.bottom + 1]

        return ground_slice

    def check_block(self, x, y):
        return np.array(self.mask)[x][y] == 1

    def invert_block(self, x, y):
        np.array(self.mask)[x][y] = -np.array(self.mask)[x][y]


playmap = Map()
playmap.set_image("data/maps/lego/image.png", "data/maps/lego/mask.png")
