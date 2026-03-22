"""
QDD Progress Visualizer
=======================
CustomTkinter dashboard showing learning progress, unlocks,
checkpoints, and next actions. Reads testing/learn/progress.json.
"""

import json
from datetime import date, datetime
from pathlib import Path
import customtkinter as ctk

# --- Paths ---
PROGRESS_JSON = Path(__file__).parent.parent / "testing" / "learn" / "progress.json"

# --- Colors ---
C_BG_MAIN = "#1a1a2e"
C_BG_SIDEBAR = "#0d0d1a"
C_TEXT = "#e0e0e0"
C_TEXT_SEC = "#888888"
C_TEXT_MUTED = "#555555"
C_BLUE = "#3b82f6"
C_BLUE_LIGHT = "#93c5fd"
C_TEAL = "#2dd4bf"
C_TEAL_LIGHT = "#99f6e4"
C_GOLD = "#ffd700"
C_GREEN = "#4ade80"
C_RED = "#f87171"
C_PURPLE = "#c084fc"
C_YELLOW = "#facc15"
C_ORANGE = "#f59e0b"

# --- Constants ---
STEPS = ["diagnose", "learn", "distill", "practice", "grade", "drill"]
PRIORITY_ORDER = {"project": 0, "interview": 1, "breadth": 2}

CHECKPOINTS = [
    ("TEST CAMPAIGN", date(2026, 4, 7), C_RED),
    ("SENIOR CONTACTS", date(2026, 4, 20), C_PURPLE),
    ("EXAMS DONE", date(2026, 4, 22), C_YELLOW),
    ("APPLICATION READY", date(2026, 5, 1), C_GREEN),
    ("INTERVIEW READY", date(2026, 5, 15), C_ORANGE),
]

PHASES = [
    {
        "dates": "Mar 22-25",
        "start": date(2026, 3, 22), "end": date(2026, 3, 25),
        "topics": ["01", "02"],
        "apply": "Cycle 1: Motor char.",
        "ship": [("done", "Msg Francis & Onur")],
    },
    {
        "dates": "Mar 26-27",
        "start": date(2026, 3, 26), "end": date(2026, 3, 27),
        "topics": ["03"],
        "apply": "Cycle 2: Thermal",
        "ship": [],
    },
    {
        "dates": "Mar 28-Apr 1",
        "start": date(2026, 3, 28), "end": date(2026, 4, 1),
        "topics": ["04", "05"],
        "apply": "Cycle 3: Friction",
        "ship": [],
    },
    {
        "dates": "Apr 2-7",
        "start": date(2026, 4, 2), "end": date(2026, 4, 7),
        "topics": ["06", "07"],
        "apply": "Cycle 4: Writeup",
        "ship": [("highlight", "Senior Tesla msgs")],
    },
    {
        "dates": "Apr 8-22",
        "start": date(2026, 4, 8), "end": date(2026, 4, 22),
        "topics": [],
        "apply": "",
        "ship": [],
        "exam": True,
    },
    {
        "dates": "Apr 23-30",
        "start": date(2026, 4, 23), "end": date(2026, 4, 30),
        "topics": ["08", "09", "10", "11", "12", "13"],
        "apply": "Cycles 5-6",
        "ship": [("milestone", "APPLICATION")],
    },
    {
        "dates": "May 1-15",
        "start": date(2026, 5, 1), "end": date(2026, 5, 15),
        "topics": [],
        "apply": "Polish",
        "ship": [("milestone_orange", "INTERVIEW READY")],
    },
]


def load_data():
    """Load and return progress.json as dict. Returns None on error."""
    try:
        with open(PROGRESS_JSON, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def topic_steps_done(topic_data):
    """Return list of bools for each of the 6 steps."""
    return [topic_data["steps"][s].get("done", False) for s in STEPS]


def topic_complete(topic_data):
    """True if all 6 steps are done."""
    if "steps" not in topic_data:
        return False
    return all(topic_steps_done(topic_data))


def get_next_learning_action(data):
    """Return (step_name, topic_id, topic_name, priority, gaps_count) or None."""
    topics = data["topics"]
    sorted_topics = sorted(
        topics.items(),
        key=lambda t: (PRIORITY_ORDER.get(t[1]["priority"], 99), t[0])
    )
    for tid, tdata in sorted_topics:
        for step in STEPS:
            if not tdata["steps"][step].get("done", False):
                return (step.capitalize(), tid, tdata["name"],
                        tdata["priority"], len(tdata.get("gaps", [])))
    return None


def get_next_networking_action(data):
    """Return (key, label, unlocked) for first unlocked unlock, or first locked."""
    for key, udata in data["unlocks"].items():
        if udata.get("unlocked", False):
            return (key, udata["label"], True)
    for key, udata in data["unlocks"].items():
        if not udata.get("unlocked", False):
            return (key, udata["label"], False)
    return None


def get_next_unlock_progress(data):
    """Return (unlock_label, completed_count, total_required, flag, flag_done) or None."""
    for key, udata in data["unlocks"].items():
        if not udata.get("unlocked", False):
            required = udata.get("required_topics", [])
            completed = sum(1 for t in required if topic_complete(data["topics"].get(t, {})))
            flag = udata.get("requires_flag")
            flag_done = data["flags"].get(flag, False) if flag else None
            return (udata["label"], completed, len(required), flag, flag_done)
    return None


def get_unlock_stats(data):
    """Return (unlocked_count, total_count)."""
    unlocks = data["unlocks"]
    unlocked = sum(1 for u in unlocks.values() if u.get("unlocked", False))
    return (unlocked, len(unlocks))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QDD Progress Visualizer")
        self.geometry("960x720")
        self.minsize(800, 600)
        ctk.set_appearance_mode("dark")

        self.data = None
        self.build_layout()
        self.refresh_data()
        self.schedule_refresh()
        self.bind("<FocusIn>", self._on_focus)

    def _on_focus(self, event):
        if event.widget == self:
            self.refresh_data()

    def build_layout(self):
        """Create the two-panel layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.main_frame = ctk.CTkScrollableFrame(
            self, fg_color=C_BG_MAIN, corner_radius=0
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.sidebar = ctk.CTkScrollableFrame(
            self, fg_color=C_BG_SIDEBAR, corner_radius=0, width=230
        )
        self.sidebar.grid(row=0, column=1, sticky="nsew")

    def refresh_data(self):
        """Reload progress.json and rebuild all widgets."""
        self.data = load_data()
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        if self.data is None:
            ctk.CTkLabel(
                self.main_frame, text="Error: Could not load progress.json",
                text_color=C_RED, font=("Segoe UI", 16)
            ).pack(pady=40)
            return

        self.build_hero()
        self.build_journey()
        self.build_sidebar_streak()
        self.build_sidebar_checkpoints()
        self.build_sidebar_progress()
        self.build_sidebar_unlocks()

    def schedule_refresh(self):
        """Refresh every 60 seconds."""
        self.after(60000, self._auto_refresh)

    def _auto_refresh(self):
        self.refresh_data()
        self.schedule_refresh()

    # --- Hero Action Cards ---

    def build_hero(self):
        """Render the two hero action cards at the top."""
        hero_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        hero_frame.pack(fill="x", padx=20, pady=(16, 8))

        action = get_next_learning_action(self.data)
        if action:
            step_name, tid, tname, priority, gaps = action
            self._action_card(
                hero_frame,
                icon="\U0001f4d6",
                title=f"{step_name} \u2014 {tid} {tname}",
                subtitle=f"{gaps} gaps \u00b7 {priority.upper()} priority",
                btn_text="START \u2192",
                accent=C_BLUE, accent_light=C_BLUE_LIGHT,
                bg="#1e3a5f", border="#3b82f6",
            )

        net = get_next_networking_action(self.data)
        if net:
            key, label, unlocked = net
            status = "UNLOCKED" if unlocked else "LOCKED"
            self._action_card(
                hero_frame,
                icon="\U0001f4ac",
                title=label,
                subtitle=status,
                btn_text="SEND \u2192" if unlocked else "LOCKED",
                accent=C_TEAL if unlocked else C_TEXT_MUTED,
                accent_light=C_TEAL_LIGHT if unlocked else C_TEXT_MUTED,
                bg="#1e3b3b" if unlocked else "#1a1a2e",
                border="#2dd4bf" if unlocked else "#555555",
            )

    def _action_card(self, parent, icon, title, subtitle, btn_text,
                     accent, accent_light, bg, border):
        """Render a single action card."""
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=10,
                            border_width=1, border_color=border)
        card.pack(fill="x", pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(inner, text=icon, font=("Segoe UI", 20),
                     text_color=C_TEXT).grid(row=0, column=0, rowspan=2, padx=(0, 12))

        ctk.CTkLabel(inner, text=title, font=("Segoe UI", 13, "bold"),
                     text_color=accent_light, anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(inner, text=subtitle, font=("Segoe UI", 10),
                     text_color=C_TEXT_SEC, anchor="w").grid(row=1, column=1, sticky="w")

        text_color = "#ffffff" if accent != C_TEAL else "#000000"
        btn = ctk.CTkLabel(inner, text=btn_text, font=("Segoe UI", 10, "bold"),
                           fg_color=accent, text_color=text_color,
                           corner_radius=14, width=70, height=26)
        btn.grid(row=0, column=2, rowspan=2, padx=(12, 0))

    # --- Journey Timeline ---

    def build_journey(self):
        """Render the vertical phase-line journey timeline."""
        ctk.CTkFrame(self.main_frame, fg_color="#333333", height=1).pack(
            fill="x", padx=20, pady=(0, 4))

        journey_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        journey_frame.pack(fill="x", padx=20, pady=(4, 16))

        today = date.today()

        for phase in PHASES:
            is_current = phase["start"] <= today <= phase["end"]
            is_past = today > phase["end"]
            is_exam = phase.get("exam", False)

            row = ctk.CTkFrame(journey_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure(2, weight=1)

            # Date label
            date_color = C_BLUE if is_current else (C_YELLOW if is_exam else C_TEXT_SEC)
            date_weight = "bold" if is_current else "normal"
            ctk.CTkLabel(row, text=phase["dates"],
                         font=("Segoe UI", 10, date_weight),
                         text_color=date_color, width=78,
                         anchor="e").grid(row=0, column=0, padx=(0, 8))

            # Dot
            dot_frame = ctk.CTkFrame(row, fg_color="transparent", width=14)
            dot_frame.grid(row=0, column=1, sticky="ns")
            dot_frame.grid_propagate(False)

            if is_current:
                dot_color = C_BLUE
            elif is_exam:
                dot_color = C_YELLOW
            elif is_past:
                dot_color = C_GREEN
            else:
                dot_color = C_TEXT_MUTED

            dot = ctk.CTkFrame(dot_frame, fg_color=dot_color,
                               width=10, height=10, corner_radius=5)
            dot.place(relx=0.5, y=10, anchor="center")

            # Exam row
            if is_exam:
                card = ctk.CTkFrame(row, fg_color="#1f1f0e", corner_radius=8)
                card.grid(row=0, column=2, sticky="ew", pady=2)
                ctk.CTkLabel(card, text="EXAMS \u2014 streak paused",
                             font=("Segoe UI", 10),
                             text_color=C_YELLOW).pack(padx=14, pady=8)
                continue

            # Normal phase card
            card_bg = "#1a2a4e" if is_current else "#16213e"
            bw = 1 if is_current else 0
            card = ctk.CTkFrame(row, fg_color=card_bg, corner_radius=8,
                                border_width=bw,
                                border_color="#3b82f6" if bw else C_BG_MAIN)
            card.grid(row=0, column=2, sticky="ew", pady=2)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=8)
            inner.grid_columnconfigure(0, weight=1)
            inner.grid_columnconfigure(1, weight=1)
            inner.grid_columnconfigure(2, weight=1)

            for col, header in enumerate(["Learn", "Apply", "Ship"]):
                ctk.CTkLabel(inner, text=header, font=("Segoe UI", 9),
                             text_color="#666666",
                             anchor="w").grid(row=0, column=col, sticky="w")

            # Learn column
            learn_frame = ctk.CTkFrame(inner, fg_color="transparent")
            learn_frame.grid(row=1, column=0, sticky="w")
            for tid in phase["topics"]:
                tdata = self.data["topics"].get(tid)
                if tdata:
                    dots = topic_steps_done(tdata)
                    tid_label = ctk.CTkFrame(learn_frame, fg_color="transparent")
                    tid_label.pack(anchor="w")
                    ctk.CTkLabel(
                        tid_label, text=f"{tid} ",
                        font=("Segoe UI", 10),
                        text_color=C_BLUE_LIGHT if is_current else C_TEXT_SEC,
                        anchor="w"
                    ).pack(side="left")
                    for d in dots:
                        ctk.CTkLabel(
                            tid_label,
                            text="\u25cf" if d else "\u25cb",
                            font=("Segoe UI", 8),
                            text_color=C_GREEN if d else C_TEXT_MUTED,
                            anchor="w"
                        ).pack(side="left")

            # Apply column
            if phase["apply"]:
                apply_color = C_TEXT if is_current else C_TEXT_MUTED
                ctk.CTkLabel(inner, text=phase["apply"],
                             font=("Segoe UI", 10),
                             text_color=apply_color,
                             anchor="w").grid(row=1, column=1, sticky="w")

            # Ship column
            ship_frame = ctk.CTkFrame(inner, fg_color="transparent")
            ship_frame.grid(row=1, column=2, sticky="w")
            for stype, stext in phase["ship"]:
                if stype == "done":
                    ctk.CTkLabel(ship_frame, text=f"\u2713 {stext}",
                                 font=("Segoe UI", 10),
                                 text_color=C_GREEN, anchor="w").pack(anchor="w")
                elif stype == "highlight":
                    ctk.CTkLabel(ship_frame, text=stext,
                                 font=("Segoe UI", 10),
                                 text_color=C_PURPLE, anchor="w").pack(anchor="w")
                elif stype == "milestone":
                    ctk.CTkLabel(ship_frame, text=f"\u2605 {stext}",
                                 font=("Segoe UI", 10, "bold"),
                                 text_color=C_GREEN, anchor="w").pack(anchor="w")
                elif stype == "milestone_orange":
                    ctk.CTkLabel(ship_frame, text=f"\u2605 {stext}",
                                 font=("Segoe UI", 10, "bold"),
                                 text_color=C_ORANGE, anchor="w").pack(anchor="w")
            if not phase["ship"]:
                ctk.CTkLabel(ship_frame, text="\u2014",
                             font=("Segoe UI", 10),
                             text_color=C_TEXT_MUTED).pack(anchor="w")

    # --- Sidebar: Streak ---

    def build_sidebar_streak(self):
        """Render streak counter."""
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(10, 6))

        streak = self.data["streak"]
        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(anchor="w")
        ctk.CTkLabel(row, text="\U0001f525",
                     font=("Segoe UI", 16)).pack(side="left")
        ctk.CTkLabel(row, text=str(streak["current"]),
                     font=("Segoe UI", 26, "bold"),
                     text_color=C_GOLD).pack(side="left", padx=(4, 0))

        ctk.CTkLabel(frame,
                     text=f"day streak \u00b7 best: {streak['longest']}",
                     font=("Segoe UI", 10),
                     text_color=C_TEXT_SEC).pack(anchor="w")

    # --- Sidebar: Checkpoints ---

    def build_sidebar_checkpoints(self):
        """Render 5 checkpoint countdowns."""
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(frame, text="CHECKPOINTS", font=("Segoe UI", 9),
                     text_color=C_TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        today = date.today()
        for label, target, color in CHECKPOINTS:
            days = (target - today).days
            done = days <= 0

            cp = ctk.CTkFrame(frame, fg_color=self._cp_bg(color),
                              corner_radius=6, border_width=0)
            cp.pack(fill="x", pady=2)

            left_bar = ctk.CTkFrame(cp, fg_color=color, width=3, corner_radius=0)
            left_bar.place(x=0, y=0, relheight=1)

            inner = ctk.CTkFrame(cp, fg_color="transparent")
            inner.pack(fill="x", padx=(8, 0))
            inner.grid_columnconfigure(0, weight=1)

            lbl_font = ctk.CTkFont(family="Segoe UI", size=10, weight="bold",
                                    overstrike=done)
            ctk.CTkLabel(inner, text=label, font=lbl_font,
                         text_color=color if not done else C_TEXT_MUTED,
                         anchor="w").grid(row=0, column=0, sticky="w",
                                         padx=(4, 0), pady=(4, 0))

            if label == "SENIOR CONTACTS":
                date_str = f"Before {target.strftime('%b %d')}"
            else:
                date_str = target.strftime("%b %d")
            ctk.CTkLabel(inner, text=date_str, font=("Segoe UI", 8),
                         text_color=C_TEXT_SEC,
                         anchor="w").grid(row=1, column=0, sticky="w",
                                         padx=(4, 0), pady=(0, 4))

            day_text = f"{days}d" if days > 0 else "DONE"
            ctk.CTkLabel(inner, text=day_text,
                         font=("Segoe UI", 14, "bold"),
                         text_color=color if not done else C_TEXT_MUTED
                         ).grid(row=0, column=1, rowspan=2, padx=(0, 10))

    def _cp_bg(self, color):
        """Return a dark background tint based on checkpoint color."""
        bg_map = {
            C_RED: "#2a1a1e",
            C_PURPLE: "#1f1a2e",
            C_YELLOW: "#1f1f0e",
            C_GREEN: "#0f1f15",
            C_ORANGE: "#2a1a0e",
        }
        return bg_map.get(color, C_BG_SIDEBAR)

    # --- Sidebar: Progress Bars ---

    def build_sidebar_progress(self):
        """Render next-unlock and total-unlock progress bars."""
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(frame, text="PROGRESS", font=("Segoe UI", 9),
                     text_color=C_TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        nup = get_next_unlock_progress(self.data)
        if nup:
            label, done_count, total, flag, flag_done = nup
            pct = done_count / total if total > 0 else 0
            self._progress_bar(frame, "Next unlock", pct,
                               f"{done_count}/{total}", C_BLUE)

        unlocked, total = get_unlock_stats(self.data)
        pct = unlocked / total if total > 0 else 0
        self._progress_bar(frame, "Total unlocks", pct,
                           f"{unlocked}/{total}", C_GREEN)

    def _progress_bar(self, parent, label, fraction, text, color):
        """Render a labeled progress bar."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row, text=label, font=("Segoe UI", 9),
                     text_color=C_TEXT_SEC, width=70,
                     anchor="w").grid(row=0, column=0)

        bar = ctk.CTkProgressBar(row, progress_color=color,
                                 fg_color="#333333", height=5,
                                 corner_radius=3)
        bar.set(fraction)
        bar.grid(row=0, column=1, sticky="ew", padx=4)

        ctk.CTkLabel(row, text=text, font=("Segoe UI", 9),
                     text_color=C_TEXT_SEC, width=28,
                     anchor="e").grid(row=0, column=2)

    # --- Sidebar: Unlock List ---

    def build_sidebar_unlocks(self):
        """Render full unlock list."""
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkLabel(frame, text="UNLOCKS", font=("Segoe UI", 9),
                     text_color=C_TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        found_next = False
        for key, udata in self.data["unlocks"].items():
            unlocked = udata.get("unlocked", False)
            is_next = not unlocked and not found_next

            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            row.grid_columnconfigure(1, weight=1)

            if unlocked:
                dot_color = C_GREEN
                text_color = C_GREEN
            elif is_next:
                dot_color = C_BLUE
                text_color = C_BLUE_LIGHT
                found_next = True
            else:
                dot_color = C_TEXT_MUTED
                text_color = "#666666"

            dot = ctk.CTkFrame(row, fg_color=dot_color,
                               width=6, height=6, corner_radius=3)
            dot.grid(row=0, column=0, padx=(0, 6), pady=3)
            dot.grid_propagate(False)

            short = udata["label"]
            if len(short) > 25:
                short = short[:22] + "..."

            name_frame = ctk.CTkFrame(row, fg_color="transparent")
            name_frame.grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(name_frame, text=short, font=("Segoe UI", 10),
                         text_color=text_color,
                         anchor="w").pack(side="left")

            if is_next:
                ctk.CTkLabel(name_frame, text="NEXT",
                             font=("Segoe UI", 7, "bold"),
                             fg_color=C_BLUE, text_color="#ffffff",
                             corner_radius=3, width=30,
                             height=14).pack(side="left", padx=(4, 0))

            target = udata.get("target_date", "")
            if target:
                try:
                    d = datetime.strptime(target, "%Y-%m-%d").date()
                    date_str = d.strftime("%b %d")
                except ValueError:
                    date_str = target
            else:
                date_str = ""

            if unlocked:
                date_str = "DONE"

            ctk.CTkLabel(row, text=date_str, font=("Segoe UI", 8),
                         text_color=C_TEXT_MUTED,
                         anchor="e").grid(row=0, column=2)


if __name__ == "__main__":
    app = App()
    app.mainloop()
