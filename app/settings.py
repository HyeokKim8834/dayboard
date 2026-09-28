"""Simple JSON settings (Google Calendar ICS URL, etc.)."""

from __future__ import annotations

import json

from app.db import DATA_DIR

PATH = DATA_DIR / "settings.json"

DEFAULTS = {"google_ics_url": ""}


def load() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PATH.exists():
        return dict(DEFAULTS)
    try:
        data = json.loads(PATH.read_text())
    except json.JSONDecodeError:
        return dict(DEFAULTS)
    out = dict(DEFAULTS)
    out.update(data)
    return out


def save(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    current = load()
    current.update(data)
    PATH.write_text(json.dumps(current, indent=2))
