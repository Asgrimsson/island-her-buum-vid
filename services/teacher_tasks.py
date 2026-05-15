
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


DATA_PATH = Path("data/tasks.json")


def _ensure_file():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text("[]", encoding="utf-8")


def load_tasks() -> list[dict[str, Any]]:
    _ensure_file()
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_tasks(tasks: list[dict[str, Any]]) -> None:
    _ensure_file()
    DATA_PATH.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def add_task(title: str, subject: str, duration: str, body: str, target: str = "Allir hópar") -> tuple[bool, str]:
    title = title.strip()
    body = body.strip()
    if not title:
        return False, "Vantar titil á verkefni."
    if not body:
        return False, "Vantar verkefnalýsingu."

    tasks = load_tasks()
    now = datetime.now().isoformat(timespec="seconds")
    task = {
        "id": f"task-{int(datetime.now().timestamp())}",
        "title": title,
        "subject": subject,
        "duration": duration,
        "target": target,
        "body": body,
        "status": "Virkt",
        "created_at": now,
        "updated_at": now,
    }
    tasks.insert(0, task)
    save_tasks(tasks)
    return True, "Verkefni vistað."


def update_task_status(task_id: str, status: str) -> tuple[bool, str]:
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = status
            t["updated_at"] = datetime.now().isoformat(timespec="seconds")
            save_tasks(tasks)
            return True, "Staða verkefnis uppfærð."
    return False, "Verkefni fannst ekki."


def delete_task(task_id: str) -> tuple[bool, str]:
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        return False, "Verkefni fannst ekki."
    save_tasks(new_tasks)
    return True, "Verkefni eytt."


def tasks_df() -> pd.DataFrame:
    tasks = load_tasks()
    if not tasks:
        return pd.DataFrame(columns=["title", "subject", "duration", "target", "status", "created_at"])
    return pd.DataFrame(tasks)
