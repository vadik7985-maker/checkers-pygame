"""
Модуль для вспомогательных функций.

Этот модуль содержит утилитарные функции для графического интерфейса игры.
Все функции предназначены для работы с PyGame и улучшения визуального вида.

Функции:
    1. create_gradient_surface - создание поверхности с градиентом
    2. draw_text_with_shadow - отрисовка текста с эффектом тени
    3. load_fonts - загрузка и кэширование шрифтов
    4. create_window_icon - создание иконки окна приложения
"""

import pygame
from typing import Tuple, Dict
from .constants import *


def create_gradient_surface(width: int, height: int,
                            color1: Tuple[int, int, int],
                            color2: Tuple[int, int, int],
                            vertical: bool = True) -> pygame.Surface:
    """Создает поверхность PyGame с градиентной заливкой.

    Args:
        width (int): Ширина поверхности в пикселях
        height (int): Высота поверхности в пикселях
        color1 (Tuple[int, int, int]): Начальный цвет градиента (RGB)
        color2 (Tuple[int, int, int]): Конечный цвет градиента (RGB)
        vertical (bool): Направление градиента (True - вертикальный, False - горизонтальный)

    Returns:
        pygame.Surface: Поверхность с градиентной заливкой

    """
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
    """Отрисовывает текст с эффектом тени на указанной поверхности.

    Args:
        surface (pygame.Surface): Поверхность для отрисовки текста
        text (str): Текст для отображения
        font (pygame.font.Font): Шрифт для отрисовки текста
        color (Tuple[int, int, int]): Основной цвет текста (RGB)
        shadow_color (Tuple[int, int, int]): Цвет тени текста (RGB)
        pos (Tuple[int, int]): Позиция текста (x, y) на поверхности
        shadow_offset (int): Смещение тени в пикселях, по умолчанию 2
    """
    shadow_surf = font.render(text, True, shadow_color)
    text_surf = font.render(text, True, color)

    shadow_rect = shadow_surf.get_rect(center=(pos[0] + shadow_offset, pos[1] + shadow_offset))
    text_rect = text_surf.get_rect(center=pos)

    surface.blit(shadow_surf, shadow_rect)
    surface.blit(text_surf, text_rect)


def load_fonts() -> Dict[str, pygame.font.Font]:
    """Загружает и возвращает словарь шрифтов разных размеров.

    Returns:
        Dict[str, pygame.font.Font]: Словарь с ключами:
            - 'large': крупный шрифт (48px)
            - 'medium': средний шрифт (32px)
            - 'small': мелкий шрифт (24px)
            - 'tiny': очень мелкий шрифт (18px)

    Примечание:
        Если системный шрифт не доступен, используется шрифт Arial.
    """
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
    """Создает иконку для окна приложения.

    Returns:
        pygame.Surface: Иконка размером 32x32 пикселя

    Описание иконки:
        - Золотой фон
        - Черная шашка в верхней части
        - Белая шашка в нижней части
        - Представляет игру в шашки
    """
    icon = pygame.Surface((32, 32))
    icon.fill(ACCENT_GOLD)
    pygame.draw.circle(icon, BLACK_PIECE, (16, 10), 8)
    pygame.draw.circle(icon, WHITE_PIECE, (16, 22), 8)
    return icon