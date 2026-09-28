"""Fetch today's events from a Google Calendar secret ICS URL."""

from __future__ import annotations

from datetime import date, datetime, timezone
from urllib.request import Request, urlopen


def fetch_today_events(ics_url: str, day: date | None = None) -> list[dict]:
    if not ics_url or not ics_url.strip():
        return []
    day = day or date.today()
    req = Request(ics_url.strip(), headers={"User-Agent": "Dayboard/0.1"})
    with urlopen(req, timeout=20) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    return [e for e in _parse_ics(text) if e["day"] == day.isoformat()]


def _unfold(text: str) -> str:
    return text.replace("\r\n ", "").replace("\n ", "").replace("\r\n", "\n")


def _parse_ics(text: str) -> list[dict]:
    events: list[dict] = []
    current: dict[str, str] = {}
    for raw in _unfold(text).split("\n"):
        line = raw.strip()
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT":
            parsed = _event_from(current)
            if parsed:
                events.append(parsed)
            current = {}
        elif ":" in line and current is not None:
            key, val = line.split(":", 1)
            name = key.split(";")[0].upper()
            current[name] = val.replace("\\,", ",").replace("\\n", " ")
    return events


def _event_from(fields: dict[str, str]) -> dict | None:
    raw = fields.get("DTSTART") or fields.get("DTSTART;VALUE=DATE")
    if not raw:
        for k, v in fields.items():
            if k.startswith("DTSTART"):
                raw = v
                break
    if not raw:
        return None
    title = fields.get("SUMMARY") or "(no title)"
    day, time_label = _when(raw)
    return {"title": title, "day": day, "start_time": time_label, "source": "google"}


def _when(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if raw.endswith("Z") and len(raw) >= 15:
        dt = datetime.strptime(raw, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        local = dt.astimezone()
        return local.date().isoformat(), local.strftime("%H:%M")
    if "T" in raw:
        body = raw.split("T", 1)
        day = f"{body[0][0:4]}-{body[0][4:6]}-{body[0][6:8]}"
        hhmm = body[1][:4]
        return day, f"{hhmm[0:2]}:{hhmm[2:4]}"
    if len(raw) >= 8:
        return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}", ""
    return date.today().isoformat(), ""
