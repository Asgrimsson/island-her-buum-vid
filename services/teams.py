
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


DATA_PATH = Path("data/teams.json")


def _ensure_file():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text("[]", encoding="utf-8")


def load_teams() -> list[dict[str, Any]]:
    _ensure_file()
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_teams(teams: list[dict[str, Any]]) -> None:
    _ensure_file()
    DATA_PATH.write_text(json.dumps(teams, ensure_ascii=False, indent=2), encoding="utf-8")


def teams_df() -> pd.DataFrame:
    teams = load_teams()
    if not teams:
        return pd.DataFrame(columns=["name", "class_name", "points", "missions", "badges", "created_at", "updated_at"])
    return pd.DataFrame(teams).sort_values(["points", "missions"], ascending=[False, False])


def add_team(name: str, class_name: str = "") -> tuple[bool, str]:
    name = name.strip()
    class_name = class_name.strip()
    if not name:
        return False, "Vantar nafn á lið."
    teams = load_teams()
    if any(t["name"].lower() == name.lower() for t in teams):
        return False, "Þetta lið er þegar til."

    now = datetime.now().isoformat(timespec="seconds")
    teams.append({
        "name": name,
        "class_name": class_name,
        "points": 0,
        "missions": 0,
        "badges": [],
        "history": [],
        "created_at": now,
        "updated_at": now,
    })
    save_teams(teams)
    return True, f"Liðið {name} var búið til."


def award_points(team_name: str, points: int, reason: str = "Mission") -> tuple[bool, str]:
    teams = load_teams()
    now = datetime.now().isoformat(timespec="seconds")
    for t in teams:
        if t["name"] == team_name:
            t["points"] = int(t.get("points", 0)) + int(points)
            t["missions"] = int(t.get("missions", 0)) + 1
            t["updated_at"] = now
            t.setdefault("history", []).append({
                "time": now,
                "points": int(points),
                "reason": reason,
            })

            badges = set(t.get("badges", []))
            total = t["points"]
            if total >= 50:
                badges.add("Kortakönnuðir")
            if total >= 100:
                badges.add("Veðurvaktin")
            if total >= 200:
                badges.add("Mission Meistarar")
            if t["missions"] >= 5:
                badges.add("Úthaldsteymi")
            t["badges"] = sorted(badges)
            save_teams(teams)
            return True, f"{team_name} fékk {points} stig."
    return False, "Lið fannst ekki."


def reset_all() -> None:
    save_teams([])
