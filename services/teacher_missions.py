
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import uuid

import streamlit as st


DATA_DIR = Path("data")
MISSIONS_FILE = DATA_DIR / "teacher_missions.json"


DEFAULT_MISSIONS = [
    {
        "id": "default-south-coast",
        "title": "Suðurstrandarleiðangur",
        "subject": "Landafræði",
        "level": "20 mín hópverkefni",
        "points": 35,
        "focus": "Staðir + veður + færð",
        "prompt": "Veljið þrjá staði á Suðurlandi og metið hvaða staður hentar best fyrir dagsferð frá Vallaskóla í dag.",
        "checklist": [
            "Veljið þrjá staði á Suðurlandi.",
            "Skoðið veður eða færð.",
            "Berið saman fjarlægð frá Vallaskóla.",
            "Gefið grænt/gult/rautt ferðaljós.",
            "Rökstyðjið niðurstöðu með gögnum."
        ],
        "teacher_hint": "Hentar vel þegar nemendur eru að æfa áttir, fjarlægðir og gagnaúrvinnslu.",
        "created_at": "default",
    },
    {
        "id": "default-population-compare",
        "title": "Mannfjöldaspæjarar",
        "subject": "Samfélagsfræði",
        "level": "10 mín hraðáskorun",
        "points": 25,
        "focus": "Hagstofa + staðir",
        "prompt": "Veljið tvo staði og berið saman mannfjölda, landshluta og fjarlægð frá Vallaskóla.",
        "checklist": [
            "Veljið tvo staði.",
            "Skráið mannfjölda beggja staða.",
            "Segið hvor er nær Vallaskóla.",
            "Skrifið eina ályktun."
        ],
        "teacher_hint": "Gott sem upphitun í byrjun tíma.",
        "created_at": "default",
    },
]


def _ensure_file():
    DATA_DIR.mkdir(exist_ok=True)
    if not MISSIONS_FILE.exists():
        MISSIONS_FILE.write_text(json.dumps(DEFAULT_MISSIONS, ensure_ascii=False, indent=2), encoding="utf-8")


def load_teacher_missions() -> list[dict]:
    _ensure_file()
    try:
        data = json.loads(MISSIONS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return DEFAULT_MISSIONS.copy()


def save_teacher_missions(missions: list[dict]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    MISSIONS_FILE.write_text(json.dumps(missions, ensure_ascii=False, indent=2), encoding="utf-8")


def create_teacher_mission(title: str, subject: str, level: str, points: int, focus: str, prompt: str, checklist_text: str, teacher_hint: str) -> dict:
    checklist = [line.strip("-• 	") for line in checklist_text.splitlines() if line.strip()]
    if not checklist:
        checklist = ["Skoðið gögn.", "Rökstyðjið niðurstöðu.", "Skilið svari."]

    return {
        "id": str(uuid.uuid4()),
        "title": title.strip() or "Ný áskorun",
        "subject": subject,
        "level": level,
        "points": int(points),
        "focus": focus.strip() or "Landafræði",
        "prompt": prompt.strip(),
        "checklist": checklist,
        "teacher_hint": teacher_hint.strip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def add_teacher_mission(mission: dict) -> None:
    missions = load_teacher_missions()
    missions.insert(0, mission)
    save_teacher_missions(missions)


def delete_teacher_mission(mission_id: str) -> bool:
    missions = load_teacher_missions()
    new_missions = [m for m in missions if m.get("id") != mission_id or str(m.get("id", "")).startswith("default-")]
    # Do not delete default missions with this method.
    if len(new_missions) == len(missions):
        return False
    save_teacher_missions(new_missions)
    return True


def mission_to_challenge(mission: dict) -> dict:
    return {
        "kind": "teacher_mission",
        "title": f"👨‍🏫 {mission.get('title', 'Kennaraáskorun')}",
        "points": int(mission.get("points", 25)),
        "prompt": mission.get("prompt", ""),
        "data": [],
        "checklist": mission.get("checklist", []),
        "teacher_hint": mission.get("teacher_hint", ""),
        "teacher_mission_id": mission.get("id", ""),
        "focus": mission.get("focus", ""),
        "level": mission.get("level", ""),
        "subject": mission.get("subject", ""),
    }


def export_missions_json() -> str:
    return json.dumps(load_teacher_missions(), ensure_ascii=False, indent=2)


def import_missions_json(text: str) -> tuple[bool, str]:
    try:
        data = json.loads(text)
        if not isinstance(data, list):
            return False, "JSON þarf að vera listi af verkefnum."
        cleaned = []
        for item in data:
            if not isinstance(item, dict):
                continue
            item.setdefault("id", str(uuid.uuid4()))
            item.setdefault("title", "Innflutt áskorun")
            item.setdefault("points", 25)
            item.setdefault("checklist", ["Skoðið gögn.", "Rökstyðjið."])
            cleaned.append(item)
        if not cleaned:
            return False, "Engin gild verkefni fundust."
        save_teacher_missions(cleaned)
        return True, f"Flutti inn {len(cleaned)} verkefni."
    except Exception as e:
        return False, f"Villa við innflutning: {e}"
