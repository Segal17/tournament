# -*- coding: utf-8 -*-
"""Валидация ввода для турнира."""

from typing import List


def validate_players(raw: str) -> List[str]:
    """Разбирает и валидирует список участников."""
    lines = [line.strip() for line in raw.splitlines()]
    players = [line for line in lines if line]

    if len(players) < 4:
        raise ValueError(f"Нужно минимум 4 участника (сейчас {len(players)})")

    if len(players) != len(set(players)):
        raise ValueError("Все фамилии должны быть уникальными")

    return players


def validate_settings(
    matches: int, courts: int, game_minutes: int, break_minutes: int
) -> None:
    """Проверяет настройки турнира."""
    if matches not in (1, 2):
        raise ValueError("Партий на игрока должно быть 1 или 2")
    if courts not in (1, 2):
        raise ValueError("Площадок должно быть 1 или 2")
    if game_minutes < 5:
        raise ValueError("Длительность игры минимум 5 минут")
    if break_minutes < 0:
        raise ValueError("Перерыв не может быть отрицательным")


def validate_scheme(scheme: str, max_number: int, expected_pairs: int) -> None:
    """Проверяет схему пар. Разделитель — ':'."""
    if not scheme or not scheme.strip():
        raise ValueError("Схема пустая.")

    chunks = [c.strip() for c in scheme.split(",") if c.strip()]
    used: set = set()

    for chunk in chunks:
        if ":" not in chunk:
            if not chunk.isdigit():
                raise ValueError(f"Неверный формат пары: '{chunk}' (ожидается 1:8 или 7)")
            num = int(chunk)
            if num < 1 or num > max_number:
                raise ValueError(f"Номер {num} вне диапазона 1..{max_number}")
            if num in used:
                raise ValueError(f"Номер {num} встречается дважды")
            used.add(num)
            continue

        parts = chunk.split(":")
        if len(parts) != 2:
            raise ValueError(f"Неверный формат пары: '{chunk}' (ожидается 1:8)")

        left, right = parts[0].strip(), parts[1].strip()

        if not left.isdigit():
            raise ValueError(f"Неверный номер: '{left}' в паре '{chunk}'")
        num1 = int(left)
        if num1 < 1 or num1 > max_number:
            raise ValueError(f"Номер {num1} вне диапазона 1..{max_number}")

        if right == "":
            if num1 in used:
                raise ValueError(f"Номер {num1} встречается дважды")
            used.add(num1)
            continue

        if not right.isdigit():
            raise ValueError(f"Неверный номер: '{right}' в паре '{chunk}'")
        num2 = int(right)
        if num2 < 1 or num2 > max_number:
            raise ValueError(f"Номер {num2} вне диапазона 1..{max_number}")

        if num1 == num2:
            if num1 in used:
                raise ValueError(f"Номер {num1} встречается дважды")
            used.add(num1)
            continue

        for n in (num1, num2):
            if n in used:
                raise ValueError(f"Номер {n} встречается дважды")
            used.add(n)

    if len(used) != max_number:
        missing = sorted(set(range(1, max_number + 1)) - used)
        raise ValueError(f"Не все участники задействованы. Не хватает номеров: {missing}")