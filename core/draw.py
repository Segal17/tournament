"""Жеребьёвка участников."""

import random
from typing import Dict, List


def draw_numbers(players: List[str]) -> Dict[int, str]:
    """Случайным образом присваивает каждому участнику номер.

    Returns:
        Словарь {номер: фамилия}.
    """
    numbers = list(range(1, len(players) + 1))
    random.shuffle(numbers)
    return {number: name for number, name in zip(numbers, players)}
