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

def load_fonts() -> Dict[str, pygame.font.Font]:
    """Загрузка шрифтов"""
    try:
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        font_tiny = pygame.font.Font(None, 18)
    except:
        font_large = pygame.font.SysFont('arial', 48, bold=True)
        font_medium = pygame.font.SysFont('arial', 32)
        font_small = pygame.font.SysFont('arial', 24)
        font_tiny = pygame.font.SysFont('arial', 18)
    
    return {
        'large': font_large,
        'medium': font_medium,
        'small': font_small,
        'tiny': font_tiny
    }

def create_window_icon() -> pygame.Surface:
    """Создание иконки окна"""
    icon = pygame.Surface((32, 32))
    icon.fill(ACCENT_GOLD)
    pygame.draw.circle(icon, BLACK_PIECE, (16, 10), 8)
    pygame.draw.circle(icon, WHITE_PIECE, (16, 22), 8)
    return icon