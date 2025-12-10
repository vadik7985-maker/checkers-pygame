import unittest

def safe_divide(a, b):
    """Функция деления с проверкой"""
    if b == 0:
        raise ZeroDivisionError("Деление на ноль запрещено")
    return a / b

def get_board_cell(board, row, col):
    """Получение клетки доски с проверкой границ"""
    if not (0 <= row < 8 and 0 <= col < 8):
        raise IndexError("Координаты вне доски")
    return board[row][col]

class TestExceptions(unittest.TestCase):
    def test_zero_division(self):
        """Тест деления на ноль как в лекции"""
        with self.assertRaises(ZeroDivisionError):
            safe_divide(10, 0)
    
    def test_invalid_board_coordinates(self):
        """Тест некорректных координат доски"""
        board = [[0] * 8 for _ in range(8)]
        
        with self.assertRaises(IndexError):
            get_board_cell(board, -1, 3)
        
        with self.assertRaises(IndexError):
            get_board_cell(board, 8, 5)
    
    def test_valid_operations(self):
        """Тест корректных операций"""
        self.assertEqual(safe_divide(10, 2), 5)
        
        board = [[0] * 8 for _ in range(8)]
        board[3][4] = "WHITE"
        self.assertEqual(get_board_cell(board, 3, 4), "WHITE")
