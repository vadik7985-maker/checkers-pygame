"""
Модуль для графического интерфейса игры
"""

import pygame
import sys
import time
from typing import Optional, Tuple
from .constants import *
from .game_logic import CheckersGame
from .enums import Player
from .models import Piece

class CheckersGUI:
    def __init__(self):
        # Создаем окно с заголовком
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("♔ Русские Шашки - Профессиональная Версия ♚")
        self.clock = pygame.time.Clock()
        self.game = CheckersGame()

        # Иконка окна
        try:
            icon = pygame.Surface((32, 32))
            icon.fill(ACCENT_GOLD)
            pygame.draw.circle(icon, BLACK_PIECE, (16, 10), 8)
            pygame.draw.circle(icon, WHITE_PIECE, (16, 22), 8)
            pygame.display.set_icon(icon)
        except:
            pass

        # Загружаем шрифты
        try:
            self.font_large = pygame.font.Font(None, 48)
            self.font_medium = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
            self.font_tiny = pygame.font.Font(None, 18)
        except:
            self.font_large = pygame.font.SysFont('arial', 48, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 32)
            self.font_small = pygame.font.SysFont('arial', 24)
            self.font_tiny = pygame.font.SysFont('arial', 18)

        # Эффекты
        self.pulse_value = 0
        self.last_pulse_time = 0
        