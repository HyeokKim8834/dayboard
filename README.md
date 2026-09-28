# Dayboard

Local-first self-management app for macOS.

Tasks, habits, a Pomodoro timer, a simple calendar, and a daily journal — one Python desktop window. Nothing leaves your machine. No account.

Built as a GitHub-ready MVP you can run today and extend.

## Features

- **Today** — snapshot of open tasks, habits, focus sessions, events, and today's reflection
- **Tasks** — add, complete, delete; optional due date (`YYYY-MM-DD`)
- **Habits** — daily check-off and current streak
- **Focus** — 25 / 5 / 15 minute timer; completed focus blocks are logged
- **Calendar** — month grid + per-day events
- **Journal** — mood + free-text reflection for today

Storage is a local SQLite file at `data/dayboard.db`.

## Requirements

- macOS
- Python 3.10+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

## Run on a Mac

```bash
git clone https://github.com/HyeokKim8834/dayboard.git
cd dayboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

If macOS blocks the window toolkit the first time, allow it under **System Settings → Privacy & Security**.

## Project layout

```
dayboard/
├── run.py              # entry point
├── requirements.txt
├── app/
│   ├── main.py         # UI
│   └── db.py           # SQLite helpers
└── data/               # created on first launch (ignored by git except .gitkeep)
```

## Why Python (not Swift)?

This repo is meant to ship a working Mac app quickly with a small learning curve. The UI uses CustomTkinter so it looks acceptable in dark mode without Xcode.

A later native SwiftUI port is a good follow-up if you want menu-bar integration, notifications, and a signed `.app`.

## Roadmap

- Menu bar timer + native notifications
- Recurring tasks and habits on selected weekdays
- Export journal / tasks to Markdown
- Optional iCloud or folder sync of `dayboard.db`
- Packaged `.app` via PyInstaller or Briefcase

## License

MIT
