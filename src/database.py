import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
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

    def save_game_result(self, winner: str, white_pieces: int, black_pieces: int,
                         white_time: float, black_time: float, total_moves: int = 0,
                         game_duration: Optional[str] = None,
                         additional_info: Optional[Dict] = None) -> bool:

        if not self.connection:
            print("Нет подключения к базе данных")
            return False

        try:
            insert_query = """
               INSERT INTO game_results 
               (winner, white_pieces_remaining, black_pieces_remaining, 
                white_time_remaining, black_time_remaining, total_moves,
                game_duration, additional_info)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id;
               """

            self.cursor.execute(insert_query, (
                winner,
                white_pieces,
                black_pieces,
                white_time,
                black_time,
                total_moves,
                game_duration,
                psycopg2.extras.Json(additional_info) if additional_info else None
            ))

            game_id = self.cursor.fetchone()['id']
            self.connection.commit()

            print(f"Результат игры сохранен с ID: {game_id}")
            return True

        except Exception as e:
            print(f"Ошибка при сохранении результата игры: {e}")
            self.connection.rollback()
            return False

    def get_game_statistics(self, limit: int = 10) -> list:
        if not self.connection:
            return []

        try:
            query = """
               SELECT * FROM game_results 
               ORDER BY game_date DESC 
               LIMIT %s;
               """

            self.cursor.execute(query, (limit,))
            return self.cursor.fetchall()

        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return []

    def get_winner_stats(self) -> Dict:
        """Получение статистики побед"""
        if not self.connection:
            return {}

        try:
            query = """
                SELECT 
                    winner,
                    COUNT(*) as total_games,
                    AVG(white_pieces_remaining) as avg_white_pieces,
                    AVG(black_pieces_remaining) as avg_black_pieces,
                    AVG(white_time_remaining) as avg_white_time,
                    AVG(black_time_remaining) as avg_black_time
                FROM game_results 
                GROUP BY winner
                ORDER BY total_games DESC;
                """

            self.cursor.execute(query)
            results = self.cursor.fetchall()

            stats = {}
            for row in results:
                stats[row['winner']] = dict(row)

            return stats

        except Exception as e:
            print(f"Ошибка при получении статистики побед: {e}")
            return {}

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Создаем глобальный экземпляр для использования в проекте
    db_manager = DatabaseManager()