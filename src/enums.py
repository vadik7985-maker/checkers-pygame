"""
Модуль для хранения перечислений (Enums)
"""

from enum import Enum

class PieceType(Enum):
    NONE = 0
    MAN = 1
    KING = 2

class Player(Enum):
    WHITE = 0
    BLACK = 1