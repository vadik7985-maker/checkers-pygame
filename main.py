import sys
import pygame
from src.graphics import CheckersGUI
from src.database import db_manager


def main():
    """Основная функция запуска игры"""
    try:
        try:
            db_manager.connect()
        except Exception as db_error:
            print(f"Не удалось подключиться к базе данных: {db_error}")
            print("Игра будет работать без сохранения статистики")

        pygame.init()
        pygame.font.init()
        gui = CheckersGUI()
        gui.run()
    except Exception as e:
        print(f"Ошибка при запуске игры: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()