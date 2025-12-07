"""
Модуль для логики игры в шашки
"""

import time
from typing import List, Tuple, Optional, Set
from .constants import BOARD_SIZE, INITIAL_TIME_SECONDS
from .enums import PieceType, Player
from .models import Piece

class CheckersGame:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = Player.WHITE
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.white_time = INITIAL_TIME_SECONDS
        self.black_time = INITIAL_TIME_SECONDS
        self.last_time_update = time.time()
        self.multiple_capture = False
        self.captured_pieces_to_highlight = []
        self.setup_board()
        self.move_history = []

    def setup_board(self):
        # Расставляем черные шашки (сверху)
        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece(Player.BLACK)

        # Расставляем белые шашки (снизу)
        for row in range(5, BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    self.board[row][col] = Piece(Player.WHITE)

    def update_timer(self):
        current_time = time.time()
        time_passed = current_time - self.last_time_update

        if not self.game_over:
            if self.current_player == Player.WHITE:
                self.white_time -= time_passed
                if self.white_time <= 0:
                    self.white_time = 0
                    self.game_over = True
                    self.winner = Player.BLACK
            else:
                self.black_time -= time_passed
                if self.black_time <= 0:
                    self.black_time = 0
                    self.game_over = True
                    self.winner = Player.WHITE

        self.last_time_update = current_time

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_piece(self, row, col):
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def get_all_possible_captures(self, player: Player):
        """Получить все возможные взятия для всех шашек игрока"""
        all_captures = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece and piece.player == player:
                    captures = self.get_captures_for_piece(row, col, piece)
                    for target_row, target_col, captured in captures:
                        all_captures.append((row, col, target_row, target_col, captured))

        return all_captures

    def get_captures_for_piece(self, row: int, col: int, piece: Piece,
                               captured_so_far: List[Tuple[int, int]] = None,
                               visited: set = None):
        """Найти все возможные взятия для шашки с рекурсией"""
        if captured_so_far is None:
            captured_so_far = []
        if visited is None:
            visited = set()

        captures = []
        visited_key = (row, col, tuple(sorted(captured_so_far)))
        if visited_key in visited:
            return captures
        visited.add(visited_key)

        if piece.type == PieceType.KING:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for dr, dc in directions:
                current_row, current_col = row, col
                enemy_found = False
                enemy_row, enemy_col = -1, -1

                # Ищем вражескую шашку в этом направлении
                while True:
                    current_row += dr
                    current_col += dc

                    if not (0 <= current_row < BOARD_SIZE and 0 <= current_col < BOARD_SIZE):
                        break

                    target = self.get_piece(current_row, current_col)

                    if target:
                        if target.player != piece.player and (current_row, current_col) not in captured_so_far:
                            enemy_found = True
                            enemy_row, enemy_col = current_row, current_col
                            break
                        else:
                            break

                if enemy_found:
                    # Ищем пустую клетку за врагом
                    landing_row, landing_col = enemy_row + dr, enemy_col + dc
                    while 0 <= landing_row < BOARD_SIZE and 0 <= landing_col < BOARD_SIZE:
                        if not self.get_piece(landing_row, landing_col):
                            # Сохраняем состояние доски
                            original_board = [[self.board[r][c] for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]

                            # Временно делаем взятие
                            self.board[landing_row][landing_col] = piece
                            self.board[row][col] = None
                            self.board[enemy_row][enemy_col] = None

                            # Ищем дальнейшие взятия
                            new_captured = captured_so_far + [(enemy_row, enemy_col)]
                            further_captures = self.get_captures_for_piece(landing_row, landing_col, piece,
                                                                           new_captured, visited)

                            # Восстанавливаем доску
                            self.board = original_board

                            if further_captures:
                                for fr, fc, fc_captured in further_captures:
                                    captures.append((fr, fc, fc_captured))
                            else:
                                captures.append((landing_row, landing_col, new_captured))

                            landing_row += dr
                            landing_col += dc
                        else:
                            break
        else:  # Простая шашка
            # Простая шашка может бить ВПЕРЕД и НАЗАД
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for dr, dc in directions:
                enemy_row, enemy_col = row + dr, col + dc
                jump_row, jump_col = row + dr * 2, col + dc * 2

                if (0 <= enemy_row < BOARD_SIZE and 0 <= enemy_col < BOARD_SIZE and
                        0 <= jump_row < BOARD_SIZE and 0 <= jump_col < BOARD_SIZE):

                    enemy_piece = self.get_piece(enemy_row, enemy_col)
                    jump_piece = self.get_piece(jump_row, jump_col)

                    if (enemy_piece and enemy_piece.player != piece.player and
                            not jump_piece and (enemy_row, enemy_col) not in captured_so_far):

                        # Сохраняем состояние доски
                        original_board = [[self.board[r][c] for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]

                        # Временно делаем взятие
                        self.board[jump_row][jump_col] = piece
                        self.board[row][col] = None
                        self.board[enemy_row][enemy_col] = None

                        # Ищем дальнейшие взятия
                        new_captured = captured_so_far + [(enemy_row, enemy_col)]
                        further_captures = self.get_captures_for_piece(jump_row, jump_col, piece,
                                                                       new_captured, visited)

                        # Восстанавливаем доску
                        self.board = original_board

                        if further_captures:
                            for fr, fc, fc_captured in further_captures:
                                captures.append((fr, fc, fc_captured))
                        else:
                            captures.append((jump_row, jump_col, new_captured))

        return captures

    def get_simple_moves_for_piece(self, row: int, col: int, piece: Piece):
        """Получить простые ходы для шашки (без взятия)"""
        moves = []

        if piece.type == PieceType.KING:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc

                while 0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE:
                    if not self.get_piece(new_row, new_col):
                        moves.append((new_row, new_col))
                        new_row += dr
                        new_col += dc
                    else:
                        break
        else:
            # Простая шашка ходит только вперед (но может бить назад!)
            if piece.player == Player.WHITE:
                directions = [(-1, -1), (-1, 1)]  # Вперед для белых (вверх)
            else:
                directions = [(1, -1), (1, 1)]  # Вперед для черных (вниз)

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < BOARD_SIZE and 0 <= new_col < BOARD_SIZE and
                        not self.get_piece(new_row, new_col)):
                    moves.append((new_row, new_col))

        return moves

    def get_valid_moves(self, row, col):
        """Получить допустимые ходы для выбранной шашки"""
        piece = self.get_piece(row, col)
        if not piece or piece.player != self.current_player:
            return []

        # Проверяем, есть ли обязательные взятия у всего игрока
        all_captures = self.get_all_possible_captures(self.current_player)

        if all_captures:
            # Находим максимальное количество взятий
            max_captures = 0
            for _, _, _, _, captured in all_captures:
                if len(captured) > max_captures:
                    max_captures = len(captured)

            # Фильтруем только ходы с максимальным количеством взятий
            best_captures = []
            for fr, fc, tr, tc, captured in all_captures:
                if fr == row and fc == col and len(captured) == max_captures:
                    # Собираем шашки, которые будут взяты
                    captured_coords = captured
                    best_captures.append((tr, tc, captured_coords))

            if best_captures:
                # Сохраняем шашки для подсветки
                self.captured_pieces_to_highlight = []
                for _, _, captured in best_captures:
                    for r, c in captured:
                        if (r, c) not in self.captured_pieces_to_highlight:
                            self.captured_pieces_to_highlight.append((r, c))
                return best_captures
            else:
                return []
        else:
            # Нет взятий - показываем простые ходы
            self.captured_pieces_to_highlight = []
            simple_moves = self.get_simple_moves_for_piece(row, col, piece)
            return [(mr, mc, []) for mr, mc in simple_moves]
   
    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]

        # Проверяем, является ли ход допустимым
        valid_move = False
        captured_pieces = []

        for move in self.valid_moves:
            if move[0] == to_row and move[1] == to_col:
                valid_move = True
                captured_pieces = move[2]
                break

        if not valid_move:
            return False

        # Сохраняем ход в историю
        self.move_history.append({
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'captured': captured_pieces,
            'piece': piece
        })

        # Выполняем ход
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # Удаляем все взятые шашки
        for r, c in captured_pieces:
            self.board[r][c] = None

        # Проверяем превращение в дамку
        if piece.type == PieceType.MAN:
            if piece.player == Player.WHITE and to_row == 0:
                piece.type = PieceType.KING
            elif piece.player == Player.BLACK and to_row == BOARD_SIZE - 1:
                piece.type = PieceType.KING

        # Проверяем возможность дальнейшего взятия
        if captured_pieces:
            further_captures = self.get_captures_for_piece(to_row, to_col, piece)

            # Фильтруем только те взятия, которые берут новые шашки
            valid_further = []
            for fr, fc, capt in further_captures:
                # Проверяем, что это новые шашки (не те, что уже взяты)
                new_captures = [c for c in capt if c not in captured_pieces]
                if new_captures:
                    valid_further.append((fr, fc, capt))

            if valid_further:
                # Находим максимальное количество дополнительных взятий
                max_further = max(len(capt) for _, _, capt in valid_further)
                best_further = [(fr, fc, capt) for fr, fc, capt in valid_further if len(capt) == max_further]

                if best_further:
                    # Продолжаем множественное взятие
                    self.multiple_capture = True
                    self.selected_piece = (to_row, to_col)
                    self.valid_moves = best_further
                    # Обновляем подсветку шашек для взятия
                    self.captured_pieces_to_highlight = []
                    for _, _, captured in best_further:
                        for r, c in captured:
                            if (r, c) not in self.captured_pieces_to_highlight:
                                self.captured_pieces_to_highlight.append((r, c))
                    return True

        # Если множественное взятие закончено или его не было
        self.multiple_capture = False
        self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE
        self.selected_piece = None
        self.valid_moves = []
        self.captured_pieces_to_highlight = []

        # Проверка на конец игры
        self.check_game_over()

        return True

    def check_game_over(self):
        white_pieces = 0
        black_pieces = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    if piece.player == Player.WHITE:
                        white_pieces += 1
                    else:
                        black_pieces += 1

        # Проверяем наличие ходов у текущего игрока
        current_player_has_moves = False
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece and piece.player == self.current_player:
                    if self.get_valid_moves(row, col):
                        current_player_has_moves = True
                        break
            if current_player_has_moves:
                break

        if white_pieces == 0 or (self.current_player == Player.WHITE and not current_player_has_moves):
            self.game_over = True
            self.winner = Player.BLACK
        elif black_pieces == 0 or (self.current_player == Player.BLACK and not current_player_has_moves):
            self.game_over = True
            self.winner = Player.WHITE

    def handle_click(self, row, col):
        if self.game_over:
            return

        piece = self.get_piece(row, col)

        if self.selected_piece:
            # Пытаемся сделать ход
            if self.move_piece(self.selected_piece[0], self.selected_piece[1], row, col):
                return
            else:
                # Если ход не удался, снимаем выделение
                self.selected_piece = None
                self.valid_moves = []
                self.captured_pieces_to_highlight = []

        # Проверяем, есть ли обязательные взятия у текущего игрока
        all_captures = self.get_all_possible_captures(self.current_player)

        if all_captures:
            # Есть обязательные взятия - можно выбрать только шашки, которые могут бить
            if piece and piece.player == self.current_player:
                # Проверяем, может ли эта шашка бить
                piece_captures = []
                for fr, fc, tr, tc, captured in all_captures:
                    if fr == row and fc == col:
                        piece_captures.append((tr, tc, captured))

                if piece_captures:
                    self.selected_piece = (row, col)
                    # Находим максимальное количество взятий
                    max_captures = 0
                    for _, _, captured in piece_captures:
                        if len(captured) > max_captures:
                            max_captures = len(captured)

                    # Выбираем только ходы с максимальным количеством взятий
                    best_moves = []
                    for tr, tc, captured in piece_captures:
                        if len(captured) == max_captures:
                            best_moves.append((tr, tc, captured))

                    self.valid_moves = best_moves
                    # Сохраняем шашки для подсветки
                    self.captured_pieces_to_highlight = []
                    for _, _, captured in best_moves:
                        for r, c in captured:
                            if (r, c) not in self.captured_pieces_to_highlight:
                                self.captured_pieces_to_highlight.append((r, c))
        else:
            # Нет обязательных взятий - можно выбрать любую свою шашку
            if piece and piece.player == self.current_player:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
