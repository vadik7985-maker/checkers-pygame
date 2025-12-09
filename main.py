"""
Основной модуль запуска игры "Шашки".

Этот модуль является точкой входа в приложение. Он выполняет:
1. Настройку окружения и загрузку переменных из .env файла
2. Подключение к базе данных PostgreSQL
3. Инициализацию графического интерфейса PyGame
4. Запуск основного игрового цикла
5. Обработку ошибок и корректное завершение работы

Зависимости:
    - pygame: графическая библиотека
    - python-dotenv: загрузка переменных окружения
    - psycopg2: драйвер PostgreSQL (через src.database)
"""

import sys
import os
import pygame
from dotenv import load_dotenv

# Добавляем диагностику
print("=" * 50)
print(f"Текущая директория: {os.getcwd()}")
print(f"Путь к main.py: {__file__}")
print("=" * 50)

# Проверяем наличие .env файлов
env_paths = [
    '.env',  # Текущая директория
    os.path.join(os.path.dirname(__file__), '.env'),  # Рядом с main.py
]

for env_path in env_paths:
    if os.path.exists(env_path):
        print(f"Найден .env файл: {env_path}")
        load_dotenv(env_path)
        break
else:
    print("Внимание: .env файл не найден!")

# Проверяем переменные окружения
print("\nПроверка переменных окружения:")
env_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
for var in env_vars:
    value = os.getenv(var)
    print(f"  {var}: {value if value else 'НЕ НАЙДЕНА'}")

print("=" * 50)

from src.graphics import CheckersGUI
from src.database import db_manager


def main():
    """Основная функция запуска игры.

    Инициализирует все компоненты приложения и запускает игровой цикл.
    Обеспечивает корректную обработку ошибок и освобождение ресурсов.

    Raises:
        Exception: Любая ошибка при запуске игры логируется и выводится

    Примечание:
        Использует конструкцию try-except-finally для гарантированного
        закрытия соединений с БД и PyGame.
    """
    try:
        # Пытаемся подключиться к базе данных
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
    """Точка входа при запуске файла напрямую.

    Вызывает функцию main() и завершает программу с кодом возврата.
    """
    main()