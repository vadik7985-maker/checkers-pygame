import unittest

# Игровые константы
BOARD_SIZE = 8
SQUARE_SIZE = 80
WHITE = "WHITE"
BLACK = "BLACK"
PLAYER_COLORS = [WHITE, BLACK]
PIECE_TYPES = ["MAN", "KING"]

class TestGameConstants(unittest.TestCase):
    def test_constants(self):
        """Тест игровых констант"""
        self.assertEqual(BOARD_SIZE, 8)
        self.assertEqual(SQUARE_SIZE, 80)
        self.assertEqual(WHITE, "WHITE")
        self.assertEqual(BLACK, "BLACK")
    
    def test_colors_list(self):
        """Тест списка цветов"""
        self.assertIn(WHITE, PLAYER_COLORS)
        self.assertIn(BLACK, PLAYER_COLORS)
        self.assertEqual(len(PLAYER_COLORS), 2)
    
    def test_piece_types(self):
        """Тест типов шашек"""
        self.assertIn("MAN", PIECE_TYPES)
        self.assertIn("KING", PIECE_TYPES)
        self.assertEqual(PIECE_TYPES[0], "MAN")
        self.assertEqual(PIECE_TYPES[1], "KING")
    
    def test_board_dimensions(self):
        """Тест размеров доски"""
        board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.assertEqual(len(board), BOARD_SIZE)
        for row in board:
            self.assertEqual(len(row), BOARD_SIZE)
