"""
Модуль для просмотра статистики игр из базы данных.

Этот скрипт предоставляет консольный интерфейс для просмотра:
1. Последних игр с детальной информацией
2. Статистики побед по игрокам
3. Средних показателей игры

Использование:
    python view_stats.py

Назначение:
    - Анализ результатов игр
    - Отладка системы сохранения статистики
    - Просмотр истории игр без запуска графического интерфейса
"""

from src.database import db_manager


def view_statistics():
    """Выводит статистику игр в консоль.

    Запрашивает данные из базы данных и форматирует их для удобного
    чтения в консоли. Показывает:

    1. Последние 10 игр:
        - Дата и время
        - Победитель
        - Оставшиеся шашки
        - Оставшееся время

    2. Статистику побед:
        - Количество побед каждого игрока
        - Средние показатели игры

    Raises:
        Exception: Если не удалось подключиться к базе данных
    """
    db_manager.connect()

    print("=== СТАТИСТИКА ИГР В ШАШКИ ===\n")

    games = db_manager.get_game_statistics(limit=10)

    print("Последние игры:")
    print("-" * 100)
    print(f"{'Дата':<20} {'Победитель':<10} {'Белые':<8} {'Черные':<8} {'Время белых':<12} {'Время черных':<12}")
    print("-" * 100)

    for game in games:
        print(f"{game['game_date'].strftime('%Y-%m-%d %H:%M'):<20} "
              f"{game['winner']:<10} "
              f"{game['white_pieces_remaining']:<8} "
              f"{game['black_pieces_remaining']:<8} "
              f"{game['white_time_remaining']:<12.1f} "
              f"{game['black_time_remaining']:<12.1f}")

    print("\n" + "=" * 100 + "\n")

    stats = db_manager.get_winner_stats()

    print("Статистика побед:")
    print("-" * 50)
    for winner, data in stats.items(): # словарь со статистикой
        print(f"\nПобедитель: {winner}")
        print(f"  Всего игр: {data['total_games']}")
        print(f"  Среднее осталось белых шашек: {data['avg_white_pieces']:.1f}")
        print(f"  Среднее осталось черных шашек: {data['avg_black_pieces']:.1f}")
        print(f"  Среднее оставшееся время белых: {data['avg_white_time']:.1f} сек")
        print(f"  Среднее оставшееся время черных: {data['avg_black_time']:.1f} сек")

    db_manager.close()


if __name__ == "__main__":
    """Точка входа при запуске скрипта напрямую.

    Вызывает функцию view_statistics() для отображения статистики.
    """
    view_statistics()