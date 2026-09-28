# Dayboard

Local-first self-management app for macOS.

Tasks, habits, a Pomodoro timer, a simple calendar, and a daily journal — one Python desktop window. Nothing leaves your machine. No account.

## Features

- **Today To Do** — tasks due today (or undated open tasks); add and complete them on the Today page
- **Google Calendar** — paste the calendar secret ICS URL; today's events show on Today and on the wallpaper
- **Desktop wallpaper widget** — month calendar + Today To Do + schedule, then set as the macOS wallpaper
- **Today** — snapshot of habits, focus sessions, events, and today's reflection
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

## Google Calendar

1. Open [Google Calendar](https://calendar.google.com) → Settings → select your calendar.
2. Under **Integrate calendar**, copy **Secret address in iCal format**.
3. Paste it on the Dayboard **Today** page and click **Save & refresh**.

The secret ICS URL stays in `data/settings.json` on your Mac and is gitignored.

## Desktop wallpaper

On the **Today** page click **Generate & set wallpaper**. Dayboard writes `data/dayboard-wallpaper.png` and, on macOS, sets it as the desktop picture.

## License

MIT
