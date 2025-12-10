import unittest

class TestAssertMethods(unittest.TestCase):
    def test_various_asserts(self):
        # Примеры из лекции
        self.assertEqual(10, 10)                     # assertEqual
        self.assertNotEqual(10, 20)                  # assertNotEqual
        self.assertTrue(10 > 5)                      # assertTrue
        self.assertFalse(10 < 5)                     # assertFalse
        self.assertIs(None, None)                    # assertIs
        self.assertIsNone(None)                      # assertIsNone
        self.assertIn(3, [1, 2, 3])                  # assertIn
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)  # assertAlmostEqual
        self.assertGreater(10, 5)                    # assertGreater
        self.assertLessEqual(3, 3)                   # assertLessEqual
    
    def test_board_coordinates(self):
        # Проверка координат на доске
        board = [[0] * 8 for _ in range(8)]
        self.assertEqual(len(board), 8)  # 8 строк
        self.assertEqual(len(board[0]), 8)  # 8 столбцов
        self.assertTrue(all(len(row) == 8 for row in board))
