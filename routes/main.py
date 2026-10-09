# -*- coding: utf-8 -*-
"""Маршруты Flask-приложения турнира."""
from datetime import datetime

from flask import (
    Blueprint, render_template, request, session,
    redirect, url_for, send_file,
)

from config import Config
from core.draw import draw_numbers
from core.pairing import parse_scheme, apply_scheme
from core.scheduler import build_schedule
from core.exporter import export_to_docx, export_template_docx
from core.models import TournamentConfig, Match, Schedule
from utils.validators import validate_players, validate_settings, validate_scheme
from utils.time_utils import parse_time


main_bp = Blueprint("main", __name__)


# ============================================================
# ГЕНЕРАЦИЯ СХЕМ
# ============================================================

def _suggest_scheme(n_players: int, stage: int, variant: str = "through_one") -> str:
    if n_players < 4:
        return ""

    pairs = []

    # ============================================================
    # ЭТАП 2 — специальная логика
    # ============================================================
    if stage == 2:
        i = 1
        while i <= n_players:
            group = list(range(i, min(i + 8, n_players + 1)))

            if len(group) == 8:
                # полная группа — «скрест»
                a, b, c, d, e, f, g, h = group
                pairs.append(f"{b}:{h}")
                pairs.append(f"{a}:{g}")
                pairs.append(f"{d}:{f}")
                pairs.append(f"{c}:{e}")
            else:
                # неполная группа — простая последовательная
                j = 0
                while j + 1 < len(group):
                    pairs.append(f"{group[j]}:{group[j+1]}")
                    j += 2
                if j < len(group):
                    pairs.append(f"{group[j]}")

            i += 8

        return ", ".join(pairs)

    # ============================================================
    # ЭТАП 1 — обычная логика
    # ============================================================
    nums = list(range(1, n_players + 1))

    if variant == "first_last":
        left, right = 0, len(nums) - 1
        while left < right:
            pairs.append(f"{nums[left]}:{nums[right]}")
            left += 1
            right -= 1
        if left == right:
            pairs.append(f"{nums[left]}")
    else:
        i = 0
        while i + 3 < len(nums):
            a, b, c, d = nums[i], nums[i + 1], nums[i + 2], nums[i + 3]
            pairs.append(f"{a}:{c}")
            pairs.append(f"{b}:{d}")
            i += 4
        remaining = nums[i:]
        if len(remaining) == 3:
            pairs.append(f"{remaining[0]}:{remaining[2]}")
            pairs.append(f"{remaining[1]}")
        elif len(remaining) == 2:
            pairs.append(f"{remaining[0]}:{remaining[1]}")
        elif len(remaining) == 1:
            pairs.append(f"{remaining[0]}")

    return ", ".join(pairs)


def _empty_schemes() -> dict:
    return {
        "scheme1_through": "",
        "scheme1_first": "",
        "scheme2_through": "",
        "scheme2_first": "",
    }


def _build_schemes(draw_result: dict, matches: int) -> dict:
    if not draw_result:
        return _empty_schemes()
    n = len(draw_result)
    return {
        "scheme1_through": _suggest_scheme(n, 1, "through_one"),
        "scheme1_first": _suggest_scheme(n, 1, "first_last"),
        "scheme2_through": _suggest_scheme(n, 2, "through_one") if matches == 2 else "",
        "scheme2_first": _suggest_scheme(n, 2, "first_last") if matches == 2 else "",
    }


def _serialize_match(m) -> dict:
    return {
        "time": m.time.strftime("%H:%M"),
        "stage": m.stage,
        "court": m.court,
        "round_num": m.round_num,
        "num1": m.num1,
        "num2": m.num2,
        "name1": m.name1,
        "name2": m.name2,
        "warning_back_to_back": m.warning_back_to_back,
        "warning_same_court": m.warning_same_court,
        "is_playoff": getattr(m, "is_playoff", False),
        "playoff_label": getattr(m, "playoff_label", ""),
    }


def _deserialize_match(d: dict) -> Match:
    return Match(
        time=parse_time(d["time"]),
        stage=d["stage"],
        court=d["court"],
        round_num=d["round_num"],
        num1=d["num1"],
        num2=d["num2"],
        name1=d["name1"],
        name2=d["name2"],
        warning_back_to_back=d["warning_back_to_back"],
        warning_same_court=d["warning_same_court"],
        is_playoff=d.get("is_playoff", False),
        playoff_label=d.get("playoff_label", ""),
    )


# ============================================================
# ГЛАВНАЯ
# ============================================================

@main_bp.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        draw_result=None,
        matches=1,
        courts=2,
        gender="W",
        tournament_name="",
        n_players=0,
        error=None,
        rules_text=Config.DRAW_RULES_TEXT,
        **_empty_schemes(),
    )


# ============================================================
# ЖЕРЕБЬЁВКА
# ============================================================

@main_bp.route("/draw", methods=["POST"])
def draw():
    try:
        raw_players = request.form.get("players", "")
        matches = int(request.form.get("matches", "1"))
        courts = int(request.form.get("courts", "2"))
        start_time_str = request.form.get("start_time", "09:00")
        game_minutes = int(request.form.get("game_minutes", "40"))
        break_minutes = int(request.form.get("break_minutes", "5"))
        gender = request.form.get("gender", "W")
        tournament_name = request.form.get("tournament_name", "").strip()

        players_list = validate_players(raw_players)
        validate_settings(matches, courts, game_minutes, break_minutes)
        parse_time(start_time_str)

        draw_result = draw_numbers(players_list)

        session["draw_result"] = {str(k): v for k, v in draw_result.items()}
        session["settings"] = {
            "matches": matches,
            "courts": courts,
            "start_time": start_time_str,
            "game_minutes": game_minutes,
            "break_minutes": break_minutes,
            "playoff_size": 4,
            "gender": gender,
            "tournament_name": tournament_name,
        }

        return render_template(
            "index.html",
            draw_result=draw_result,
            matches=matches,
            courts=courts,
            gender=gender,
            tournament_name=tournament_name,
            n_players=len(players_list),
            error=None,
            rules_text=Config.DRAW_RULES_TEXT,
            **_build_schemes(draw_result, matches),
        )

    except ValueError as e:
        return render_template(
            "index.html",
            draw_result=None, matches=1, courts=2, gender="W",
            tournament_name="",
            n_players=0,
            error=str(e),
            rules_text=Config.DRAW_RULES_TEXT,
            **_empty_schemes(),
        )
    except Exception as e:
        return render_template(
            "index.html",
            draw_result=None, matches=1, courts=2, gender="W",
            tournament_name="",
            n_players=0,
            error=f"Ошибка: {e}",
            rules_text=Config.DRAW_RULES_TEXT,
            **_empty_schemes(),
        )


# ============================================================
# РАСПИСАНИЕ
# ============================================================

@main_bp.route("/schedule", methods=["POST"])
def schedule():
    try:
        draw_result_raw = session.get("draw_result")
        settings = session.get("settings")
        if not draw_result_raw or not settings:
            return redirect(url_for("main.index"))

        draw_result = {int(k): v for k, v in draw_result_raw.items()}
        n_players = len(draw_result)
        matches = settings["matches"]
        courts = settings["courts"]
        start_time = parse_time(settings["start_time"])
        game_minutes = settings["game_minutes"]
        break_minutes = settings["break_minutes"]
        gender = settings.get("gender", "W")
        tournament_name = settings.get("tournament_name", "")

        playoff_size = int(request.form.get("playoff_size", "4"))
        if playoff_size == 8 and n_players < 8:
            playoff_size = 4

        expected_pairs = (n_players + 1) // 2

        scheme1_str = request.form.get("scheme1", "").strip()
        if not scheme1_str:
            raise ValueError("Не задана схема для этапа 1.")

        scheme1_parsed = parse_scheme(scheme1_str)
        validate_scheme(scheme1_str, n_players, expected_pairs)
        pairs1 = apply_scheme(scheme1_parsed, draw_result, stage=1)

        pairs_by_stage = {1: pairs1}

        if matches == 2:
            scheme2_str = request.form.get("scheme2", "").strip()
            if not scheme2_str:
                raise ValueError("Не задана схема для этапа 2.")
            scheme2_parsed = parse_scheme(scheme2_str)
            validate_scheme(scheme2_str, n_players, expected_pairs)
            pairs2 = apply_scheme(scheme2_parsed, draw_result, stage=2)
            pairs_by_stage[2] = pairs2

        cfg = TournamentConfig(
            matches_per_player=matches,
            courts=courts,
            start_time=start_time,
            game_minutes=game_minutes,
            break_minutes=break_minutes,
            playoff_size=playoff_size,
            gender=gender,
            tournament_name=tournament_name,
        )

        schedule_obj = build_schedule(pairs_by_stage, cfg, draw_result)

        schedule_data = [_serialize_match(m) for m in schedule_obj.matches]
        session["schedule_data"] = schedule_data
        session["draw_result"] = {str(k): v for k, v in draw_result.items()}
        session["settings"] = {
            "matches": matches,
            "courts": courts,
            "start_time": settings["start_time"],
            "game_minutes": game_minutes,
            "break_minutes": break_minutes,
            "playoff_size": playoff_size,
            "gender": gender,
            "tournament_name": tournament_name,
        }
        session["info"] = {
            "n_players": n_players,
            "matches": matches,
            "courts": courts,
            "game_minutes": game_minutes,
            "break_minutes": break_minutes,
            "gender": gender,
            "tournament_name": tournament_name,
            "date": datetime.now().strftime("%d.%m.%Y"),
        }

        return render_template(
            "preview.html",
            schedule=schedule_data,
            draw_result=draw_result,
            info=session["info"],
            rules_text=Config.DRAW_RULES_TEXT,
        )

    except ValueError as e:
        draw_result_raw = session.get("draw_result", {})
        draw_result = {int(k): v for k, v in draw_result_raw.items()} if draw_result_raw else None
        matches = session.get("settings", {}).get("matches", 1)
        courts = session.get("settings", {}).get("courts", 2)
        gender = session.get("settings", {}).get("gender", "W")
        tournament_name = session.get("settings", {}).get("tournament_name", "")
        n_players = len(draw_result) if draw_result else 0
        return render_template(
            "index.html",
            draw_result=draw_result, matches=matches, courts=courts, gender=gender,
            tournament_name=tournament_name,
            n_players=n_players,
            error=str(e),
            rules_text=Config.DRAW_RULES_TEXT,
            **_build_schemes(draw_result, matches),
        )
    except Exception as e:
        return render_template(
            "index.html",
            draw_result=None, matches=1, courts=2, gender="W",
            tournament_name="",
            n_players=0,
            error=f"Ошибка: {e}",
            rules_text=Config.DRAW_RULES_TEXT,
            **_empty_schemes(),
        )


# ============================================================
# СКАЧИВАНИЕ
# ============================================================

@main_bp.route("/download", methods=["GET"])
def download():
    try:
        schedule_data = session.get("schedule_data")
        draw_result_raw = session.get("draw_result")
        info = session.get("info")
        if not schedule_data or not draw_result_raw or not info:
            return redirect(url_for("main.index"))

        draw_result = {int(k): v for k, v in draw_result_raw.items()}

        settings = session.get("settings", {})
        cfg = TournamentConfig(
            matches_per_player=info["matches"],
            courts=info["courts"],
            start_time=parse_time(settings.get("start_time", "09:00")),
            game_minutes=info["game_minutes"],
            break_minutes=info["break_minutes"],
            playoff_size=settings.get("playoff_size", 4),
            gender=settings.get("gender", "W"),
            tournament_name=settings.get("tournament_name", ""),
        )

        matches_list = [_deserialize_match(d) for d in schedule_data]
        schedule_obj = Schedule(matches=matches_list, players=draw_result, config=cfg)

        buffer = export_to_docx(schedule_obj, draw_result, Config.DRAW_RULES_TEXT)

        filename = f"расписание_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        return f"Ошибка при скачивании: {e}", 500


# ============================================================
# ШАБЛОН
# ============================================================

@main_bp.route("/template", methods=["GET"])
def template():
    try:
        schedule_data = session.get("schedule_data")
        info = session.get("info")
        if not schedule_data or not info:
            return redirect(url_for("main.index"))

        draw_result_raw = session.get("draw_result", {})
        draw_result = {int(k): v for k, v in draw_result_raw.items()}

        settings = session.get("settings", {})
        cfg = TournamentConfig(
            matches_per_player=info["matches"],
            courts=info["courts"],
            start_time=parse_time(settings.get("start_time", "09:00")),
            game_minutes=info["game_minutes"],
            break_minutes=info["break_minutes"],
            playoff_size=settings.get("playoff_size", 4),
            gender=settings.get("gender", "W"),
            tournament_name=settings.get("tournament_name", ""),
        )

        matches_list = [_deserialize_match(d) for d in schedule_data]
        schedule_obj = Schedule(matches=matches_list, players=draw_result, config=cfg)

        buffer = export_template_docx(schedule_obj)

        filename = f"шаблон_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except Exception as e:
        return f"Ошибка: {e}", 500


# ============================================================
# СБРОС
# ============================================================

@main_bp.route("/reset", methods=["POST"])
def reset():
    session.clear()
    return redirect(url_for("main.index"))