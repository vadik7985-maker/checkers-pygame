"""
Модуль для хранения классов данных.

Этот модуль содержит dataclass-классы, представляющие основные сущности игры.
Используется для типобезопасного хранения данных о шашках, ходах и состоянии игры.

Классы:
    1. Piece - класс шашки с методами отрисовки
    2. Move - класс хода с информацией о взятиях
    3. GameState - класс состояния игры
"""

import pygame
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Any
from .constants import PIECE_SHADOW, ACCENT_GOLD
from .enums import PieceType, Player


@dataclass
class Piece:
    """Класс, представляющий шашку на игровой доске.

    Attributes:
        player (Player): Игрок, которому принадлежит шашка (WHITE или BLACK)
        type (PieceType): Тип шашки (MAN или KING), по умолчанию MAN
        last_move_time (float): Время последнего хода этой шашкой, по умолчанию 0.0
    """
    player: Player
    type: PieceType = PieceType.MAN
    last_move_time: float = 0.0

    def draw(self, screen, x, y, size, selected=False):
        """Отрисовывает шашку на экране.

        Args:
            screen: Поверхность PyGame для отрисовки
            x (int): X-координата центра шашки
            y (int): Y-координата центра шашки
            size (int): Размер шашки в пикселях
            selected (bool): Флаг выделения шашки, по умолчанию False
        """
        radius = size // 2 - 5

        # Тень
        shadow_offset = 3
        pygame.draw.circle(screen, PIECE_SHADOW,
                           (x + shadow_offset, y + shadow_offset),
                           radius + 2)

        # Основной цвет с градиентом
        if self.player == Player.WHITE:
            colors = [
                (255, 255, 255),
                (240, 240, 250),
                (220, 220, 235),
                (200, 200, 220)
            ]
        else:
            colors = [
                (80, 80, 100),
                (60, 60, 80),
                (45, 45, 60),
                (30, 30, 45)
            ]

        # Градиентный круг
        for i in range(4):
            current_radius = radius - i * 2
            if current_radius > 0:
                pygame.draw.circle(screen, colors[i], (x, y), current_radius)

        # Блик
        highlight_radius = radius // 3
        highlight_x = x - radius // 3
        highlight_y = y - radius // 3
        pygame.draw.circle(screen, (255, 255, 255, 150) if self.player == Player.WHITE else (150, 150, 170, 150),
                           (highlight_x, highlight_y), highlight_radius)

        # Подсветка если выбрана
        if selected:
            pulse = (pygame.time.get_ticks() % 1000) / 1000
            glow_size = int(5 + 2 * pulse)
            s = pygame.Surface((radius * 2 + glow_size * 2, radius * 2 + glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*ACCENT_GOLD[:3], 150),
                               (radius + glow_size, radius + glow_size),
                               radius + glow_size)
            screen.blit(s, (x - radius - glow_size, y - radius - glow_size))

        # Корона для дамки
        if self.type == PieceType.KING:
            crown_size = radius // 2
            pygame.draw.circle(screen, ACCENT_GOLD, (x, y), crown_size + 2)

            points = []
            for i in range(5):
                angle = i * 72
                px = x + int(crown_size * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).x)
                py = y + int(crown_size * 0.8 * pygame.math.Vector2(1, 0).rotate(angle).y)
                points.append((px, py))

            pygame.draw.polygon(screen, ACCENT_GOLD, points)
            pygame.draw.polygon(screen, (200, 170, 0), points, 2)

            pygame.draw.circle(screen, (255, 230, 50), (x, y), crown_size // 2)


@dataclass
class Move:
    """Класс, представляющий ход в игре.

    Attributes:
        from_pos (Tuple[int, int]): Начальная позиция шашки (ряд, столбец)
        to_pos (Tuple[int, int]): Конечная позиция шашки (ряд, столбец)
        captured_pieces (List[Tuple[int, int]]): Список взятых шашек, по умолчанию пустой
        piece (Optional[Any]): Ссылка на объект шашки, по умолчанию None
        turn_start_time (float): Время начала хода, по умолчанию 0.0
    """
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    captured_pieces: List[Tuple[int, int]] = field(default_factory=list)
    piece: Optional[Any] = None
    turn_start_time: float = 0.0


@dataclass
class GameState:
    """Класс, представляющий состояние игры.

    Attributes:
        board (List[List[Optional[Piece]]]): Игровая доска 8x8
        current_player (Player): Текущий игрок
        selected_piece (Optional[Tuple[int, int]]): Выбранная шашка
        valid_moves (List[Tuple[int, int, List[Tuple[int, int]]]]): Допустимые ходы
        game_over (bool): Флаг окончания игры
        winner (Optional[Player]): Победитель игры
        white_time (float): Оставшееся время белых
        black_time (float): Оставшееся время черных
        multiple_capture (bool): Флаг множественного взятия
        captured_pieces_to_highlight (List[Tuple[int, int]]): Шашки для подсветки
        move_history (List[Move]): История ходов
    """
    board: List[List[Optional[Piece]]]
    current_player: Player
    selected_piece: Optional[Tuple[int, int]]
    valid_moves: List[Tuple[int, int, List[Tuple[int, int]]]]
    game_over: bool
    winner: Optional[Player]
    white_time: float
    black_time: float
    multiple_capture: bool
    captured_pieces_to_highlight: List[Tuple[int, int]]
    move_history: List[Move]