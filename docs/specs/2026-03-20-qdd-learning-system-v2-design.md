# QDD Learning System v2 — Design Spec

> **Date:** 2026-03-20
> **Status:** Design approved
> **Goal:** Get Aaron interview-ready on QDD/actuator first principles within 4 weeks
> **Supersedes:** `2026-03-20-qdd-learning-system-design.md` (v1 was workbook-only, no teaching step)

---

## Problem

The v1 learning system has good reference material (motor physics primer, campaign walkthrough) and good assessment (13 workbooks). But there's no **teaching** step between reading and testing. Aaron attempted Workbook 01 Part 1 after reading the primer and scored 0S 3P 5R — the reference docs present information but don't build mental models.

Aaron's learning profile:
- Learns by building mental models that "click" intuitively
- Needs to trace cause → effect chains (mechanism, not just facts)
- Cements knowledge through application — writing, practicing, using real numbers
- Retains best when concepts connect to physical things he's built/touched
- Analogies help as anchors, but only when mechanistically honest (not stretched)
- Target: Tesla Optimus interview — deep first-principles understanding under pressure

## Solution

A fully conversational learning system run through Claude Code. One command (`/learn`) opens a dashboard, shows progress, and guides Aaron through a structured 6-step learning workflow per topic. Everything happens in conversation — no switching between editors, markdown files, and terminals.

---

## Architecture

### Entry Point

**`/learn` skill** in Claude Code. When invoked:
1. Reads `testing/learn/progress.json`
2. Displays the dashboard (progress, streak, countdown, unlocks, next mission)
3. Awaits "let's go" or a specific command

### Per-Topic Workflow (6 Steps)

Each of the 13 topics moves through these steps sequentially:

#### Step 1: Diagnose
- **Mode:** Conversational (in `/learn` session)
- **Time:** ~15-20 min
- **What happens:** Claude asks Part 1 concept-check questions from the workbook, one at a time. Aaron answers in chat. Claude notes gaps but does NOT grade yet — just maps what needs teaching.
- **Output:** Gap list saved to `progress.json` under `topics.XX.gaps` (array of concept strings). Persists across sessions so Diagnose and Learn don't need to happen in the same conversation.
- **Note:** For topics 01-04, Aaron already completed Part 1 in workbook files. Claude reads those answers as the diagnose input instead of re-asking.

#### Step 2: Learn (Live Lesson)
- **Mode:** Conversational, interactive
- **Model:** Opus (adaptive teaching requires strongest reasoning)
- **Time:** ~30-40 min (paired topics ~50 min)
- **Method per concept:**
  1. **Anchor** — connect to something physical Aaron has seen/touched (his motor, his gearbox, MECH courses). Only honest analogies.
  2. **Trace** — walk the causal chain link by link. Check at each link: "so if current increases, what happens next? why?"
  3. **Numbers** — use Aaron's actual hardware values. D6374-150KV ($K_t = 0.0551$ Nm/A), 5:1 planetary, 90% efficiency, ODrive v3.6.
  4. **Predict** — "what if" scenario. Aaron reasons through it before Claude confirms. This is where wrong models surface.
- **Rule:** Don't move to the next concept until the current one clicks. If Aaron says "I think I get it," probe to verify.
- **Topics can be paired** when they share a physics foundation (see Curriculum section).

#### Step 3: Distill
- **Mode:** Conversational → file output
- **Time:** ~15 min
- **What happens:** Claude asks Aaron to state the 3-5 key concepts he now understands, in his own words. Aaron dictates. Claude writes it to `testing/learn/cards/XX-topic.md` and reviews for accuracy.
- **Output:** 1-page reference card in Aaron's voice. NOT a rewrite of the primer — what clicked for him specifically.
- **Purpose:** These become the interview study deck.

#### Step 4: Practice
- **Mode:** Conversational
- **Time:** ~45-60 min
- **What happens:** Claude asks Parts 2 (applied problems), 3 (design judgment), and 4 (teach-it) questions from the workbook. Aaron answers in chat. Claude grades each answer immediately — no async round-trip.
- **Source:** Workbook files are Claude's question bank. Aaron never edits them directly.
- **Grading format:** Solid / Partial / Redo per question.

#### Step 5: Grade (includes review)
- **Mode:** Conversational
- **Time:** ~15 min
- **What happens:** Summary table of practice performance (Parts 2-4) plus a quick re-check of any Part 1 concepts that were Redo during diagnose. Live follow-up probing on anything graded Partial or Redo. Claude traces back to the mechanism Aaron missed and re-teaches that specific link.
- **Output:** Grade recorded in `progress.json`
- **Redo policy:** No hard gate — if Aaron has multiple Redo grades, the re-teaching in this step addresses them. The Interview Drill (Step 6) is the final check. If Drill reveals persistent gaps, Claude flags them but the topic still progresses. Aaron can revisit any topic later with "drill me on [topic]".

#### Step 6: Interview Drill
- **Mode:** Conversational
- **Model:** Opus (needs to probe intelligently and simulate interviewer)
- **Time:** ~10 min
- **What happens:** Rapid-fire first-principles questions, Tesla interview style. No workbook, no reference — just Aaron and the concepts. Claude pushes until Aaron breaks, then teaches the gap.
- **Examples:** "Why is torque proportional to current? Where does that break down? How would you verify that on hardware? What would you do if the measurement disagreed with theory?"

### Flexible Session Structure

Aaron can do multiple steps per session or stop after any step. Typical session patterns:
- **Heavy session (~90 min):** Lesson + Distill + Practice + Grade + Drill for one topic
- **Medium session (~50 min):** Lesson for paired topics
- **Light session (~15 min):** Just a distill card, or just an interview drill (keeps streak alive)

---

## Gamification

### Dashboard (shown at `/learn` start)

```
╔══════════════════════════════════════════════════╗
║  QDD LEARNING SYSTEM          Day 3  Streak      ║
║                                                  ║
║  Progress: ████████░░░░░░░░░░░░░░░░░░  4/13     ║
║  Interview-ready in: 24 days                     ║
║                                                  ║
║  01 Motor Fund.    ●●●●●●  Complete              ║
║  02 Torque-Speed   ●●●○○○  Practice next         ║
║  03 Thermal        ●○○○○○  Lesson next           ║
║  04 Friction       ●○○○○○  Diagnosed             ║
║  05 Gearbox        ○○○○○○  Not started           ║
║  ...                                             ║
║                                                  ║
║  TODAY'S MISSION: Lesson — Topic 03 Thermal      ║
║  Est. time: ~35 min                              ║
║                                                  ║
║  "Let's go" to start  |  "skip to [step]"        ║
╠══════════════════════════════════════════════════╣
║  ● = diagnose | learn | distill | practice |     ║
║      grade | drill                               ║
╚══════════════════════════════════════════════════╝
```

- 6 dots per topic representing the 6 steps
- Streak counter (consecutive days with at least one step)
- Countdown to target interview-ready date
- Clear next mission with time estimate
- Quick commands: "let's go", "skip to [step]", "drill me on [topic]"

### Unlock System

Real-world milestones gated by actual knowledge acquisition:

| Milestone | Unlock | Why it's gated |
|-----------|--------|---------------|
| Topics 01-02 complete | Update resume with "BLDC motor characterization" | Can now defend it in interview |
| Topics 01-05 complete | Start test campaign (Phases 0-1) | Need this knowledge to interpret test data |
| Topics 01-05 + test data | Write first-principles explainer for portfolio | Have both theory and data |
| Topics 06-07 complete | Post on LinkedIn about testing methodology | Can speak with technical depth |
| Topics 08-09 complete | Message Tesla contacts about impedance control | Can hold a real technical conversation |
| Topics 08-09 + demo | Add impedance control demo to portfolio | Real demo backed by real understanding |
| All 13 complete | Full interview-ready — reach out to recruiters | Can handle any first-principles question |

Dashboard shows unlock progress:
```
UNLOCKS
  Update resume .............. 2/2 topics — READY
  Start test campaign ........ 4/5 topics
  LinkedIn post .............. 4/7 topics
  Message Tesla contacts ..... 4/9 topics
  Interview-ready ............ 4/13 topics
```

### Streak Mechanics

- **Minimum viable day:** Complete at least one step (even a 15-min reference card or quick drill)
- **Full day:** Complete a teaching session or full practice round
- Streak resets if a day is missed
- Streak is visually prominent on dashboard

### Evening Nudge

Windows scheduled task checks `progress.json`. If no activity logged today, shows a toast notification at a user-configured time (default 7pm):

> "No QDD study today. 15 min on your reference card for Topic 02?"

Suggests the smallest possible next step to keep the streak alive.

---

## Curriculum

### Topic Pairing

Topics that share physics foundations are taught together to reduce context-switching:

| Session | Topics | Connection |
|---------|--------|-----------|
| A | 01 (Motor Fundamentals) + 02 (Torque-Speed Envelope) | Same motor physics, just extended to operating limits |
| B | 03 (Thermal) | Standalone — waste heat from the electromechanical conversion |
| C | 04 (Friction & Backdrivability) + 05 (Gearbox Mechanics) | Both about what the gearbox does to the motor's output |
| D | 06 (Measurement & Instrumentation) + 07 (Testing Methodology) | How to measure and how to structure tests |

Topics 08-13 are taught individually (more complex, more independent).

### Week 1 Schedule (Topics 01-07: Testing Prerequisites)

Diagnose is folded into the start of each lesson as a lightweight preamble. For topics 01-04, Claude reads existing Part 1 answers from workbook files. For topics 05-07, Claude asks a few quick diagnostic questions before teaching.

| Day | Mission | ~Time |
|-----|---------|-------|
| 1 | Diagnose+Lesson: Topics 01+02 (Motor + Torque-Speed) | 50 min |
| 2 | Distill 01+02, Practice+Grade 01 | 75 min |
| 3 | Practice+Grade 02, Lesson 03 (Thermal) | 75 min |
| 4 | Distill 03, Practice+Grade 03, Lesson 04+05 | 90 min |
| 5 | Distill 04+05, Practice+Grade 04 | 75 min |
| 6 | Practice+Grade 05, Lesson 06+07 | 80 min |
| 7 | Distill 06+07, Practice+Grade 06+07, Interview drill 01-07 | 90 min |

### Weeks 2-4

| Week | Topics | Focus |
|------|--------|-------|
| 2 | Start test campaign + 08 (Dynamics & System ID) | Apply 01-07 on hardware, learn modeling |
| 3 | 09 (Impedance Control) + 10 (Backlash & Compliance) | Advanced — the interview differentiators |
| 4 | 11 (GD&T) + 12 (DFM) + 13 (FEA) + full interview prep | Manufacturing + comprehensive drill |

### Hardware Integration (Topics 04, 06, 07, 10)

For topics tied to physical tests, add a **Predict → Observe → Explain** step:
- Before running a test: predict the result using theory
- Run the test, record actual data
- Explain any gap between prediction and measurement
- This creates interview stories: "I predicted X, measured Y, and the difference told me Z"

---

## Data Model

### progress.json

All dates use local system time (Aaron's Windows machine, Pacific time).

```json
{
  "target_date": "2026-04-17",
  "streak": {
    "current": 3,
    "last_activity": "2026-03-20",
    "longest": 3
  },
  "topics": {
    "01": {
      "name": "Motor Fundamentals",
      "gaps": ["FOC mechanism", "Kt derivation", "pole pairs", "phase current vs Iq"],
      "steps": {
        "diagnose": { "done": true, "date": "2026-03-20" },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    }
  },
  "unlocks": {
    "resume_update": { "required_topics": ["01", "02"], "unlocked": false },
    "test_campaign": { "required_topics": ["01", "02", "03", "04", "05"], "unlocked": false },
    "portfolio_explainer": { "required_topics": ["01", "02", "03", "04", "05"], "requires_flag": "test_data_collected", "unlocked": false },
    "linkedin_post": { "required_topics": ["01", "02", "03", "04", "05", "06", "07"], "unlocked": false },
    "message_tesla": { "required_topics": ["01", "02", "03", "04", "05", "06", "07", "08", "09"], "unlocked": false },
    "portfolio_demo": { "required_topics": ["08", "09"], "requires_flag": "impedance_demo_done", "unlocked": false },
    "interview_ready": { "required_topics": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13"], "unlocked": false }
  },
  "flags": {
    "test_data_collected": false,
    "impedance_demo_done": false
  }
}
```

### Reference Cards

Written to `testing/learn/cards/XX-topic.md` after each distill step. Format:

```markdown
# [Topic Name] — Reference Card

> Written by Aaron after lesson on [date]
> Reviewed by Claude for accuracy

## Key Concepts

[Aaron's own words — what clicked, in the order it makes sense to him]

## The Chain

[Cause → effect chain for the core relationships in this topic]

## Numbers That Matter

[Specific values from his hardware, with what they mean]
```

---

## File Structure

```
testing/learn/
  motor-physics-primer.md          # existing reference (unchanged)
  campaign-walkthrough.md          # existing reference (unchanged)
  progress.json                    # NEW — progress tracking
  cards/                           # NEW — Aaron's reference cards
    01-motor-fundamentals.md
    02-torque-speed-envelope.md
    ...
  workbooks/                       # existing (unchanged — used as question bank)
    _progress.md                   # v1 tracker (deprecated, kept for reference)
    01-motor-fundamentals.md
    ...
```

---

## Implementation Components

1. **`/learn` skill** — Claude Code skill that reads progress.json, renders dashboard, manages session flow
2. **progress.json** — data file tracking all state
3. **`testing/learn/cards/` directory** — reference cards written during distill steps
4. **Startup shortcut** — Windows Startup folder shortcut to open Claude Code in qdd-gearbox directory
5. **Nudge script** — PowerShell script + Windows scheduled task for evening toast notification

---

## Design Principles

- **One tab, one conversation** — everything happens in Claude Code, no context switching
- **Zero decision fatigue** — dashboard tells you exactly what to do next
- **Real unlocks, not fake rewards** — milestones are gated by genuine knowledge acquisition
- **Streak psychology** — minimum viable daily engagement to maintain consistency
- **First principles depth** — every concept traced to its physical mechanism, not just memorized
- **Aaron's voice** — reference cards are in his words, not textbook language
- **Interview-ready** — the drill step simulates real pressure; the unlock system connects learning to career actions

## Future: Reusable Framework

This methodology is domain-agnostic. After validation on the QDD project, extract into a standalone template repo that anyone can clone, define their own topics/questions, and use for rapid first-principles learning. Separate project — do not prematurely abstract.
