# -*- coding: utf-8 -*-
"""Работа со схемами пар."""

from typing import Dict, List, Optional, Tuple

from core.models import Pair


def parse_scheme(scheme: str) -> List[Tuple[int, Optional[int]]]:
    """Разбирает схему в список кортежей (номер1, номер2 или None).

    Разделитель — двоеточие ':'.
    Форматы: "1:8", "7", "7:", "7:7".
    """
    if not scheme.strip():
        raise ValueError("Схема пар не заполнена")

    pairs: List[Tuple[int, Optional[int]]] = []
    for chunk in scheme.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue

        # Одиночный номер: "7"
        if ":" not in chunk:
            if not chunk.isdigit():
                raise ValueError(f"Неверный формат пары: '{chunk}' (ожидается 1:8 или 7)")
            num1 = int(chunk)
            pairs.append((num1, None))
            continue

        # Есть двоеточие: "1:8", "7:", "7:7"
        parts = chunk.split(":")
        if len(parts) != 2:
            raise ValueError(f"Неверный формат пары: '{chunk}' (ожидается 1:8)")

        left, right = parts[0].strip(), parts[1].strip()
        if not left.isdigit():
            raise ValueError(f"Неверный номер в паре: '{chunk}'")
        num1 = int(left)

        num2: Optional[int] = None
        if right:
            if not right.isdigit():
                raise ValueError(f"Неверный номер в паре: '{chunk}'")
            num2 = int(right)
            if num2 == num1:
                num2 = None

        pairs.append((num1, num2))

    return pairs


def apply_scheme(
    scheme: List[Tuple[int, Optional[int]]],
    players: Dict[int, str],
    stage: int,
) -> List[Pair]:
    """Применяет схему к результату жеребьёвки."""
    return [Pair(num1=n1, num2=n2, stage=stage) for n1, n2 in scheme]


def find_player_in_pair(
    pairs: List[Pair], player_num: int, stage: int
) -> Optional[Pair]:
    """Ищет пару игрока на указанном этапе."""
    for pair in pairs:
        if pair.stage != stage:
            continue
        if pair.num1 == player_num or pair.num2 == player_num:
            return pair
    return None