"""
Модуль для вспомогательных функций
"""

import pygame
from typing import Tuple, Dict
from .constants import *


def create_gradient_surface(width: int, height: int,
                            color1: Tuple[int, int, int],
                            color2: Tuple[int, int, int],
                            vertical: bool = True) -> pygame.Surface:
    """Создание поверхности с градиентом"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))

    return surface


def draw_text_with_shadow(surface: pygame.Surface, text: str, font: pygame.font.Font,
                          color: Tuple[int, int, int], shadow_color: Tuple[int, int, int],
                          pos: Tuple[int, int], shadow_offset: int = 2) -> None:
    """Отрисовка текста с тенью"""
    shadow_surf = font.render(text, True, shadow_color)
    text_surf = font.render(text, True, color)

    shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
    text_rect = text_surf.get_rect(center=pos)

    surface.blit(shadow_surf, shadow_rect)
    surface.blit(text_surf, text_rect)
