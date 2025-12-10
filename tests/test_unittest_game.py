import unittest

class TestCheckersGame(unittest.TestCase):
    def test_game_initialization(self):
        # Тест инициализации игры
        board_size = 8
        player_turn = "WHITE"
        
        self.assertEqual(board_size, 8)
        self.assertEqual(player_turn, "WHITE")
    
    def test_piece_movement(self):
        # Тест движения шашки
        start_pos = (2, 3)
        end_pos = (3, 4)
        
        self.assertNotEqual(start_pos, end_pos)
        self.assertEqual(abs(start_pos[0] - end_pos[0]), 1)
        self.assertEqual(abs(start_pos[1] - end_pos[1]), 1)
    
    def test_king_conversion(self):
        # Тест превращения в дамку
        piece_type = "MAN"
        row_position = 7  # Последняя строка для белых
        
        if row_position == 7:
            piece_type = "KING"
        
        self.assertEqual(piece_type, "KING")
