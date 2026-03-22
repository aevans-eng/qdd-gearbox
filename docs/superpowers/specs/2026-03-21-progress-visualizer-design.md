# QDD Progress Visualizer — Design Spec

> **Date:** 2026-03-21
> **Status:** Draft
> **Tech:** CustomTkinter (Python)
> **Data source:** `testing/learn/progress.json`

---

## Purpose

A standalone desktop dashboard that shows Aaron's progress toward the Tesla Optimus internship application. Reads `progress.json` and displays: what to do next, how far along each learning topic is, what's been unlocked, and countdown timers to key milestones. Designed to gamify the process and make progress visible.

## Architecture

```
progress.json ──reads──> visualizer.py ──renders──> CustomTkinter window
```

Single-file Python script. No server, no database, no web stack. Opens a window, reads the JSON, renders the UI. Refreshes data on a timer (every 60s) or on window focus.

### Dependencies

- `customtkinter` — modern Tkinter wrapper (dark theme built-in)
- `json`, `datetime` — stdlib
- No other dependencies

### File Location

`qdd-gearbox/ui/progress_visualizer.py`

Path to `progress.json` resolved relative to the script: `Path(__file__).parent.parent / "testing" / "learn" / "progress.json"`.

### Window

- Default size: 960x720
- Minimum size: 800x600
- Resizable (panels scale proportionally)
- If `progress.json` is missing or malformed, show an error label in the window instead of crashing

---

## Layout

Two-panel layout: **main panel** (left, ~65% width) + **sidebar** (right, ~35% width).

### Main Panel

#### 1. Hero Action Cards (top)

Two cards showing the immediate next actions:

**Learning card:**
- Title: current step name + topic (e.g. "Distill — 01 Motor Fundamentals")
- Subtitle: gap count, priority tier
- Blue accent color
- "START →" button label (visual only — not clickable, this is a display dashboard)

**Networking card:**
- Title: next unlocked-but-not-done networking action from unlocks list
- Subtitle: unlock status + context
- Teal accent color
- "SEND →" button label (visual only)

**Logic for picking the learning card:**
1. Find first incomplete topic by priority tier (project > interview > breadth), then by topic number
2. Find the first incomplete step in that topic's 6-step sequence
3. Display that step + topic name

**Logic for picking the networking card:**
1. Scan unlocks in JSON key order for the first entry where `unlocked: true`
2. Show it as the active networking action (the user decides when to act on it — no separate "done" tracking)
3. If no unlocks are unlocked yet, show the next locked one with "LOCKED" state
4. If no unlocks remain, hide the card

Note: `unlocked` in progress.json means "requirements met, action available." The `/learn` skill manages setting `unlocked: true` when topics are completed. There is no separate "actioned" state — once unlocked, it stays visible until the user manually marks progress elsewhere.

#### 2. Journey Timeline (below hero)

Vertical phase-line showing the Learn → Apply → Ship cycle for each time period. Each row has:

- **Date range** (left column, 68px)
- **Phase dot** on a vertical connecting line (blue=current, grey=future, yellow=exams)
- **Phase card** with three columns: Learn | Apply | Ship

**Phase rows:**

| Date | Learn | Apply | Ship |
|------|-------|-------|------|
| Mar 22-25 | 01 ●●○○○○, 02 ●●○○○○ | Cycle 1: Motor char. | ✓ Msg Francis & Onur |
| Mar 26-27 | 03 ●○○○○○ | Cycle 2: Thermal | — |
| Mar 28-Apr 1 | 04+05 | Cycle 3: Friction | — |
| Apr 2-7 | 06+07 | Cycle 4: Writeup | Senior Tesla msgs |
| Apr 8-22 | EXAMS — streak paused (single yellow row) | | |
| Apr 23-30 | 08-13 | Cycles 5-6 | ★ APPLICATION |
| May 1-15 | Remaining | Polish | ★ INTERVIEW READY |

**Progress dots** on each topic: 6 dots representing diagnose/learn/distill/practice/grade/drill. Filled green = done, empty grey = not done. Shown inline after topic number.

**Current phase** is highlighted (brighter background, blue border). Determined by comparing today's date against phase date ranges.

**Ship column** shows key deliverables. Completed items get green "✓" prefix. Future milestone items get "★" prefix with highlight color.

### Sidebar

#### 1. Streak (top)

- Fire emoji + large number (current streak)
- Small text: "day streak · best: {longest}"
- Gold color accent

#### 2. Checkpoints (5 items)

Each checkpoint shows:
- Label (e.g. "TEST CAMPAIGN")
- Target date
- Countdown in days (calculated from today)

Compact horizontal layout: label+date on left, days on right. Each has a colored left border.

| Checkpoint | Date | Color |
|-----------|------|-------|
| TEST CAMPAIGN | Apr 7 | Red |
| SENIOR CONTACTS | Before Apr 20 | Purple |
| EXAMS DONE | Apr 22 | Yellow |
| APPLICATION READY | May 1 | Green |
| INTERVIEW READY | May 15 | Orange |

Checkpoints are **hardcoded** (these are fixed calendar milestones, not data-driven). When a checkpoint's date has passed, it shows as completed (dimmed, strikethrough label).

#### 3. Progress Bars (2 items)

**Next unlock:** Shows progress toward the next locked unlock. The bar represents how many of the `required_topics` are completed (all 6 steps done). Label shows fraction (e.g. "2/5"). The unlock name appears as the bar label.

Logic:
1. Find first unlock where `unlocked: false`
2. Count how many of its `required_topics` have all 6 steps completed
3. Bar fill = completed_topics / total_required_topics
4. If unlock also has `requires_flag`, show flag status in subtitle

**Total unlocks:** Shows overall unlock progress. Bar fill = unlocked_count / total_unlock_count. Label shows fraction dynamically (e.g. "1/12" — denominator is computed from `len(unlocks)`).

#### 4. Unlock List

Full list of all unlocks from `progress.json` in JSON key order, each showing:
- Colored dot: green (unlocked), blue+glow (next to unlock), grey (locked)
- Unlock label (short name derived from `label` field)
- Target date (right-aligned, small)

The "next" unlock (first locked one) gets a small "NEXT" badge. All 12 unlocks are shown.

---

## Data Reading

### From progress.json

| UI Element | Data Path |
|-----------|-----------|
| Streak | `streak.current`, `streak.longest` |
| Topic progress dots | `topics.{id}.steps.{step}.done` |
| Topic name | `topics.{id}.name` |
| Topic priority | `topics.{id}.priority` |
| Unlock status | `unlocks.{id}.unlocked` |
| Unlock requirements | `unlocks.{id}.required_topics`, `unlocks.{id}.requires_flag` |
| Unlock label | `unlocks.{id}.label` |
| Unlock target date | `unlocks.{id}.target_date` |
| Flag status | `flags.{flag_name}` |

### Hardcoded

| UI Element | Value |
|-----------|-------|
| Checkpoints | 5 fixed milestones with dates |
| Phase date ranges | 7 fixed time periods |
| Phase cycle descriptions | Fixed Learn/Apply/Ship content per phase |

### Computed at render time

| Value | Computation |
|-------|------------|
| Checkpoint countdown | `(checkpoint_date - today).days` |
| Current phase | Compare today against phase date ranges |
| Next learning action | First incomplete topic (by priority), first incomplete step |
| Next networking action | First unlock where `unlocked: true` (JSON key order) |
| Next unlock progress | Count completed required_topics for first locked unlock |
| Total unlock progress | Count of unlocked / total unlocks |

---

## Refresh

- **Timer:** Re-read `progress.json` every 60 seconds
- **On focus:** Re-read when window regains focus (catches changes from `/learn` sessions)
- **No file watcher** — polling is simpler and sufficient for this use case

---

## Theme

CustomTkinter dark mode. Colors match the HTML mockup:

| Element | Color |
|---------|-------|
| Background | #1a1a2e (main), #0d0d1a (sidebar) |
| Text | #e0e0e0 (primary), #888 (secondary), #555 (muted) |
| Learn accent | #3b82f6 / #93c5fd |
| Network accent | #2dd4bf / #99f6e4 |
| Streak | #ffd700 |
| Done | #4ade80 |
| Locked | #555 |
| Highlight | #c084fc |
| Exam | #facc15 |

---

## What This Is NOT

- Not interactive — no buttons actually do anything. It's a read-only dashboard.
- Not a web app — it's a desktop window.
- Not a replacement for `/learn` — that skill drives the learning workflow. This just shows the status.
- Not synced to any external service — reads a local JSON file only.

---

## Reference Mockup

`qdd-gearbox/.superpowers/brainstorm/118471-1774144951/final-mockup.html`
