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

    def draw_gradient_rect(self, rect, color1, color2, vertical=True):
        if vertical:
            for y in range(rect.height):
                ratio = y / rect.height
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                pygame.draw.line(self.screen, (r, g, b),
                                 (rect.x, rect.y + y),
                                 (rect.x + rect.width, rect.y + y))
        else:
            for x in range(rect.width):
                ratio = x / rect.width
                r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                pygame.draw.line(self.screen, (r, g, b),
                                 (rect.x + x, rect.y),
                                 (rect.x + x, rect.y + rect.height))

    def draw_board(self):
        self.screen.fill(BACKGROUND)

        # Рисуем доску
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * SQUARE_SIZE
                y = row * SQUARE_SIZE

                if (row + col) % 2 == 0:
                    cell_rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
                    self.draw_gradient_rect(cell_rect,
                                            (LIGHT_WOOD[0] + 10, LIGHT_WOOD[1] + 10, LIGHT_WOOD[2] + 10),
                                            LIGHT_WOOD)
                else:
                    cell_rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
                    self.draw_gradient_rect(cell_rect,
                                            DARK_WOOD,
                                            (DARK_WOOD[0] - 10, DARK_WOOD[1] - 10, DARK_WOOD[2] - 10))

        # Подсветка шашек, которые можно взять (обязательное взятие)
        if self.game.captured_pieces_to_highlight:
            for row, col in self.game.captured_pieces_to_highlight:
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

                # Пульсирующая обводка красным цветом
                current_time = pygame.time.get_ticks()
                pulse = (abs(pygame.math.Vector2(1, 0).rotate(current_time * 0.01).x) * 0.3 + 0.7)
                radius = SQUARE_SIZE // 2

                # Внешнее свечение
                for i in range(4, 0, -1):
                    alpha = 100 - i * 20
                    s = pygame.Surface((radius * 2 + i * 6, radius * 2 + i * 6), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*ACCENT_RED[:3], alpha),
                                       (radius + i * 3, radius + i * 3),
                                       radius + i * 3)
                    self.screen.blit(s, (center_x - radius - i * 3, center_y - radius - i * 3))

                # Основная обводка
                pygame.draw.circle(self.screen, ACCENT_RED,
                                   (center_x, center_y),
                                   radius + 2, 3)

        # Подсветка допустимых ходов
        if self.game.selected_piece:
            for move in self.game.valid_moves:
                row, col, _ = move
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

                current_time = pygame.time.get_ticks()
                if current_time - self.last_pulse_time > 16:
                    self.pulse_value = (self.pulse_value + 0.1) % (2 * 3.14159)
                    self.last_pulse_time = current_time

                pulse_size = 0.5 + 0.3 * abs(pygame.math.Vector2(1, 0).rotate(self.pulse_value * 180 / 3.14159).x)
                size = int(SQUARE_SIZE // 4 * pulse_size)

                # Внешнее свечение
                for i in range(3, 0, -1):
                    alpha = 100 - i * 25
                    s = pygame.Surface((size * 2 + i * 4, size * 2 + i * 4), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*ACCENT_GREEN[:3], alpha),
                                       (size + i * 2, size + i * 2),
                                       size + i * 2)
                    self.screen.blit(s, (center_x - size - i * 2, center_y - size - i * 2))

                # Основной круг
                pygame.draw.circle(self.screen, ACCENT_GREEN,
                                   (center_x, center_y),
                                   size)

        # Подсветка выбранной шашки
        if self.game.selected_piece:
            row, col = self.game.selected_piece
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

            pulse = (pygame.time.get_ticks() % 1000) / 1000
            border_width = 3 + int(2 * pulse)

            glow_surf = pygame.Surface((SQUARE_SIZE + 20, SQUARE_SIZE + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*ACCENT_GOLD[:3], 100),
                             (0, 0, SQUARE_SIZE + 20, SQUARE_SIZE + 20),
                             border_radius=15)
            self.screen.blit(glow_surf, (rect.x - 10, rect.y - 10))

            pygame.draw.rect(self.screen, ACCENT_GOLD, rect, border_width, border_radius=10)

    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.game.board[row][col]
                if piece:
                    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

                    selected = (self.game.selected_piece and
                                (row, col) == self.game.selected_piece)

                    piece.draw(self.screen, center_x, center_y, SQUARE_SIZE, selected)

    def draw(self):
        self.draw_board()
        self.draw_pieces()
        self.draw_status_bar()
        self.draw_panel()

        # Отрисовываем экран окончания игры поверх всего
        if self.game.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        button = self.check_button_click(event.pos)
                        if button == "RESTART":
                            self.restart_game()
                        elif button == "EXIT":
                            running = False
                        else:
                            pos = self.get_board_position(event.pos)
                            if pos:
                                self.game.handle_click(*pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            # Обновляем таймер
            self.game.update_timer()

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()