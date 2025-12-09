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

    def create_tables(self):
        """Создание таблиц в базе данных"""
        try:
            # Таблица для сохранения результатов игр
            create_table_query = """
            CREATE TABLE IF NOT EXISTS game_results (
                id SERIAL PRIMARY KEY,
                game_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                winner VARCHAR(10) NOT NULL,
                white_pieces_remaining INTEGER NOT NULL,
                black_pieces_remaining INTEGER NOT NULL,
                white_time_remaining FLOAT NOT NULL,
                black_time_remaining FLOAT NOT NULL,
                total_moves INTEGER DEFAULT 0,
                game_duration INTERVAL,
                additional_info JSONB
            );

            -- Таблица для статистики игроков (если будете добавлять логины)
            CREATE TABLE IF NOT EXISTS player_stats (
                id SERIAL PRIMARY KEY,
                player_name VARCHAR(50) UNIQUE,
                total_games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                total_pieces_taken INTEGER DEFAULT 0
            );
            """

            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("Таблицы успешно созданы")

        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            self.connection.rollback()


