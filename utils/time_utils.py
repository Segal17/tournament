"""Утилиты для работы со временем."""

from datetime import time, datetime, timedelta


def parse_time(s: str) -> time:
    """Парсит строку 'HH:MM' в объект time.

    Raises:
        ValueError: если формат неверный.
    """
    try:
        parts = s.strip().split(":")
        if len(parts) != 2:
            raise ValueError
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        return time(hour, minute)
    except ValueError:
        raise ValueError(f"Неверный формат времени: '{s}'. Ожидается HH:MM.")


def format_time(t: time) -> str:
    """Форматирует time в строку 'HH:MM'."""
    return t.strftime("%H:%M")


def add_minutes(t: time, minutes: int) -> time:
    """Прибавляет минуты к времени с переходом через полночь."""
    dt = datetime.combine(datetime.today().date(), t) + timedelta(minutes=minutes)
    return dt.time()
