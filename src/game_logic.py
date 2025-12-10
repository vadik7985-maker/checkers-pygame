"""
Модуль для логики игры в шашки.

Содержит основной класс CheckersGame, реализующий правила русских шашек.
Обеспечивает игровую логику, проверку ходов, управление временем и определение победителя.

Основные возможности:
    1. Полная реализация правил русских шашек
    2. Обязательное взятие шашек противника
    3. Множественное взятие (несколько шашек за один ход)
    4. Превращение в дамку при достижении противоположного края
    5. Таймер на 7 минут для каждого игрока
    6. Автоматическое сохранение результатов в базу данных
    7. Подсветка обязательных взятий
"""

import time
from typing import List, Tuple, Optional, Set
from .constants import BOARD_SIZE, INITIAL_TIME_SECONDS
from .enums import PieceType, Player
from .models import Piece
from .database import db_manager  # Импортируем менеджер базы данных


class CheckersGame:
    """Основной класс, управляющий логикой игры в шашки.

    Attributes:
        board (List[List[Optional[Piece]]]): Игровая доска 8x8
        current_player (Player): Текущий игрок (WHITE или BLACK)
        selected_piece (Optional[Tuple[int, int]]): Выбранная шашка (ряд, столбец)
        valid_moves (List[Tuple]): Допустимые ходы для выбранной шашки
        game_over (bool): Флаг окончания игры
        winner (Optional[Player]): Победитель игры
        white_time (float): Оставшееся время белых в секундах
        black_time (float): Оставшееся время черных в секундах
        last_time_update (float): Время последнего обновления таймера
        multiple_capture (bool): Флаг множественного взятия
        captured_pieces_to_highlight (List[Tuple[int, int]]): Шашки для подсветки
        move_history (List[Dict]): История всех ходов
        game_start_time (float): Время начала игры
        game_saved (bool): Флаг сохранения результата игры
    """

    def __init__(self):
        """Инициализирует новую игру в шашки.

        Создает доску 8x8, расставляет шашки, устанавливает таймеры
        и настраивает начальное состояние игры.
        """
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = Player.WHITE  # белые ходят первыми
        self.selected_piece = None  # пока нет выбранной шашки
        self.valid_moves = []  # допустимые ходы
        self.game_over = False  # игра не окончена
        self.winner = None  # победитель еще не определен
        self.white_time = INITIAL_TIME_SECONDS  # начальное время белых
        self.black_time = INITIAL_TIME_SECONDS  # начальное время черных
        self.last_time_update = time.time()  # время последнего обновления таймера
        self.multiple_capture = False  # нет множественного взятия
        self.captured_pieces_to_highlight = []  # нет шашек для подсветки
        self.setup_board()  # расстановка шашек на доске
        self.move_history = []  # история ходов
        self.game_start_time = time.time()  # время начала игры для статистики
        self.game_saved = False  # игра еще не сохранена в БД

    def setup_board(self):
        """Расставляет шашки на доске в начальные позиции согласно правилам русских шашек.

        Черные шашки занимают первые 3 ряда (0-2), белые - последние 3 ряда (5-7).
        Шашки размещаются только на темных клетках ((row + col) % 2 == 1).
        """
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
        """Обновляет таймеры игроков на основе прошедшего времени.

        Уменьшает время текущего игрока. Если время истекает,
        завершает игру и сохраняет результат.
        """
        current_time = time.time()
        time_passed = current_time - self.last_time_update

        if not self.game_over:
            if self.current_player == Player.WHITE:
                self.white_time -= time_passed
                if self.white_time <= 0:
                    self.white_time = 0
                    self.game_over = True
                    self.winner = Player.BLACK
                    self.save_game_result()  # Сохраняем результат при окончании по времени
            else:
                self.black_time -= time_passed
                if self.black_time <= 0:
                    self.black_time = 0
                    self.game_over = True
                    self.winner = Player.WHITE
                    self.save_game_result()  # Сохраняем результат при окончании по времени

        self.last_time_update = current_time

    def format_time(self, seconds):
        """Форматирует время в секундах в строку формата MM:SS.

        Args:
            seconds (float): Время в секундах

        Returns:
            str: Отформатированное время (например, "05:30")
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def get_piece(self, row, col):
        """Возвращает шашку на указанной позиции доски.

        Args:
            row (int): Номер ряда (0-7)
            col (int): Номер столбца (0-7)

        Returns:
            Optional[Piece]: Шашка на позиции или None, если клетка пуста
        """
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return self.board[row][col]
        return None

    def get_all_possible_captures(self, player: Player):
        """Находит все возможные взятия для всех шашек указанного игрока.

        Args:
            player (Player): Игрок (WHITE или BLACK)

        Returns:
            List[Tuple]: Список всех возможных взятий в формате
                        (from_row, from_col, to_row, to_col, captured)
        """
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
        """Находит все возможные взятия для конкретной шашки с рекурсией для множественного взятия.

        Args:
            row (int): Ряд шашки
            col (int): Столбец шашки
            piece (Piece): Объект шашки
            captured_so_far (List[Tuple[int, int]]): Уже взятые шашки в этом ходе
            visited (set): Посещенные состояния для предотвращения циклов

        Returns:
            List[Tuple]: Список возможных взятий в формате (target_row, target_col, captured)
        """
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
        """Получает простые ходы для шашки (без взятия).

        Args:
            row (int): Ряд шашки
            col (int): Столбец шашки
            piece (Piece): Объект шашки

        Returns:
            List[Tuple[int, int]]: Список возможных позиций для хода
        """
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
        """Получает допустимые ходы для выбранной шашки с учетом правил обязательного взятия.

        Args:
            row (int): Ряд шашки
            col (int): Столбец шашки

        Returns:
            List[Tuple]: Список допустимых ходов в формате (target_row, target_col, captured)
        """
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
        """Перемещает шашку на указанную позицию, выполняя взятия если необходимо.

        Args:
            from_row (int): Исходный ряд
            from_col (int): Исходный столбец
            to_row (int): Целевой ряд
            to_col (int): Целевой столбец

        Returns:
            bool: True если ход выполнен успешно, False в противном случае
        """
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
        """Проверяет условия окончания игры и определяет победителя.

        Игра заканчивается если:
        1. У одного из игроков не осталось шашек
        2. У текущего игрока нет допустимых ходов
        3. Время одного из игроков истекло (проверяется в update_timer)

        Автоматически сохраняет результат игры при завершении.
        """
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
            self.save_game_result()  # Сохраняем результат
        elif black_pieces == 0 or (self.current_player == Player.BLACK and not current_player_has_moves):
            self.game_over = True
            self.winner = Player.WHITE
            self.save_game_result()  # Сохраняем результат

    def save_game_result(self):
        """Сохраняет результат игры в базу данных.

        Собирает статистику игры и сохраняет ее через DatabaseManager.

        Returns:
            bool: True если сохранение успешно, False в противном случае
        """
        if not self.game_over or self.game_saved:
            return False

        self.game_saved = True

        # Подсчитываем оставшиеся шашки
        white_pieces = 0
        black_pieces = 0
        white_queens = 0
        black_queens = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.get_piece(row, col)
                if piece:
                    if piece.player == Player.WHITE:
                        white_pieces += 1
                        if piece.type == PieceType.KING:
                            white_queens += 1
                    else:
                        black_pieces += 1
                        if piece.type == PieceType.KING:
                            black_queens += 1

        # Определяем победителя
        winner = "white" if self.winner == Player.WHITE else "black"

        # Подсчитываем общее количество ходов
        total_moves = len(self.move_history)

        # Вычисляем продолжительность игры
        game_duration_seconds = time.time() - self.game_start_time
        game_duration_str = f"{int(game_duration_seconds // 60)}:{int(game_duration_seconds % 60):02d}"

        # Дополнительная информация
        additional_info = {
            "white_queens": white_queens,
            "black_queens": black_queens,
            "total_captures": sum(len(move['captured']) for move in self.move_history),
            "game_duration_seconds": game_duration_seconds,
            "move_history_summary": [
                {
                    "from": move['from'],
                    "to": move['to'],
                    "captured_count": len(move['captured']),
                    "piece_type": "king" if move['piece'].type == PieceType.KING else "man"
                }
                for move in self.move_history[-20:]  # Последние 20 ходов
            ]
        }

        # Сохраняем в базу данных через db_manager
        try:
            result = db_manager.save_game_result(
                winner=winner,
                white_pieces=white_pieces,
                black_pieces=black_pieces,
                white_time=self.white_time,
                black_time=self.black_time,
                total_moves=total_moves,
                game_duration=game_duration_str,
                additional_info=additional_info
            )

            if result:
                print("Результат игры успешно сохранен в базу данных")
            else:
                print("Не удалось сохранить результат игры в базу данных")

            return result

        except Exception as e:
            print(f"Ошибка при сохранении результата: {e}")
            return False

    def handle_click(self, row, col):
        """Обрабатывает клик мыши на игровой доске.

        Args:
            row (int): Ряд клетки
            col (int): Столбец клетки

        Логика обработки:
        1. Если игра окончена - игнорирует клик
        2. Если шашка выбрана - пытается сделать ход
        3. Если шашка не выбрана - выбирает шашку текущего игрока
        4. Учитывает правила обязательного взятия
        """
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