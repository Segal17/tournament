# -*- coding: utf-8 -*-
"""Построение расписания турнира."""
from datetime import time, datetime, timedelta
from typing import Optional

from core.models import Pair, Match, Schedule, TournamentConfig


def _assign_court_by_index(idx: int) -> int:
    """Нечётная пара → площадка 1, чётная → площадка 2."""
    return 1 if idx % 2 == 1 else 2


def _compute_time(start_time: time, offset_index: int, game_minutes: int, break_minutes: int) -> time:
    """Вычисляет время с учётом смещения слотов."""
    total = offset_index * (game_minutes + break_minutes)
    dt = datetime.combine(datetime.today(), start_time) + timedelta(minutes=total)
    return dt.time()


def _add_playoff(all_matches: list, config: TournamentConfig, slot: int) -> None:
    """
    Добавляет матчи плей-офф.
    - 2 площадки: полуфиналы параллельно, финал параллельно
    - 1 площадка: все матчи последовательно на площадку 1
    """
    playoff_size = getattr(config, "playoff_size", 4)
    courts = config.courts

    def make_match(slot_offset, court, label, num1, num2, name1, name2):
        match_time = _compute_time(
            config.start_time,
            slot + slot_offset,
            config.game_minutes,
            config.break_minutes,
        )
        all_matches.append(Match(
            time=match_time,
            stage=0,
            court=court,
            round_num=0,
            num1=num1,
            num2=num2,
            name1=name1,
            name2=name2,
            warning_back_to_back=False,
            warning_same_court=False,
            is_playoff=True,
            playoff_label=label,
        ))

    if courts == 1:
        # === 1 ПЛОЩАДКА: всё на площадку 1, последовательно ===
        if playoff_size == 8:
            # 1/4 финала — 4 матча подряд
            make_match(0, 1, "1/4", 1, 8, "1", "8")
            make_match(1, 1, "1/4", 2, 7, "2", "7")
            make_match(2, 1, "1/4", 3, 6, "3", "6")
            make_match(3, 1, "1/4", 4, 5, "4", "5")
            # 1/2 финала — 2 матча подряд
            make_match(4, 1, "1/2", 0, None, "", None)
            make_match(5, 1, "1/2", 0, None, "", None)
            # финал
            make_match(6, 1, "финал", 0, None, "", None)
        else:
            # playoff_size == 4
            # 1/2 финала — 2 матча подряд
            make_match(0, 1, "1/2", 1, 4, "1", "4")
            make_match(1, 1, "1/2", 2, 3, "2", "3")
            # финал
            make_match(2, 1, "финал", 0, None, "", None)
        return

    # === 2 ПЛОЩАДКИ: как было ===
    if playoff_size == 8:
        # 1/4 финала — 2 матча параллельно, потом ещё 2
        make_match(0, 1, "1/4", 1, 8, "1", "8")
        make_match(0, 2, "1/4", 2, 7, "2", "7")
        make_match(1, 1, "1/4", 3, 6, "3", "6")
        make_match(1, 2, "1/4", 4, 5, "4", "5")
        # 1/2 финала
        make_match(2, 1, "1/2", 0, None, "", None)
        make_match(2, 2, "1/2", 0, None, "", None)
        # финал
        make_match(3, 1, "финал", 0, None, "", None)
        make_match(3, 2, "финал", 0, None, "", None)
    else:
        # playoff_size == 4
        make_match(0, 1, "1/2", 1, 4, "1", "4")
        make_match(0, 2, "1/2", 2, 3, "2", "3")
        make_match(1, 1, "финал", 0, None, "", None)
        make_match(1, 2, "финал", 0, None, "", None)


def build_schedule(
    pairs_by_stage: dict,
    config: TournamentConfig,
    players: dict,
) -> Schedule:
    """Строит расписание."""
    all_matches = []
    slot = 0
    court_count = config.courts

    for stage in sorted(pairs_by_stage.keys()):
        pairs = pairs_by_stage[stage]
        if not pairs:
            continue

        for i, pair in enumerate(pairs, start=1):
            if court_count == 1:
                court = 1
            else:
                court = _assign_court_by_index(i)

            round_in_stage = (i - 1) // court_count
            time_offset = slot + round_in_stage

            match_time = _compute_time(
                config.start_time, time_offset,
                config.game_minutes, config.break_minutes,
            )

            name1 = players.get(pair.num1, "?")
            name2 = players.get(pair.num2, "?") if pair.num2 is not None else None

            all_matches.append(Match(
                time=match_time,
                stage=stage,
                court=court,
                round_num=round_in_stage + 1,
                num1=pair.num1,
                num2=pair.num2,
                name1=name1,
                name2=name2,
                warning_back_to_back=False,
                warning_same_court=False,
            ))

        n_rounds = (len(pairs) + court_count - 1) // court_count
        slot += n_rounds

    # Плей-офф — всегда (и для 1, и для 2 площадок)
    _add_playoff(all_matches, config, slot)

    return Schedule(matches=all_matches, players=players, config=config)