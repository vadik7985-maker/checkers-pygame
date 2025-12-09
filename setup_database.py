"""
Модуль для настройки базы данных PostgreSQL для игры "Шашки".

Этот скрипт выполняет начальную настройку базы данных:
1. Подключается к серверу PostgreSQL
2. Создает базу данных 'checkers_db' если она не существует
3. Предоставляет инструкции по настройке переменных окружения

Использование:
    python setup_database.py

Требования:
    - Установленный и запущенный PostgreSQL
    - Права на создание баз данных
    - Пакет psycopg2-binary

Примечание:
    Этот скрипт нужно запустить один раз перед первым запуском игры.
"""

import psycopg2
from psycopg2 import sql
import getpass


def setup_database():
    """Выполняет настройку базы данных для игры.

    Запрашивает у пользователя параметры подключения к PostgreSQL,
    создает базу данных 'checkers_db' и выводит инструкции по настройке.

    Процесс:
        1. Запрос параметров подключения (хост, порт, пользователь, пароль)
        2. Подключение к системной базе данных 'postgres'
        3. Проверка существования базы 'checkers_db'
        4. Создание базы данных если она не существует
        5. Вывод инструкций для создания .env файла

    Raises:
        psycopg2.OperationalError: Если не удалось подключиться к PostgreSQL
        Exception: Любая другая ошибка при настройке
    """
    print("=== Настройка базы данных для игры в шашки ===")

    # Запрашиваем данные для подключения
    host = input("Хост базы данных [localhost]: ") or "localhost"
    port = input("Порт [5432]: ") or "5432"
    user = input("Имя пользователя [postgres]: ") or "postgres"
    password = getpass.getpass("Пароль: ")

    try:
        # Подключаемся к серверу PostgreSQL
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"  # Подключаемся к системной базе
        )
        connection.autocommit = True
        cursor = connection.cursor()

        # Создаем базу данных если её нет
        db_name = "checkers_db"
        cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [db_name])

        if not cursor.fetchone():
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"База данных '{db_name}' создана")
        else:
            print(f"База данных '{db_name}' уже существует")

        cursor.close()
        connection.close()

        print("\nБаза данных настроена успешно!")
        print("\nДобавьте следующие переменные окружения:")
        print(f"export DB_HOST='{host}'")
        print(f"export DB_PORT='{port}'")
        print(f"export DB_NAME='{db_name}'")
        print(f"export DB_USER='{user}'")
        print(f"export DB_PASSWORD='{password}'")

        print("\nИли создайте файл .env в корне проекта:")
        print(f"DB_HOST={host}")
        print(f"DB_PORT={port}")
        print(f"DB_NAME={db_name}")
        print(f"DB_USER={user}")
        print(f"DB_PASSWORD={password}")

    except Exception as e:
        print(f"Ошибка при настройке базы данных: {e}")


if __name__ == "__main__":
    """Точка входа при запуске скрипта напрямую.

    Вызывает функцию setup_database() для настройки БД.
    """
    setup_database()