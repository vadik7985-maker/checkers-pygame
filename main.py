"""
Главный файл для запуска игры в шашки
"""

import sys
import pygame
from src.graphics import CheckersGUI

def main():
    """Основная функция запуска игры"""
    try:
        pygame.init()
        pygame.font.init()
        gui = CheckersGUI()
        gui.run()
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()