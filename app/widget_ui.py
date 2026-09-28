"""Always-on-top desktop widget window."""

from __future__ import annotations

import calendar
from datetime import date

import customtkinter as ctk

from app import db


class WidgetWindow(ctk.CTkToplevel):
    def __init__(self, master) -> None:
        super().__init__(master)
        self.master_app = master
        self.title("Dayboard Widget")
        self.geometry("360x620+40+80")
        self.resizable(False, True)
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._body = ctk.CTkScrollableFrame(self)
        self._body.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def _close(self) -> None:
        self.master_app._widget = None
        self.destroy()

    def refresh(self) -> None:
        for w in self._body.winfo_children():
            w.destroy()
        today = date.today()
        ctk.CTkLabel(self._body, text="DAYBOARD", font=ctk.CTkFont(size=12), text_color="gray").pack(
            anchor="w"
        )
        ctk.CTkLabel(self._body, text=today.strftime("%A"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(
            self._body, text=today.strftime("%b %d"), font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", pady=(0, 8))

        cal_card = ctk.CTkFrame(self._body)
        cal_card.pack(fill="x", pady=6)
        head = ctk.CTkFrame(cal_card, fg_color="transparent")
        head.pack(fill="x", padx=6, pady=(8, 0))
        for i, n in enumerate(["M", "T", "W", "T", "F", "S", "S"]):
            ctk.CTkLabel(head, text=n, width=42, text_color="gray").grid(row=0, column=i)
        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(today.year, today.month)
        grid = ctk.CTkFrame(cal_card, fg_color="transparent")
        grid.pack(fill="x", padx=6, pady=(0, 8))
        for r, week in enumerate(weeks):
            for c, d in enumerate(week):
                is_today = d == today
                in_month = d.month == today.month
                ctk.CTkLabel(
                    grid,
                    text=str(d.day),
                    width=42,
                    text_color=("white" if is_today else ("gray" if not in_month else None)),
                    fg_color=("#1D4ED8" if is_today else "transparent"),
                    corner_radius=8,
                ).grid(row=r, column=c, pady=1)

        ctk.CTkLabel(self._body, text="TODAY TO DO", font=ctk.CTkFont(size=13, weight="bold")).pack(
            anchor="w", pady=(12, 4)
        )
        todos = db.list_today_todos()
        if not todos:
            ctk.CTkLabel(self._body, text="No tasks", text_color="gray").pack(anchor="w")
        for t in todos[:8]:
            ctk.CTkLabel(self._body, text=f"\u2610  {t['title']}", wraplength=300, justify="left").pack(
                anchor="w"
            )

        ctk.CTkLabel(
            self._body, text="TODAY SCHEDULE", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(12, 4))
        events = []
        if hasattr(self.master_app, "_combined_events_today"):
            events = self.master_app._combined_events_today()
        if not events:
            ctk.CTkLabel(self._body, text="No events", text_color="gray").pack(anchor="w")
        for e in events[:8]:
            when = e.get("start_time") or "all day"
            ctk.CTkLabel(
                self._body, text=f"{when}  {e['title']}", wraplength=300, justify="left"
            ).pack(anchor="w")

        btns = ctk.CTkFrame(self._body, fg_color="transparent")
        btns.pack(fill="x", pady=16)
        ctk.CTkButton(btns, text="Refresh", width=90, command=self.refresh).pack(side="left", padx=4)
        ctk.CTkButton(
            btns,
            text="Unpin",
            width=90,
            fg_color="#374151",
            command=lambda: self.attributes("-topmost", False),
        ).pack(side="left", padx=4)
