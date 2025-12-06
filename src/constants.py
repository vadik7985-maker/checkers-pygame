"""
Модуль для хранения всех констант игры
"""

# Размеры окна
BOARD_SIZE = 8
SQUARE_SIZE = 100
WIDTH = BOARD_SIZE * SQUARE_SIZE + 300
HEIGHT = BOARD_SIZE * SQUARE_SIZE + 50
FPS = 60

# Цвета деревянной доски
DARK_WOOD = (89, 47, 27)
LIGHT_WOOD = (210, 180, 140)

# Цвета шашек
BLACK_PIECE = (45, 45, 60)
WHITE_PIECE = (235, 235, 245)

# Акцентные цвета (для выделения элементов)
ACCENT_GOLD = (255, 215, 0)
ACCENT_SILVER = (200, 200, 210)
ACCENT_RED = (220, 80, 80)
ACCENT_GREEN = (80, 200, 120)
ACCENT_BLUE = (70, 130, 200)

# Фоновые цвета
BACKGROUND = (30, 30, 40)
PANEL_COLOR = (40, 40, 55)
PANEL_ACCENT = (60, 60, 80)
LIGHT_BLUE = (173, 216, 230)

# Цвета текста и статусной панели
STATUS_BAR = (35, 35, 50)
TEXT_LIGHT = (240, 240, 250)
TEXT_DARK = (180, 180, 200)

# Цвет для подсветки шашек, которые можно взять
HIGHLIGHT_CAPTURE = (255, 100, 100, 180)  

# Цвет тени под шашкой
PIECE_SHADOW = (20, 20, 30)

# Настройки времени
INITIAL_TIME_MINUTES = 7
INITIAL_TIME_SECONDS = INITIAL_TIME_MINUTES * 60