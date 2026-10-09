# -*- coding: utf-8 -*-
"""Модели данных турнира."""
from dataclasses import dataclass
from datetime import time
from typing import Optional


@dataclass
class Player:
    number: int
    name: str
    games_played: int = 0


@dataclass
class Pair:
    num1: int
    num2: Optional[int]
    stage: int


@dataclass
class Match:
    time: time
    stage: int
    court: int
    round_num: int
    num1: int
    num2: Optional[int]
    name1: str
    name2: Optional[str]
    warning_back_to_back: bool = False
    warning_same_court: bool = False
    is_playoff: bool = False
    playoff_label: str = ""


@dataclass
class TournamentConfig:
    matches_per_player: int
    courts: int
    start_time: time
    game_minutes: int
    break_minutes: int
    playoff_size: int = 4
    gender: str = "W"
    tournament_name: str = ""


@dataclass
class Schedule:
    matches: list
    players: dict
    config: TournamentConfig