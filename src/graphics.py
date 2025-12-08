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

    def draw_status_bar(self):
        status_rect = pygame.Rect(0, BOARD_SIZE * SQUARE_SIZE, WIDTH, 50)
        self.draw_gradient_rect(status_rect, STATUS_BAR, (STATUS_BAR[0] - 5, STATUS_BAR[1] - 5, STATUS_BAR[2] - 5))

        pygame.draw.line(self.screen, PANEL_ACCENT,
                         (0, BOARD_SIZE * SQUARE_SIZE),
                         (WIDTH, BOARD_SIZE * SQUARE_SIZE), 2)

        status_text = ""
        if self.game.game_over:
            if self.game.white_time <= 0:
                status_text = " Черные победили по времени!"
            elif self.game.black_time <= 0:
                status_text = " Белые победили по времени!"
            else:
                status_text = " Игра завершена!"
        elif self.game.multiple_capture:
            status_text = " Продолжайте взятие!"
        else:
            all_captures = self.game.get_all_possible_captures(self.game.current_player)
            if all_captures:
                status_text = "‼ ОБЯЗАТЕЛЬНОЕ ВЗЯТИЕ!"
            else:
                status_text = " Ожидание хода..."

        # Обрезаем текст, если он слишком длинный
        if len(status_text) > 40:
            status_text = status_text[:37] + "..."

        status_surface = self.font_small.render(status_text, True, TEXT_LIGHT)
        text_rect = status_surface.get_rect(midleft=(20, BOARD_SIZE * SQUARE_SIZE + 25))
        self.screen.blit(status_surface, text_rect)

    def draw_panel(self):
        panel_rect = pygame.Rect(BOARD_SIZE * SQUARE_SIZE, 0, 300, HEIGHT)
        self.draw_gradient_rect(panel_rect, PANEL_COLOR,
                                (PANEL_COLOR[0] - 10, PANEL_COLOR[1] - 10, PANEL_COLOR[2] - 10))

        for i in range(3):
            pygame.draw.line(self.screen,
                             (PANEL_ACCENT[0] + i * 10, PANEL_ACCENT[1] + i * 10, PANEL_ACCENT[2] + i * 10),
                             (BOARD_SIZE * SQUARE_SIZE + i, 0),
                             (BOARD_SIZE * SQUARE_SIZE + i, HEIGHT), 1)

        # Заголовок
        title = self.font_medium.render("ШАШКИ", True, ACCENT_GOLD)
        title_rect = title.get_rect(center=(BOARD_SIZE * SQUARE_SIZE + 150, 30))
        self.screen.blit(title, title_rect)

        timer_height = 100

        # Белые таймер
        white_timer_rect = pygame.Rect(BOARD_SIZE * SQUARE_SIZE + 30, 60, 240, timer_height)
        is_active = self.game.current_player == Player.WHITE and not self.game.game_over
        timer_color1 = (PANEL_ACCENT[0] + 20, PANEL_ACCENT[1] + 20, PANEL_ACCENT[2] + 20) if is_active else PANEL_ACCENT
        timer_color2 = (timer_color1[0] - 10, timer_color1[1] - 10, timer_color1[2] - 10)

        self.draw_gradient_rect(white_timer_rect, timer_color1, timer_color2)
        border_color = ACCENT_SILVER if is_active else (100, 100, 120)
        pygame.draw.rect(self.screen, border_color, white_timer_rect, 3, border_radius=12)

        time_text = self.game.format_time(self.game.white_time)
        color = ACCENT_RED if self.game.white_time < 60 and not self.game.game_over else TEXT_LIGHT
        time_surface = self.font_large.render(time_text, True, color)
        time_rect = time_surface.get_rect(center=white_timer_rect.center)
        self.screen.blit(time_surface, time_rect)

        label = self.font_small.render("БЕЛЫЕ", True, ACCENT_SILVER if is_active else TEXT_DARK)
        label_rect = label.get_rect(center=(white_timer_rect.centerx, white_timer_rect.top + 20))
        self.screen.blit(label, label_rect)

        # Черные таймер
        black_timer_rect = pygame.Rect(BOARD_SIZE * SQUARE_SIZE + 30, 60 + timer_height + 20, 240, timer_height)
        is_active = self.game.current_player == Player.BLACK and not self.game.game_over
        timer_color1 = (PANEL_ACCENT[0] + 20, PANEL_ACCENT[1] + 20, PANEL_ACCENT[2] + 20) if is_active else PANEL_ACCENT
        timer_color2 = (timer_color1[0] - 10, timer_color1[1] - 10, timer_color1[2] - 10)

        self.draw_gradient_rect(black_timer_rect, timer_color1, timer_color2)
        border_color = ACCENT_SILVER if is_active else (100, 100, 120)
        pygame.draw.rect(self.screen, border_color, black_timer_rect, 3, border_radius=12)

        time_text = self.game.format_time(self.game.black_time)
        color = ACCENT_RED if self.game.black_time < 60 and not self.game.game_over else TEXT_LIGHT
        time_surface = self.font_large.render(time_text, True, color)
        time_rect = time_surface.get_rect(center=black_timer_rect.center)
        self.screen.blit(time_surface, time_rect)

        label = self.font_small.render("ЧЕРНЫЕ", True, ACCENT_SILVER if is_active else TEXT_DARK)
        label_rect = label.get_rect(center=(black_timer_rect.centerx, black_timer_rect.top + 20))
        self.screen.blit(label, label_rect)

        # Информация о ходе
        info_y = black_timer_rect.bottom + 30

        player_text = "ХОД БЕЛЫХ" if self.game.current_player == Player.WHITE else "ХОД ЧЕРНЫХ"
        player_surface = self.font_medium.render(player_text, True,
                                                 ACCENT_SILVER if self.game.current_player == Player.WHITE else TEXT_DARK)
        player_rect = player_surface.get_rect(center=(BOARD_SIZE * SQUARE_SIZE + 150, info_y))
        self.screen.blit(player_surface, player_rect)

        # Счет шашек
        white_count = sum(1 for row in self.game.board for piece in row if piece and piece.player == Player.WHITE)
        black_count = sum(1 for row in self.game.board for piece in row if piece and piece.player == Player.BLACK)

        count_y = info_y + 35
        count_text = f" Белые: {white_count}  |  Черные: {black_count}"
        count_surface = self.font_small.render(count_text, True, TEXT_LIGHT)
        count_rect = count_surface.get_rect(center=(BOARD_SIZE * SQUARE_SIZE + 150, count_y))
        self.screen.blit(count_surface, count_rect)

        # Правила (с переносами строк)
        rules_y = count_y + 40
        rules = [
            "ПРАВИЛА:",
            "• Обязательное взятие",
            "• Множественное взятие",
            "• Дамки ходят свободно",
            "• 7 минут на партию"
        ]

        for i, rule in enumerate(rules):
            rule_surface = self.font_tiny.render(rule, True, TEXT_DARK if i == 0 else (160, 160, 180))
            rule_rect = rule_surface.get_rect(midleft=(BOARD_SIZE * SQUARE_SIZE + 30, rules_y + i * 22))
            self.screen.blit(rule_surface, rule_rect)

        # Кнопки управления
        button_y = rules_y + len(rules) * 22 + 25

        # Кнопка рестарта
        restart_rect = pygame.Rect(BOARD_SIZE * SQUARE_SIZE + 30, button_y, 240, 45)
        mouse_pos = pygame.mouse.get_pos()
        restart_hover = restart_rect.collidepoint(mouse_pos)

        restart_color1 = ACCENT_BLUE if not restart_hover else (ACCENT_BLUE[0] + 20, ACCENT_BLUE[1] + 20,
                                                                ACCENT_BLUE[2] + 20)
        restart_color2 = (restart_color1[0] - 20, restart_color1[1] - 20, restart_color1[2] - 20)

        self.draw_gradient_rect(restart_rect, restart_color1, restart_color2)
        pygame.draw.rect(self.screen, LIGHT_BLUE, restart_rect, 3, border_radius=8)

        restart_text = self.font_medium.render("НОВАЯ ИГРА", True, TEXT_LIGHT)
        restart_rect_text = restart_text.get_rect(center=restart_rect.center)
        self.screen.blit(restart_text, restart_rect_text)
        self.restart_button_rect = restart_rect

        # Кнопка выхода
        exit_rect = pygame.Rect(BOARD_SIZE * SQUARE_SIZE + 30, button_y + 60, 240, 45)
        exit_hover = exit_rect.collidepoint(mouse_pos)

        exit_color1 = (100, 50, 50) if not exit_hover else (120, 60, 60)
        exit_color2 = (exit_color1[0] - 20, exit_color1[1] - 20, exit_color1[2] - 20)

        self.draw_gradient_rect(exit_rect, exit_color1, exit_color2)
        pygame.draw.rect(self.screen, (200, 100, 100), exit_rect, 3, border_radius=8)

        exit_text = self.font_medium.render("ВЫХОД", True, TEXT_LIGHT)
        exit_rect_text = exit_text.get_rect(center=exit_rect.center)
        self.screen.blit(exit_text, exit_rect_text)
        self.exit_button_rect = exit_rect

    def draw_game_over_screen(self):
        """Отрисовка экрана окончания игры с увеличенным окном"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Более темный фон для лучшей читаемости
        self.screen.blit(overlay, (0, 0))

        # Увеличиваем размеры окна
        win_rect = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 180, 600, 360)  # Было 400x240, теперь 600x360
        self.draw_gradient_rect(win_rect, (50, 50, 70), (30, 30, 50))
        pygame.draw.rect(self.screen, ACCENT_GOLD, win_rect, 8, border_radius=20)  # Более толстая рамка

        # Заголовок победителя - увеличенный шрифт
        if self.game.winner == Player.WHITE:
            winner_text = "БЕЛЫЕ ПОБЕДИЛИ!"
            color = ACCENT_SILVER
        else:
            winner_text = "ЧЕРНЫЕ ПОБЕДИЛИ!"
            color = (100, 100, 120)

        # Заголовок с эффектом тени
        shadow_offset = 3
        shadow_text = pygame.font.Font(None, 64).render(winner_text, True, (0, 0, 0, 150))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + shadow_offset, HEIGHT // 2 - 120 + shadow_offset))
        self.screen.blit(shadow_text, shadow_rect)

        win_title = pygame.font.Font(None, 64).render(winner_text, True, ACCENT_GOLD)
        win_title_rect = win_title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120))
        self.screen.blit(win_title, win_title_rect)

        # Причина победы - улучшенное отображение
        reason = ""
        additional_info = ""

        if self.game.white_time <= 0:
            reason = "ПОБЕДА ПО ВРЕМЕНИ"
            additional_info = "У белых закончилось время"
        elif self.game.black_time <= 0:
            reason = "ПОБЕДА ПО ВРЕМЕНИ"
            additional_info = "У черных закончилось время"
        else:
            white_count = sum(1 for row in self.game.board for piece in row if piece and piece.player == Player.WHITE)
            black_count = sum(1 for row in self.game.board for piece in row if piece and piece.player == Player.BLACK)
            reason = "ПОБЕДА ПО ОЧКАМ"
            additional_info = f"Белые: {white_count} шашек  |  Черные: {black_count} шашек"

        # Основная причина
        reason_surface = pygame.font.Font(None, 36).render(reason, True, color)
        reason_rect = reason_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
        self.screen.blit(reason_surface, reason_rect)

        # Дополнительная информация
        info_surface = pygame.font.Font(None, 28).render(additional_info, True, (200, 200, 220))
        info_rect = info_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.screen.blit(info_surface, info_rect)

        # Статистика времени
        white_time_str = self.game.format_time(self.game.white_time)
        black_time_str = self.game.format_time(self.game.black_time)
        time_stats = f"Оставшееся время: Белые: {white_time_str}  |  Черные: {black_time_str}"
        time_surface = pygame.font.Font(None, 24).render(time_stats, True, (180, 180, 200))
        time_rect = time_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(time_surface, time_rect)

        # Подсказки управления - более заметные
        hint_y = HEIGHT // 2 + 70
        hints = [
            "Нажмите R для новой игры",
            "Нажмите ESC для выхода",
            "Или используйте кнопки в правой панели"
        ]

        for i, hint in enumerate(hints):
            hint_surface = pygame.font.Font(None, 24).render(hint, True, TEXT_LIGHT if i == 2 else (200, 200, 220))
            hint_rect = hint_surface.get_rect(center=(WIDTH // 2, hint_y + i * 30))

            # Подсветка последней подсказки
            if i == 2:
                hint_bg = pygame.Surface((hint_surface.get_width() + 20, hint_surface.get_height() + 10),
                                         pygame.SRCALPHA)
                hint_bg.fill((40, 40, 60, 200))
                hint_bg_rect = hint_bg.get_rect(center=(WIDTH // 2, hint_y + i * 30))
                self.screen.blit(hint_bg, hint_bg_rect)

            self.screen.blit(hint_surface, hint_rect)

        # Декоративные элементы по углам (оставляем, они не мешают тексту)
        corner_size = 30
        corners = [
            (win_rect.left + corner_size, win_rect.top + corner_size),
            (win_rect.right - corner_size, win_rect.top + corner_size),
            (win_rect.left + corner_size, win_rect.bottom - corner_size),
            (win_rect.right - corner_size, win_rect.bottom - corner_size)
        ]

        for corner_x, corner_y in corners:
            pygame.draw.circle(self.screen, ACCENT_GOLD, (corner_x, corner_y), 8)
            pygame.draw.circle(self.screen, (255, 200, 0), (corner_x, corner_y), 5)


    def draw(self):
        self.draw_board()
        self.draw_pieces()
        self.draw_status_bar()
        self.draw_panel()

        # Отрисовываем экран окончания игры поверх всего
        if self.game.game_over:
            self.draw_game_over_screen()

        pygame.display.flip()

    def get_board_position(self, pos):
        x, y = pos
        if x < 0 or x >= BOARD_SIZE * SQUARE_SIZE:
            return None
        if y < 0 or y >= BOARD_SIZE * SQUARE_SIZE:
            return None
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return row, col
        return None

    def check_button_click(self, pos):
        x, y = pos

        # Проверяем кнопку рестарта
        if hasattr(self, 'restart_button_rect') and self.restart_button_rect.collidepoint(pos):
            return "RESTART"

        # Проверяем кнопку выхода
        if hasattr(self, 'exit_button_rect') and self.exit_button_rect.collidepoint(pos):
            return "EXIT"

        return None

    def restart_game(self):
        self.game = CheckersGame()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()