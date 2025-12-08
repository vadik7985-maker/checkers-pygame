import psycopg2
from psycopg2.extras import RealDictCursor

import os


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Подключение к базе данных"""
        try:
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'checkers_db')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', 'password')

            self.connection = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Успешно подключено к базе данных")

            self.create_tables()

        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            self.connection = None

