"""
Модуль для тестирования подключения к базе данных PostgreSQL.

Этот скрипт проверяет корректность настроек подключения к базе данных:
1. Загружает переменные окружения из .env файла
2. Пытается подключиться к PostgreSQL с указанными параметрами
3. Проверяет наличие необходимых таблиц
4. Выводит диагностическую информацию

Использование:
    python test_connection.py

Назначение:
    - Отладка проблем с подключением к БД
    - Проверка корректности настроек в .env файле
    - Верификация существования таблиц
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

print("=== Тест подключения к PostgreSQL ===")

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print("✅ Подключение успешно!")

    # Проверяем, есть ли таблицы
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = cursor.fetchall()

    print(f"Таблицы в базе: {[t[0] for t in tables]}")

    conn.close()

except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("\nВозможные причины:")
    print("1. PostgreSQL не запущен")
    print("2. Неправильный пароль в .env файле")
    print("3. База данных checkers_db не создана")
    print("4. Порт 5432 занят другим приложением")