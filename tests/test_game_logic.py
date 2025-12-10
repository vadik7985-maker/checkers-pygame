import unittest
import time
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import List, Optional, Tuple

# Добавляем путь к родительской директории для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Импортируем классы из вашего модуля
# Теперь импортируем из src
from src.game_logic import CheckersGame
from src.constants import BOARD_SIZE, INITIAL_TIME_SECONDS
from src.enums import PieceType, Player
from src.models import Piece


class TestCheckersGameInitialization(unittest.TestCase):
    """Тесты инициализации игры"""

    def test_game_initialization(self):
        """Тест корректной инициализации игры"""
        game = CheckersGame()

        # Проверяем начальные атрибуты
        self.assertEqual(game.current_player, Player.WHITE)
        self.assertIsNone(game.selected_piece)
        self.assertEqual(game.valid_moves, [])
        self.assertFalse(game.game_over)
        self.assertIsNone(game.winner)
        # INITIAL_TIME_SECONDS = 7 * 60 = 420
        self.assertEqual(game.white_time, 420.0)
        self.assertEqual(game.black_time, 420.0)
        self.assertFalse(game.multiple_capture)
        self.assertEqual(game.captured_pieces_to_highlight, [])
        self.assertEqual(game.move_history, [])
        self.assertFalse(game.game_saved)

    def test_board_size(self):
        """Тест размера доски"""
        game = CheckersGame()
        self.assertEqual(len(game.board), BOARD_SIZE)
        self.assertEqual(len(game.board[0]), BOARD_SIZE)

    def test_initial_piece_placement(self):
        """Тест начальной расстановки шашек"""
        game = CheckersGame()

        # Считаем шашки
        white_count = 0
        black_count = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = game.get_piece(row, col)
                if piece:
                    if piece.player == Player.WHITE:
                        white_count += 1
                    else:
                        black_count += 1

        # Должно быть по 12 шашек у каждого игрока
        self.assertEqual(white_count, 12)
        self.assertEqual(black_count, 12)

    def test_piece_types_initial(self):
        """Тест типов шашек при инициализации"""
        game = CheckersGame()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = game.get_piece(row, col)
                if piece:
                    # Все начальные шашки должны быть обычными
                    self.assertEqual(piece.type, PieceType.MAN)


class TestBoardOperations(unittest.TestCase):
    """Тесты операций с доской"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_get_piece_valid(self):
        """Тест получения шашки с корректными координатами"""
        # В стандартной расстановке шашки есть только на темных клетках (row + col) % 2 == 1
        # Проверяем несколько возможных позиций для белых шашек
        white_positions = [(5, 1), (5, 3), (5, 5), (5, 7), (6, 0), (6, 2), (6, 4), (6, 6), (7, 1), (7, 3), (7, 5),
                           (7, 7)]

        found_piece = False
        for row, col in white_positions:
            piece = self.game.get_piece(row, col)
            if piece:
                self.assertEqual(piece.player, Player.WHITE)
                found_piece = True
                break

        self.assertTrue(found_piece, "Должна быть найдена хотя бы одна белая шашка")

    def test_get_piece_out_of_bounds(self):
        """Тест получения шашки за пределами доски"""
        self.assertIsNone(self.game.get_piece(-1, 0))
        self.assertIsNone(self.game.get_piece(8, 0))
        self.assertIsNone(self.game.get_piece(0, -1))
        self.assertIsNone(self.game.get_piece(0, 8))

    def test_empty_cells(self):
        """Тест пустых клеток на доске"""
        # Клетка (0, 0) должна быть пустой (светлые клетки не используются)
        self.assertIsNone(self.game.get_piece(0, 0))
        # Клетка (1, 0) тоже должна быть пустой (светлая)
        self.assertIsNone(self.game.get_piece(1, 0))
        # Проверяем, что клетка (0, 1) имеет черную шашку
        self.assertIsNotNone(self.game.get_piece(0, 1))


class TestTimerOperations(unittest.TestCase):
    """Тесты операций с таймером"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_format_time(self):
        """Тест форматирования времени"""
        self.assertEqual(self.game.format_time(0), "00:00")
        self.assertEqual(self.game.format_time(30), "00:30")
        self.assertEqual(self.game.format_time(60), "01:00")
        self.assertEqual(self.game.format_time(125), "02:05")
        self.assertEqual(self.game.format_time(3600), "60:00")

    @patch('time.time')
    def test_update_timer_normal(self, mock_time):
        """Тест обновления таймера в нормальных условиях"""
        # Настраиваем мок времени
        mock_time.side_effect = [1000.0, 1010.0]  # Прошло 10 секунд

        # Сохраняем начальное время (должно быть 420.0)
        initial_time = self.game.white_time
        self.assertEqual(initial_time, 420.0)

        # Обновляем last_time_update чтобы оно соответствовало первому значению мока
        self.game.last_time_update = 1000.0

        self.game.update_timer()

        # Время белых должно уменьшиться на 10 секунд
        self.assertAlmostEqual(self.game.white_time, initial_time - 10.0)

    @patch('time.time')
    @patch.object(CheckersGame, 'save_game_result')
    def test_update_timer_timeout(self, mock_save, mock_time):
        """Тест окончания времени у игрока"""
        # Настраиваем мок времени для истечения времени белых
        # Начальное время белых = 420 сек
        mock_time.side_effect = [0.0, 421.0]  # Прошло 421 секунда

        self.game.last_time_update = 0.0
        self.game.update_timer()

        # Игра должна завершиться
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, Player.BLACK)
        self.assertEqual(self.game.white_time, 0)
        mock_save.assert_called_once()

    def test_time_does_not_go_negative(self):
        """Тест, что время не становится отрицательным"""
        # Используем patch для time.time чтобы контролировать прошедшее время
        with patch('time.time') as mock_time:
            mock_time.side_effect = [0.0, 10.0]  # Прошло 10 секунд
            self.game.white_time = 5.0
            self.game.last_time_update = 0.0

            self.game.update_timer()

            self.assertEqual(self.game.white_time, 0)


class TestMoveValidation(unittest.TestCase):
    """Тесты валидации ходов"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_get_simple_moves_for_white_man(self):
        """Тест получения простых ходов для белой простой шашки"""
        # Создаем тестовую доску с белой шашкой в центре
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        white_piece = Piece(Player.WHITE)
        self.game.board[4][4] = white_piece

        moves = self.game.get_simple_moves_for_piece(4, 4, white_piece)

        # Белая шашка может ходить вперед (вверх) по диагонали
        expected_moves = [(3, 3), (3, 5)]
        self.assertEqual(set(moves), set(expected_moves))

    def test_get_simple_moves_for_black_man(self):
        """Тест получения простых ходов для черной простой шашки"""
        # Создаем тестовую доску с черной шашкой в центре
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        black_piece = Piece(Player.BLACK)
        self.game.board[3][3] = black_piece

        moves = self.game.get_simple_moves_for_piece(3, 3, black_piece)

        # Черная шашка может ходить вперед (вниз) по диагонали
        expected_moves = [(4, 2), (4, 4)]
        self.assertEqual(set(moves), set(expected_moves))

    def test_get_simple_moves_for_king(self):
        """Тест получения простых ходов для дамки"""
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        king_piece = Piece(Player.WHITE)
        king_piece.type = PieceType.KING
        self.game.board[4][4] = king_piece

        moves = self.game.get_simple_moves_for_piece(4, 4, king_piece)

        # Дамка может ходить по всем диагоналям до конца доски или до препятствия
        # Проверяем, что есть ходы во всех направлениях
        # В данном случае, доска пустая, поэтому должно быть много ходов
        self.assertGreater(len(moves), 10)  # Проверяем, что есть ходы


class TestCaptureLogic(unittest.TestCase):
    """Тесты логики взятия"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_simple_capture(self):
        """Тест простого взятия"""
        # Создаем тестовую доску
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка в позиции (4, 4)
        white_piece = Piece(Player.WHITE)
        self.game.board[4][4] = white_piece

        # Черная шашка в позиции (3, 3)
        black_piece = Piece(Player.BLACK)
        self.game.board[3][3] = black_piece

        # Клетка (2, 2) пустая
        self.game.board[2][2] = None

        # Получаем взятия для белой шашки
        captures = self.game.get_captures_for_piece(4, 4, white_piece)

        # Должно быть возможно взятие черной шашки
        capture_found = False
        for _, _, captured in captures:
            if captured == [(3, 3)]:
                capture_found = True
                break
        self.assertTrue(capture_found, "Должно быть возможно взятие черной шашки")

    def test_multiple_capture(self):
        """Тест множественного взятия"""
        # Создаем тестовую доску для множественного взятия
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка в позиции (5, 5)
        white_piece = Piece(Player.WHITE)
        self.game.board[5][5] = white_piece

        # Черные шашки в позициях (4, 4) и (2, 2)
        self.game.board[4][4] = Piece(Player.BLACK)
        self.game.board[2][2] = Piece(Player.BLACK)

        # Пустые клетки для прыжков
        self.game.board[3][3] = None
        self.game.board[1][1] = None

        captures = self.game.get_captures_for_piece(5, 5, white_piece)

        # Ищем взятия, которые захватывают обе черные шашки
        double_captures = [captured for _, _, captured in captures if len(captured) == 2]
        self.assertGreater(len(double_captures), 0)


class TestGameMechanics(unittest.TestCase):
    """Тесты игровой механики"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_move_piece_success(self):
        """Тест успешного перемещения шашки"""
        # Создаем тестовую доску
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка в позиции (5, 1)
        white_piece = Piece(Player.WHITE)
        self.game.board[5][1] = white_piece

        # Устанавливаем валидные ходы
        self.game.selected_piece = (5, 1)
        self.game.valid_moves = [(4, 0, [])]  # Простой ход

        # Пытаемся сделать ход
        result = self.game.move_piece(5, 1, 4, 0)

        self.assertTrue(result)
        self.assertIsNone(self.game.board[5][1])
        self.assertEqual(self.game.board[4][0], white_piece)

    def test_move_piece_failure(self):
        """Тест неудачного перемещения шашки"""
        # Создаем тестовую доску
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка в позиции (5, 1)
        white_piece = Piece(Player.WHITE)
        self.game.board[5][1] = white_piece

        # Устанавливаем валидные ходы (только на (4, 0))
        self.game.selected_piece = (5, 1)
        self.game.valid_moves = [(4, 0, [])]

        # Пытаемся сделать невалидный ход
        result = self.game.move_piece(5, 1, 4, 2)  # Не входит в valid_moves

        self.assertFalse(result)
        self.assertEqual(self.game.board[5][1], white_piece)  # Шашка не переместилась

    def test_promotion_to_king(self):
        """Тест превращения в дамку"""
        # Создаем тестовую доску
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка на предпоследнем ряду перед превращением
        white_piece = Piece(Player.WHITE)
        self.game.board[1][1] = white_piece

        # Делаем ход на последний ряд (для белых это ряд 0)
        self.game.selected_piece = (1, 1)
        self.game.valid_moves = [(0, 0, []), (0, 2, [])]

        result = self.game.move_piece(1, 1, 0, 0)

        self.assertTrue(result)
        self.assertEqual(white_piece.type, PieceType.KING)  # Превратилась в дамку

    def test_capture_execution(self):
        """Тест выполнения взятия"""
        # Создаем тестовую доску
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка в позиции (4, 4)
        white_piece = Piece(Player.WHITE)
        self.game.board[4][4] = white_piece

        # Черная шашка в позиции (3, 3)
        black_piece = Piece(Player.BLACK)
        self.game.board[3][3] = black_piece

        # Устанавливаем валидный ход со взятием
        self.game.selected_piece = (4, 4)
        self.game.valid_moves = [(2, 2, [(3, 3)])]

        result = self.game.move_piece(4, 4, 2, 2)

        self.assertTrue(result)
        self.assertIsNone(self.game.board[4][4])  # Исходная позиция пуста
        self.assertIsNone(self.game.board[3][3])  # Черная шашка взята
        self.assertEqual(self.game.board[2][2], white_piece)  # Белая шашка на новой позиции


class TestGameOverConditions(unittest.TestCase):
    """Тесты условий окончания игры"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    @patch.object(CheckersGame, 'save_game_result')
    def test_game_over_no_white_pieces(self, mock_save):
        """Тест окончания игры при отсутствии белых шашек"""
        # Удаляем все белые шашки
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.game.get_piece(row, col)
                if piece and piece.player == Player.WHITE:
                    self.game.board[row][col] = None

        self.game.check_game_over()

        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, Player.BLACK)
        mock_save.assert_called_once()

    @patch.object(CheckersGame, 'save_game_result')
    def test_game_over_no_moves(self, mock_save):
        """Тест окончания игры при отсутствии ходов"""
        # Создаем ситуацию, когда у текущего игрока нет ходов
        self.game.current_player = Player.WHITE

        # Удаляем все шашки, кроме одной черной, заблокированной
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Одна белая шашка, окруженная со всех сторон
        self.game.board[1][1] = Piece(Player.WHITE)
        self.game.board[0][0] = Piece(Player.BLACK)
        self.game.board[0][2] = Piece(Player.BLACK)
        self.game.board[2][0] = Piece(Player.BLACK)
        self.game.board[2][2] = Piece(Player.BLACK)

        self.game.check_game_over()

        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, Player.BLACK)
        mock_save.assert_called_once()


class TestClickHandling(unittest.TestCase):
    """Тесты обработки кликов"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_handle_click_select_piece(self):
        """Тест выбора шашки кликом"""
        # В стандартной расстановке, белые шашки находятся в рядах 5, 6, 7
        # Находим первую белую шашку
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.game.get_piece(row, col)
                if piece and piece.player == Player.WHITE:
                    # Нажимаем на белую шашку
                    self.game.handle_click(row, col)
                    self.assertEqual(self.game.selected_piece, (row, col))
                    return

        self.fail("Не найдена белая шашка для теста")

    def test_handle_click_move_piece(self):
        """Тест перемещения шашки после выбора"""
        # Создаем простую доску с одной белой шашкой
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        white_piece = Piece(Player.WHITE)
        self.game.board[5][1] = white_piece
        self.game.current_player = Player.WHITE

        # Выбираем шашку
        self.game.handle_click(5, 1)

        # Должны быть доступны ходы
        self.assertGreater(len(self.game.valid_moves), 0)

        # Находим валидный ход для этой шашки
        if self.game.valid_moves:
            target_row, target_col, _ = self.game.valid_moves[0]

            # Нажимаем на целевую клетку
            self.game.handle_click(target_row, target_col)

            # Шашка должна переместиться
            self.assertIsNone(self.game.board[5][1])
            self.assertIsNotNone(self.game.board[target_row][target_col])

    def test_handle_click_game_over(self):
        """Тест игнорирования кликов при завершенной игре"""
        self.game.game_over = True
        initial_state = [[self.game.board[row][col] for col in range(BOARD_SIZE)] for row in range(BOARD_SIZE)]

        # Клик должен игнорироваться
        self.game.handle_click(5, 1)

        # Состояние доски не должно измениться
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.assertEqual(self.game.board[row][col], initial_state[row][col])


class TestDatabaseIntegration(unittest.TestCase):
    """Тесты интеграции с базой данных"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    @patch('src.game_logic.db_manager')
    def test_save_game_result_success(self, mock_db_manager):
        """Тест успешного сохранения результата игры"""
        # Настраиваем мок
        mock_db_manager.save_game_result.return_value = True

        # Завершаем игру
        self.game.game_over = True
        self.game.winner = Player.WHITE

        # Сохраняем результат
        result = self.game.save_game_result()

        self.assertTrue(result)
        self.assertTrue(self.game.game_saved)
        mock_db_manager.save_game_result.assert_called_once()

    @patch('src.game_logic.db_manager')
    def test_save_game_result_already_saved(self, mock_db_manager):
        """Тест предотвращения повторного сохранения"""
        # Настраиваем мок
        mock_db_manager.save_game_result.return_value = True

        # Первое сохранение
        self.game.game_over = True
        self.game.winner = Player.WHITE
        self.game.save_game_result()

        # Второе сохранение (не должно вызывать db_manager)
        mock_db_manager.save_game_result.reset_mock()
        result = self.game.save_game_result()

        self.assertFalse(result)  # Возвращает False при повторном сохранении
        mock_db_manager.save_game_result.assert_not_called()


class TestEdgeCases(unittest.TestCase):
    """Тесты граничных случаев и особых ситуаций"""

    def setUp(self):
        """Подготовка тестовой среды"""
        self.game = CheckersGame()

    def test_king_movement_complex(self):
        """Тест сложных ходов дамки"""
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Дамка в центре
        king = Piece(Player.WHITE)
        king.type = PieceType.KING
        self.game.board[3][3] = king

        # Препятствия по диагоналям
        self.game.board[1][1] = Piece(Player.BLACK)  # Вверх-влево
        self.game.board[1][5] = Piece(Player.WHITE)  # Вверх-вправо (своя шашка)
        self.game.board[5][1] = Piece(Player.BLACK)  # Вниз-влево
        self.game.board[6][6] = Piece(Player.BLACK)  # Вниз-вправо (далеко)

        moves = self.game.get_simple_moves_for_piece(3, 3, king)

        # Проверяем, что есть ходы
        self.assertGreater(len(moves), 0)

    def test_capture_with_edge_block(self):
        """Тест взятия у края доски"""
        self.game.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        # Белая шашка в позиции (1, 1)
        white_piece = Piece(Player.WHITE)
        self.game.board[1][1] = white_piece

        # Черная шашка в позиции (0, 0) - у самого края
        black_piece = Piece(Player.BLACK)
        self.game.board[0][0] = black_piece

        # Нельзя взять шашку у края доски (нет клетки за ней)
        captures = self.game.get_captures_for_piece(1, 1, white_piece)

        self.assertEqual(len(captures), 0)  # Нет возможных взятий


class TestPerformance(unittest.TestCase):
    """Тесты производительности"""

    def test_board_initialization_performance(self):
        """Тест производительности инициализации доски"""
        import time

        start_time = time.time()
        game = CheckersGame()
        end_time = time.time()

        # Инициализация должна занимать менее 0.1 секунды
        self.assertLess(end_time - start_time, 0.1)

    def test_valid_moves_calculation_performance(self):
        """Тест производительности расчета валидных ходов"""
        import time

        game = CheckersGame()

        # Измеряем время расчета валидных ходов для всех шашек
        start_time = time.time()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = game.get_piece(row, col)
                if piece and piece.player == game.current_player:
                    game.get_valid_moves(row, col)

        end_time = time.time()

        # Расчет должен занимать менее 0.5 секунды для всей доски
        self.assertLess(end_time - start_time, 0.5)


if __name__ == '__main__':
    unittest.main()