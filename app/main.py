"""Dayboard desktop app (CustomTkinter)."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

import customtkinter as ctk

from app import db

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

NAV = [
    ("Today", "today"),
    ("Tasks", "tasks"),
    ("Habits", "habits"),
    ("Focus", "focus"),
    ("Calendar", "calendar"),
    ("Journal", "journal"),
]

MOODS = ["", "Great", "Good", "Okay", "Low", "Tired"]


class DayboardApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        db.init_db()
        self.title("Dayboard")
        self.geometry("1100x720")
        self.minsize(900, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._pomodoro_remaining = 25 * 60
        self._pomodoro_running = False
        self._pomodoro_kind = "focus"
        self._pomodoro_job = None
        self._cal_cursor = date.today().replace(day=1)
        self._selected_day = date.today()

        self._build_sidebar()
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(1, weight=1)

        self.show("today")

    def _build_sidebar(self) -> None:
        bar = ctk.CTkFrame(self, width=200, corner_radius=0)
        bar.grid(row=0, column=0, sticky="nsw")
        bar.grid_propagate(False)

        ctk.CTkLabel(bar, text="DAYBOARD", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=(24, 4)
        )
        ctk.CTkLabel(
            bar, text="local · private · macOS", font=ctk.CTkFont(size=11), text_color="gray"
        ).pack(pady=(0, 20))

        for label, key in NAV:
            btn = ctk.CTkButton(
                bar,
                text=label,
                anchor="w",
                fg_color="transparent",
                command=lambda k=key: self.show(k),
            )
            btn.pack(fill="x", padx=12, pady=4)

        ctk.CTkLabel(
            bar,
            text="Data stays in ./data\nNo account. No cloud.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left",
        ).pack(side="bottom", pady=20, padx=16)

    def _clear(self) -> None:
        for w in self.content.winfo_children():
            w.destroy()

    def show(self, key: str) -> None:
        self._clear()
        getattr(self, f"_page_{key}")()

    def _header(self, title: str, subtitle: str = "") -> None:
        ctk.CTkLabel(self.content, text=title, font=ctk.CTkFont(size=26, weight="bold")).grid(
            row=0, column=0, sticky="w"
        )
        if subtitle:
            ctk.CTkLabel(self.content, text=subtitle, text_color="gray").grid(
                row=0, column=0, sticky="e"
            )

    def _page_today(self) -> None:
        today = date.today().strftime("%A, %B %d")
        self._header("Today", today)

        body = ctk.CTkScrollableFrame(self.content)
        body.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        body.grid_columnconfigure((0, 1), weight=1)

        open_tasks = [t for t in db.list_tasks() if not t["done"]]
        habits = db.list_habits()
        done_habits = sum(1 for h in habits if db.habit_done_today(h["id"]))
        focus_n = db.pomodoro_today_count()
        events = db.list_events(db.today_iso())
        journal = db.get_journal(db.today_iso())

        stats = [
            ("Open tasks", str(len(open_tasks))),
            ("Habits today", f"{done_habits}/{len(habits)}" if habits else "0"),
            ("Focus sessions", str(focus_n)),
            ("Events", str(len(events))),
        ]
        stat_row = ctk.CTkFrame(body, fg_color="transparent")
        stat_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        for i, (label, value) in enumerate(stats):
            card = ctk.CTkFrame(stat_row)
            card.grid(row=0, column=i, padx=6, sticky="ew")
            stat_row.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold")).pack(
                pady=(12, 0)
            )
            ctk.CTkLabel(card, text=label, text_color="gray").pack(pady=(0, 12))

        left = ctk.CTkFrame(body)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(left, text="Focus list", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        if not open_tasks:
            ctk.CTkLabel(left, text="No open tasks. Nice.", text_color="gray").pack(
                padx=12, pady=8, anchor="w"
            )
        for t in open_tasks[:8]:
            due = f"  ·  {t['due_date']}" if t["due_date"] else ""
            ctk.CTkLabel(left, text=f"☐  {t['title']}{due}").pack(anchor="w", padx=12, pady=2)

        right = ctk.CTkFrame(body)
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(right, text="Today on calendar", font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        if not events:
            ctk.CTkLabel(right, text="Nothing scheduled.", text_color="gray").pack(
                padx=12, pady=8, anchor="w"
            )
        for e in events:
            when = e["start_time"] or "all day"
            ctk.CTkLabel(right, text=f"{when}  {e['title']}").pack(anchor="w", padx=12, pady=2)

        note = (journal["body"][:180] + "…") if journal and journal["body"] else "No journal entry yet."
        mood = journal["mood"] if journal and journal["mood"] else "—"
        jcard = ctk.CTkFrame(body)
        jcard.grid(row=2, column=0, columnspan=2, sticky="ew", pady=16)
        ctk.CTkLabel(jcard, text=f"Reflection  ·  mood: {mood}", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        ctk.CTkLabel(jcard, text=note, wraplength=800, justify="left").pack(
            anchor="w", padx=12, pady=(0, 12)
        )

    def _page_tasks(self) -> None:
        self._header("Tasks", "Local list · due dates optional")

        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(1, weight=1)

        form = ctk.CTkFrame(wrap)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._task_entry = ctk.CTkEntry(form, placeholder_text="New task…", width=360)
        self._task_entry.pack(side="left", padx=8, pady=10)
        self._task_due = ctk.CTkEntry(form, placeholder_text="Due YYYY-MM-DD", width=160)
        self._task_due.pack(side="left", padx=8)
        ctk.CTkButton(form, text="Add", width=80, command=self._add_task).pack(side="left", padx=8)

        self._task_list = ctk.CTkScrollableFrame(wrap)
        self._task_list.grid(row=1, column=0, sticky="nsew")
        self._render_tasks()

    def _add_task(self) -> None:
        title = self._task_entry.get().strip()
        if not title:
            return
        due = self._task_due.get().strip() or None
        db.add_task(title, due)
        self._task_entry.delete(0, "end")
        self._render_tasks()

    def _render_tasks(self) -> None:
        for w in self._task_list.winfo_children():
            w.destroy()
        for t in db.list_tasks():
            row = ctk.CTkFrame(self._task_list)
            row.pack(fill="x", pady=3, padx=4)
            mark = "☑" if t["done"] else "☐"
            due = t["due_date"] or ""
            label = f"{mark}  {t['title']}"
            if due:
                label += f"    {due}"
            ctk.CTkLabel(row, text=label, anchor="w").pack(side="left", padx=10, pady=8)
            ctk.CTkButton(
                row, text="Toggle", width=70, command=lambda i=t["id"]: self._toggle_task(i)
            ).pack(side="right", padx=4)
            ctk.CTkButton(
                row,
                text="Delete",
                width=70,
                fg_color="#7F1D1D",
                command=lambda i=t["id"]: self._del_task(i),
            ).pack(side="right", padx=4)

    def _toggle_task(self, task_id: int) -> None:
        db.toggle_task(task_id)
        self._render_tasks()

    def _del_task(self, task_id: int) -> None:
        db.delete_task(task_id)
        self._render_tasks()

    def _page_habits(self) -> None:
        self._header("Habits", "Check off once per day")

        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(1, weight=1)

        form = ctk.CTkFrame(wrap)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._habit_entry = ctk.CTkEntry(form, placeholder_text="New habit…", width=320)
        self._habit_entry.pack(side="left", padx=8, pady=10)
        ctk.CTkButton(form, text="Add habit", command=self._add_habit).pack(side="left", padx=8)

        self._habit_list = ctk.CTkScrollableFrame(wrap)
        self._habit_list.grid(row=1, column=0, sticky="nsew")
        self._render_habits()

    def _add_habit(self) -> None:
        name = self._habit_entry.get().strip()
        if not name:
            return
        db.add_habit(name)
        self._habit_entry.delete(0, "end")
        self._render_habits()

    def _render_habits(self) -> None:
        for w in self._habit_list.winfo_children():
            w.destroy()
        for h in db.list_habits():
            done = db.habit_done_today(h["id"])
            streak = db.habit_streak(h["id"])
            row = ctk.CTkFrame(self._habit_list)
            row.pack(fill="x", pady=4, padx=4)
            status = "Done today" if done else "Not yet"
            ctk.CTkLabel(
                row,
                text=f"{h['name']}    ·    streak {streak}    ·    {status}",
                anchor="w",
            ).pack(side="left", padx=10, pady=10)
            ctk.CTkButton(
                row,
                text="Check" if not done else "Undo",
                width=80,
                command=lambda i=h["id"]: self._toggle_habit(i),
            ).pack(side="right", padx=4)
            ctk.CTkButton(
                row,
                text="Delete",
                width=70,
                fg_color="#7F1D1D",
                command=lambda i=h["id"]: self._del_habit(i),
            ).pack(side="right", padx=4)

    def _toggle_habit(self, habit_id: int) -> None:
        db.toggle_habit_today(habit_id)
        self._render_habits()

    def _del_habit(self, habit_id: int) -> None:
        db.delete_habit(habit_id)
        self._render_habits()

    def _page_focus(self) -> None:
        self._header("Focus", f"Completed today: {db.pomodoro_today_count()}")

        box = ctk.CTkFrame(self.content)
        box.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

        self._timer_label = ctk.CTkLabel(
            box, text=self._fmt(self._pomodoro_remaining), font=ctk.CTkFont(size=64, weight="bold")
        )
        self._timer_label.pack(pady=(48, 8))
        self._kind_label = ctk.CTkLabel(box, text=self._pomodoro_kind.upper(), text_color="gray")
        self._kind_label.pack()

        btns = ctk.CTkFrame(box, fg_color="transparent")
        btns.pack(pady=24)
        ctk.CTkButton(btns, text="Focus 25", command=lambda: self._set_timer("focus", 25)).pack(
            side="left", padx=6
        )
        ctk.CTkButton(btns, text="Short 5", command=lambda: self._set_timer("break", 5)).pack(
            side="left", padx=6
        )
        ctk.CTkButton(btns, text="Long 15", command=lambda: self._set_timer("break", 15)).pack(
            side="left", padx=6
        )

        ctrl = ctk.CTkFrame(box, fg_color="transparent")
        ctrl.pack(pady=8)
        ctk.CTkButton(ctrl, text="Start / Pause", width=140, command=self._toggle_timer).pack(
            side="left", padx=6
        )
        ctk.CTkButton(ctrl, text="Reset", width=100, fg_color="#374151", command=self._reset_timer).pack(
            side="left", padx=6
        )

        ctk.CTkLabel(
            box,
            text="When a focus block finishes it is logged locally.",
            text_color="gray",
        ).pack(pady=20)

    def _fmt(self, seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _set_timer(self, kind: str, minutes: int) -> None:
        self._pomodoro_running = False
        if self._pomodoro_job:
            self.after_cancel(self._pomodoro_job)
            self._pomodoro_job = None
        self._pomodoro_kind = kind
        self._pomodoro_remaining = minutes * 60
        if hasattr(self, "_timer_label"):
            self._timer_label.configure(text=self._fmt(self._pomodoro_remaining))
            self._kind_label.configure(text=kind.upper())

    def _toggle_timer(self) -> None:
        self._pomodoro_running = not self._pomodoro_running
        if self._pomodoro_running:
            self._tick()

    def _reset_timer(self) -> None:
        minutes = 25 if self._pomodoro_kind == "focus" else 5
        self._set_timer(self._pomodoro_kind, minutes)

    def _tick(self) -> None:
        if not self._pomodoro_running:
            return
        if self._pomodoro_remaining <= 0:
            self._pomodoro_running = False
            if self._pomodoro_kind == "focus":
                db.log_pomodoro("focus", 25)
            try:
                self.bell()
            except Exception:
                pass
            if hasattr(self, "_kind_label"):
                self._kind_label.configure(text="DONE")
            return
        self._pomodoro_remaining -= 1
        if hasattr(self, "_timer_label"):
            self._timer_label.configure(text=self._fmt(self._pomodoro_remaining))
        self._pomodoro_job = self.after(1000, self._tick)

    def _page_calendar(self) -> None:
        self._header("Calendar", self._cal_cursor.strftime("%B %Y"))

        wrap = ctk.CTkFrame(self.content, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        wrap.grid_columnconfigure(1, weight=1)
        wrap.grid_rowconfigure(1, weight=1)

        nav = ctk.CTkFrame(wrap)
        nav.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ctk.CTkButton(nav, text="<", width=40, command=self._cal_prev).pack(side="left", padx=6, pady=8)
        ctk.CTkButton(nav, text=">", width=40, command=self._cal_next).pack(side="left")
        ctk.CTkButton(nav, text="Today", width=80, command=self._cal_today).pack(side="left", padx=8)

        grid = ctk.CTkFrame(wrap)
        grid.grid(row=1, column=0, sticky="nsw", padx=(0, 12))
        for i, name in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ctk.CTkLabel(grid, text=name, width=36).grid(row=0, column=i, padx=2, pady=4)

        cal = calendar.Calendar(firstweekday=0)
        weeks = cal.monthdatescalendar(self._cal_cursor.year, self._cal_cursor.month)
        for r, week in enumerate(weeks, start=1):
            for c, d in enumerate(week):
                in_month = d.month == self._cal_cursor.month
                fg = None if in_month else "gray"
                is_sel = d == self._selected_day
                btn = ctk.CTkButton(
                    grid,
                    text=str(d.day),
                    width=36,
                    height=32,
                    fg_color="#1D4ED8" if is_sel else "transparent",
                    text_color=fg or ("white" if is_sel else None),
                    command=lambda day=d: self._select_day(day),
                )
                btn.grid(row=r, column=c, padx=2, pady=2)

        side = ctk.CTkFrame(wrap)
        side.grid(row=1, column=1, sticky="nsew")
        ctk.CTkLabel(
            side,
            text=self._selected_day.isoformat(),
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        form = ctk.CTkFrame(side, fg_color="transparent")
        form.pack(fill="x", padx=12)
        self._ev_title = ctk.CTkEntry(form, placeholder_text="Event title")
        self._ev_title.pack(fill="x", pady=4)
        self._ev_time = ctk.CTkEntry(form, placeholder_text="Time e.g. 14:00")
        self._ev_time.pack(fill="x", pady=4)
        ctk.CTkButton(form, text="Add event", command=self._add_event).pack(anchor="w", pady=6)

        self._ev_list = ctk.CTkScrollableFrame(side)
        self._ev_list.pack(fill="both", expand=True, padx=12, pady=8)
        self._render_events()

    def _cal_prev(self) -> None:
        first = self._cal_cursor
        self._cal_cursor = (first.replace(day=1) - timedelta(days=1)).replace(day=1)
        self.show("calendar")

    def _cal_next(self) -> None:
        year, month = self._cal_cursor.year, self._cal_cursor.month
        if month == 12:
            self._cal_cursor = date(year + 1, 1, 1)
        else:
            self._cal_cursor = date(year, month + 1, 1)
        self.show("calendar")

    def _cal_today(self) -> None:
        self._selected_day = date.today()
        self._cal_cursor = date.today().replace(day=1)
        self.show("calendar")

    def _select_day(self, d: date) -> None:
        self._selected_day = d
        self.show("calendar")

    def _add_event(self) -> None:
        title = self._ev_title.get().strip()
        if not title:
            return
        db.add_event(title, self._selected_day.isoformat(), self._ev_time.get().strip())
        self._ev_title.delete(0, "end")
        self._ev_time.delete(0, "end")
        self._render_events()

    def _render_events(self) -> None:
        for w in self._ev_list.winfo_children():
            w.destroy()
        rows = db.list_events(self._selected_day.isoformat())
        if not rows:
            ctk.CTkLabel(self._ev_list, text="No events.", text_color="gray").pack(anchor="w")
            return
        for e in rows:
            row = ctk.CTkFrame(self._ev_list)
            row.pack(fill="x", pady=3)
            when = e["start_time"] or "all day"
            ctk.CTkLabel(row, text=f"{when}  {e['title']}").pack(side="left", padx=8, pady=6)
            ctk.CTkButton(
                row,
                text="×",
                width=32,
                fg_color="#7F1D1D",
                command=lambda i=e["id"]: self._del_event(i),
            ).pack(side="right", padx=6)

    def _del_event(self, event_id: int) -> None:
        db.delete_event(event_id)
        self._render_events()

    def _page_journal(self) -> None:
        self._header("Journal", db.today_iso())

        wrap = ctk.CTkFrame(self.content)
        wrap.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(2, weight=1)

        existing = db.get_journal(db.today_iso())
        ctk.CTkLabel(wrap, text="Mood").grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))
        self._mood = ctk.CTkOptionMenu(wrap, values=MOODS)
        self._mood.grid(row=1, column=0, sticky="w", padx=12)
        if existing and existing["mood"]:
            self._mood.set(existing["mood"])

        self._journal = ctk.CTkTextbox(wrap, wrap="word")
        self._journal.grid(row=2, column=0, sticky="nsew", padx=12, pady=12)
        if existing and existing["body"]:
            self._journal.insert("1.0", existing["body"])

        ctk.CTkButton(wrap, text="Save today's reflection", command=self._save_journal).grid(
            row=3, column=0, sticky="w", padx=12, pady=(0, 16)
        )

    def _save_journal(self) -> None:
        db.save_journal(db.today_iso(), self._mood.get(), self._journal.get("1.0", "end").strip())
        self.show("journal")


def main() -> None:
    app = DayboardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
