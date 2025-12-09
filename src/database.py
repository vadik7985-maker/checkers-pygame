"""
Модуль для работы с базой данных PostgreSQL.

Этот модуль предоставляет класс DatabaseManager для управления подключением
к базе данных PostgreSQL и сохранения результатов игр.

Основные возможности:
    1. Подключение к PostgreSQL с настройками из .env файла
    2. Автоматическое создание таблиц при первом подключении
    3. Сохранение результатов игры с детальной статистикой
    4. Получение статистики игр и побед
    5. Безопасное управление соединением (контекстный менеджер)

Зависимости:
    - psycopg2: драйвер PostgreSQL для Python
    - python-dotenv: загрузка переменных окружения из .env файла
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import os


class DatabaseManager:
    """Менеджер для работы с базой данных PostgreSQL.

    Обеспечивает все операции с базой данных для игры в шашки:
    подключение, создание таблиц, сохранение и получение статистики.

    Attributes:
        connection: Соединение с базой данных PostgreSQL
        cursor: Курсор для выполнения SQL-запросов
    """

    def __init__(self):
        """Инициализирует менеджер базы данных.

        Создает пустые атрибуты для соединения и курсора.
        Фактическое подключение происходит при вызове метода connect().
        """
        self.connection = None
        self.cursor = None

    def connect(self):
        """Устанавливает подключение к базе данных PostgreSQL.

        Загружает настройки из .env файла и подключается к базе данных.
        При успешном подключении автоматически создает необходимые таблицы.

        Raises:
            Exception: Если подключение к базе данных не удалось

        Примечание:
            Ищет .env файл в нескольких возможных расположениях:
            1. Корень проекта
            2. Папка src
            3. Текущая директория
        """
        try:
            # Загружаем .env из разных возможных мест
            env_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'),  # Корень проекта
                os.path.join(os.path.dirname(__file__), '.env'),  # Папка src
                '.env'  # Текущая директория
            ]

            for env_path in env_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    print(f"Загружен .env из: {env_path}")
                    break

            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'checkers_db')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', 'password')  # Убрали декодирование

            self.connection = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Успешно подключено к базе данных")

            # Создаем таблицу если её нет
            self.create_tables()

        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            self.connection = None

    def create_tables(self):
        """Создает необходимые таблицы в базе данных.

        Создает две таблицы:
        1. game_results - для сохранения результатов отдельных игр
        2. player_stats - для статистики игроков (резерв на будущее)

        Raises:
            Exception: Если создание таблиц не удалось
        """
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
        """Сохраняет результат игры в базу данных.

        Args:
            winner (str): Победитель игры ('white' или 'black')
            white_pieces (int): Количество оставшихся белых шашек
            black_pieces (int): Количество оставшихся черных шашек
            white_time (float): Оставшееся время белых в секундах
            black_time (float): Оставшееся время черных в секундах
            total_moves (int): Общее количество ходов в игре, по умолчанию 0
            game_duration (Optional[str]): Продолжительность игры в формате MM:SS
            additional_info (Optional[Dict]): Дополнительная информация о игре

        Returns:
            bool: True если сохранение успешно, False в противном случае

        Raises:
            Exception: Если произошла ошибка при сохранении
        """
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
        """Получает последние результаты игр из базы данных.

        Args:
            limit (int): Количество возвращаемых записей, по умолчанию 10

        Returns:
            list: Список словарей с результатами игр

        Примечание:
            Возвращает пустой список если нет подключения к БД или произошла ошибка
        """
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
        """Получает статистику побед по игрокам.

        Returns:
            Dict: Словарь с статистикой побед, где ключ - победитель ('white'/'black')

        Статистика включает:
            - total_games: общее количество побед
            - avg_white_pieces: среднее оставшихся белых шашек
            - avg_black_pieces: среднее оставшихся черных шашек
            - avg_white_time: среднее оставшееся время белых
            - avg_black_time: среднее оставшееся время черных
        """
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
        """Закрывает соединение с базой данных.

        Освобождает ресурсы курсора и соединения.
        Рекомендуется вызывать после завершения работы с БД.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

    def __enter__(self):
        """Поддерживает использование класса как контекстного менеджера.

        Returns:
            DatabaseManager: Текущий экземпляр менеджера
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Завершает работу контекстного менеджера, закрывая соединение."""
        self.close()


# Создаем глобальный экземпляр для использования в проекте
db_manager = DatabaseManager()