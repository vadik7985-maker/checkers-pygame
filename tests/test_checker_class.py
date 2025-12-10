import unittest

# Модель шашки как в лекции
class CheckerPiece:
    def __init__(self, color, is_king=False):
        self.color = color  # "WHITE" или "BLACK"
        self.is_king = is_king
        self.position = None
    
    def promote_to_king(self):
        """Превращение в дамку"""
        self.is_king = True
        return self
    
    def move(self, new_position):
        """Перемещение шашки"""
        old_position = self.position
        self.position = new_position
        return old_position, new_position

class TestCheckerPiece(unittest.TestCase):
    def test_piece_creation(self):
        """Тест создания шашки"""
        piece = CheckerPiece("WHITE")
        self.assertEqual(piece.color, "WHITE")
        self.assertFalse(piece.is_king)
    
    def test_promotion(self):
        """Тест превращения в дамку"""
        piece = CheckerPiece("BLACK")
        piece.promote_to_king()
        self.assertTrue(piece.is_king)
        self.assertEqual(piece.color, "BLACK")
    
    def test_movement(self):
        """Тест перемещения шашки"""
        piece = CheckerPiece("WHITE")
        piece.position = (2, 3)
        old, new = piece.move((3, 4))
        
        self.assertEqual(old, (2, 3))
        self.assertEqual(new, (3, 4))
        self.assertEqual(piece.position, (3, 4))
