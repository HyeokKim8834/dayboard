"""SQLite persistence. All data stays on your Mac."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "dayboard.db"


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                notes TEXT DEFAULT '',
                due_date TEXT,
                priority INTEGER DEFAULT 1,
                done INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT DEFAULT '#3B82F6',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                day TEXT NOT NULL,
                UNIQUE(habit_id, day),
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                day TEXT NOT NULL,
                start_time TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS journal (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL UNIQUE,
                mood TEXT DEFAULT '',
                body TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                minutes INTEGER NOT NULL,
                finished_at TEXT NOT NULL
            );
            """
        )


def today_iso() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def add_task(title: str, due_date: str | None = None, priority: int = 1) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO tasks (title, due_date, priority, created_at) VALUES (?, ?, ?, ?)",
            (title.strip(), due_date, priority, now_iso()),
        )


def list_tasks(include_done: bool = True) -> list[sqlite3.Row]:
    q = "SELECT * FROM tasks"
    if not include_done:
        q += " WHERE done = 0"
    q += " ORDER BY done, due_date IS NULL, due_date, priority DESC, id DESC"
    with connect() as conn:
        return list(conn.execute(q))


def toggle_task(task_id: int) -> None:
    with connect() as conn:
        conn.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))


def delete_task(task_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def add_habit(name: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO habits (name, created_at) VALUES (?, ?)",
            (name.strip(), now_iso()),
        )


def list_habits() -> list[sqlite3.Row]:
    with connect() as conn:
        return list(conn.execute("SELECT * FROM habits ORDER BY id"))


def delete_habit(habit_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))


def habit_done_today(habit_id: int) -> bool:
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM habit_logs WHERE habit_id = ? AND day = ?",
            (habit_id, today_iso()),
        ).fetchone()
        return row is not None


def toggle_habit_today(habit_id: int) -> None:
    day = today_iso()
    with connect() as conn:
        row = conn.execute(
            "SELECT id FROM habit_logs WHERE habit_id = ? AND day = ?",
            (habit_id, day),
        ).fetchone()
        if row:
            conn.execute("DELETE FROM habit_logs WHERE id = ?", (row["id"],))
        else:
            conn.execute(
                "INSERT INTO habit_logs (habit_id, day) VALUES (?, ?)",
                (habit_id, day),
            )


def habit_streak(habit_id: int) -> int:
    with connect() as conn:
        rows = conn.execute(
            "SELECT day FROM habit_logs WHERE habit_id = ? ORDER BY day DESC",
            (habit_id,),
        ).fetchall()
    days = {r["day"] for r in rows}
    if not days:
        return 0
    streak = 0
    d = date.today()
    if d.isoformat() not in days:
        d = d - timedelta(days=1)
    while d.isoformat() in days:
        streak += 1
        d = d - timedelta(days=1)
    return streak


def add_event(title: str, day: str, start_time: str = "", notes: str = "") -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO events (title, day, start_time, notes) VALUES (?, ?, ?, ?)",
            (title.strip(), day, start_time, notes),
        )


def list_events(day: str) -> list[sqlite3.Row]:
    with connect() as conn:
        return list(
            conn.execute(
                "SELECT * FROM events WHERE day = ? ORDER BY start_time, id",
                (day,),
            )
        )


def delete_event(event_id: int) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM events WHERE id = ?", (event_id,))


def get_journal(day: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute("SELECT * FROM journal WHERE day = ?", (day,)).fetchone()


def save_journal(day: str, mood: str, body: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO journal (day, mood, body) VALUES (?, ?, ?)
            ON CONFLICT(day) DO UPDATE SET mood = excluded.mood, body = excluded.body
            """,
            (day, mood, body),
        )


def log_pomodoro(kind: str, minutes: int) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO pomodoro_sessions (kind, minutes, finished_at) VALUES (?, ?, ?)",
            (kind, minutes, now_iso()),
        )


def pomodoro_today_count() -> int:
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM pomodoro_sessions WHERE kind = 'focus' AND finished_at LIKE ?",
            (today_iso() + "%",),
        ).fetchone()
        return int(row["n"]) if row else 0
