# QDD Learning System v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a conversational `/learn` skill for Claude Code that guides Aaron through a 6-step learning workflow per topic, with gamification (dashboard, streaks, unlocks) and a nudge notification system.

**Architecture:** A Claude Code skill (`/learn`) reads/writes `progress.json` for state, renders a dashboard, and manages session flow through 6 steps (diagnose, learn, distill, practice, grade, drill). A PowerShell nudge script runs as a Windows scheduled task. All learning happens conversationally — no external UI.

**Tech Stack:** Claude Code skills (markdown), JSON (progress tracking), PowerShell (nudge notifications), Windows Task Scheduler

**Spec:** `docs/specs/2026-03-20-qdd-learning-system-v2-design.md`

---

## File Structure

```
NEW FILES:
  .claude/skills/learn/SKILL.md              — /learn skill (main entry point + full session logic)
  claude-tools/skills/learn/SKILL.md         — backup copy of skill
  testing/learn/progress.json                — progress state
  testing/learn/cards/                       — directory for reference cards (created during distill)
  claude-tools/scripts/qdd-nudge.ps1         — evening nudge notification script

EXISTING FILES (read-only reference):
  testing/learn/workbooks/01-*.md through 13-*.md  — question bank
  testing/learn/motor-physics-primer.md             — reference material
  testing/learn/campaign-walkthrough.md             — reference material
  testing/learn/workbooks/_progress.md              — v1 tracker (deprecated)

MODIFIED FILES:
  qdd-gearbox/CLAUDE.md                     — add /learn to skills table
  c-projects/CLAUDE.md                      — add /learn to skills table
```

---

### Task 1: Create progress.json with initial state

**Files:**
- Create: `testing/learn/progress.json`

This is the data backbone. Everything reads from and writes to this file.

- [ ] **Step 1: Create the progress.json file**

All 13 topics initialized. Topics 01-04 have `diagnose.done: true` since Aaron already completed Part 1 concept checks. Topic 01 has gaps populated from the grading session.

```json
{
  "target_date": "2026-04-17",
  "streak": {
    "current": 1,
    "last_activity": "2026-03-20",
    "longest": 1
  },
  "topics": {
    "01": {
      "name": "Motor Fundamentals",
      "gaps": ["FOC mechanism", "Lorentz force / linearity", "Kt/Ke/Kv triangle", "pole pairs and electrical angle", "phase current vs Iq", "nonlinearity sources"],
      "steps": {
        "diagnose": { "done": true, "date": "2026-03-20" },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "02": {
      "name": "Torque-Speed Envelope",
      "gaps": [],
      "steps": {
        "diagnose": { "done": true, "date": "2026-03-20" },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "03": {
      "name": "Thermal",
      "gaps": [],
      "steps": {
        "diagnose": { "done": true, "date": "2026-03-20" },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "04": {
      "name": "Friction & Backdrivability",
      "gaps": [],
      "steps": {
        "diagnose": { "done": true, "date": "2026-03-20" },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "05": {
      "name": "Gearbox Mechanics",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "06": {
      "name": "Measurement & Instrumentation",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "07": {
      "name": "Testing Methodology",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "08": {
      "name": "Dynamics & System ID",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "09": {
      "name": "Impedance Control",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "10": {
      "name": "Backlash & Compliance",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "11": {
      "name": "GD&T & Tolerancing",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "12": {
      "name": "DFM & Manufacturing",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    },
    "13": {
      "name": "FEA Literacy",
      "gaps": [],
      "steps": {
        "diagnose": { "done": false },
        "learn": { "done": false },
        "distill": { "done": false },
        "practice": { "done": false },
        "grade": { "done": false, "score": { "solid": 0, "partial": 0, "redo": 0 } },
        "drill": { "done": false }
      }
    }
  },
  "unlocks": {
    "resume_update": { "required_topics": ["01", "02"], "unlocked": false, "label": "Update resume with BLDC motor characterization" },
    "test_campaign": { "required_topics": ["01", "02", "03", "04", "05"], "unlocked": false, "label": "Start test campaign (Phases 0-1)" },
    "portfolio_explainer": { "required_topics": ["01", "02", "03", "04", "05"], "requires_flag": "test_data_collected", "unlocked": false, "label": "Write first-principles explainer for portfolio" },
    "linkedin_post": { "required_topics": ["01", "02", "03", "04", "05", "06", "07"], "unlocked": false, "label": "Post on LinkedIn about testing methodology" },
    "message_tesla": { "required_topics": ["01", "02", "03", "04", "05", "06", "07", "08", "09"], "unlocked": false, "label": "Message Tesla contacts about impedance control" },
    "portfolio_demo": { "required_topics": ["08", "09"], "requires_flag": "impedance_demo_done", "unlocked": false, "label": "Add impedance control demo to portfolio" },
    "interview_ready": { "required_topics": ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13"], "unlocked": false, "label": "Interview-ready — reach out to recruiters" }
  },
  "flags": {
    "test_data_collected": false,
    "impedance_demo_done": false
  }
}
```

- [ ] **Step 2: Create the cards directory**

Run: `mkdir -p testing/learn/cards` (inside qdd-gearbox)

- [ ] **Step 3: Verify the file parses correctly**

Run: `python -c "import json; d=json.load(open('testing/learn/progress.json')); print(f'{len(d[\"topics\"])} topics, {len(d[\"unlocks\"])} unlocks'); [print(f'  {k}: diagnose={v[\"steps\"][\"diagnose\"][\"done\"]}') for k,v in d['topics'].items()]"`

Expected: 13 topics, 7 unlocks. Topics 01-04 show `diagnose=True`, 05-13 show `diagnose=False`.

- [ ] **Step 4: Commit**

```bash
git add testing/learn/progress.json
git commit -m "feat: add progress.json for learning system v2

Initializes all 13 topics with 6-step tracking, unlock milestones,
streak tracking, and flags for composite unlocks. Topics 01-04
pre-populated as diagnosed from workbook Part 1 attempts."
```

---

### Task 2: Create the `/learn` skill

**Files:**
- Create: `.claude/skills/learn/SKILL.md`
- Create: `claude-tools/skills/learn/SKILL.md` (backup copy)

This is the core of the system. The skill handles everything: reading progress, rendering the dashboard, managing session flow, updating progress after each step. Because all the logic is in the skill instructions (not code), the quality of this file directly determines the quality of the learning experience.

The skill is long because it encodes:
1. Dashboard rendering logic
2. All 6 step behaviors with teaching methodology
3. Progress update rules
4. Streak calculation
5. Unlock evaluation

- [ ] **Step 1: Write the skill file**

Create `.claude/skills/learn/SKILL.md` with the following content:

````markdown
---
name: learn
description: QDD Learning System — conversational study sessions with dashboard, streaks, and unlocks. Use when Aaron says "/learn", "teach me", "let's study", "drill me", "grade my workbook", or wants to work through QDD topics. Also triggers on "show my progress" or "what should I study next".
version: 2.0.0
---

# /learn — QDD Learning System v2

**Invoke with:** `/learn`

You are a **first-principles tutor and interview coach** for QDD actuator concepts. Your job is to build Aaron's mental models so deeply that he can explain any concept from the physics up, under pressure, in a Tesla Optimus interview.

**On invocation:** Read `testing/learn/progress.json`, render the dashboard, and present today's mission. Wait for Aaron to say "let's go" or give a specific command.

---

## Dashboard Rendering

Read `testing/learn/progress.json` and render this dashboard. Calculate all values from the JSON data.

**Streak calculation:** Compare `streak.last_activity` to today's date (use Bash: `date '+%Y-%m-%d'`).
- If last_activity is today → streak is current, show `streak.current`
- If last_activity is yesterday → streak is current, show `streak.current`
- If last_activity is older → streak has reset, set `streak.current = 0` and save

**Progress bar:** Count topics where ALL 6 steps are done. That count / 13 = completion.

**Per-topic dots:** 6 dots per topic. Filled (●) if that step's `done` is true, empty (○) if false. Steps in order: diagnose, learn, distill, practice, grade, drill.

**Next mission:** Find the first topic (by number) that has incomplete steps. The first incomplete step is the mission. Show the step name and estimated time.

**Time estimates per step:**
- diagnose: ~15 min
- learn: ~35 min (paired topics ~50 min)
- distill: ~15 min
- practice: ~50 min
- grade: ~15 min
- drill: ~10 min

**Unlock progress:** For each unlock, count how many of its `required_topics` have all 6 steps complete. If all required topics are complete (and flag is met if `requires_flag` exists), mark as UNLOCKED. Show as "X/Y topics" with the label.

**Dashboard format:**

```
╔══════════════════════════════════════════════════╗
║  QDD LEARNING SYSTEM       Day {streak} Streak   ║
║                                                  ║
║  Progress: {bar}  {complete}/13                  ║
║  Interview-ready in: {days} days                 ║
║                                                  ║
║  {for each topic: number, short name, 6 dots, status label}
║                                                  ║
║  TODAY'S MISSION: {step} — {topic}               ║
║  Est. time: ~{time} min                          ║
║                                                  ║
║  "Let's go" to start  |  "skip to [step]"        ║
╠══════════════════════════════════════════════════╣
║  UNLOCKS                                         ║
║  {for each unlock: label, progress, UNLOCKED/locked}
╚══════════════════════════════════════════════════╝
```

**Commands Aaron can use:**
- "let's go" — start the next mission
- "skip to [step]" — jump to a specific step for current topic (e.g., "skip to practice")
- "teach me topic XX" — start/resume a specific topic
- "drill me on XX" — interview drill on any completed topic
- "show my progress" — re-render dashboard
- "set flag [flag_name]" — manually set a flag (e.g., after collecting test data)

---

## Step Behaviors

### Step 1: DIAGNOSE

**For topics 01-04** (already have Part 1 answers in workbook files):
1. Read the workbook file: `testing/learn/workbooks/{topic_number}-{topic_slug}.md`
2. Review Aaron's written Part 1 answers
3. Identify gaps — concepts where his answer was wrong, vague, or blank
4. Save gaps to `progress.json` under `topics.{XX}.gaps`
5. Summarize: "I've read your Part 1 answers. Here are the gaps I'll focus the lesson on: [list]"
6. Mark `diagnose.done = true`, set `diagnose.date` to today

**For topics 05-13** (no prior Part 1 attempt):
1. Read the workbook file to see Part 1 questions
2. Ask 3-4 key diagnostic questions conversationally (not all Part 1 questions — just enough to map the terrain)
3. Based on Aaron's answers, identify gaps
4. Save gaps to `progress.json`
5. Mark `diagnose.done = true`

**Transition:** "Ready for the lesson? These are the concepts we'll build: [gap list]"

### Step 2: LEARN (Live Lesson)

**This is the most important step.** The quality of teaching here determines whether Aaron actually learns.

**Read the gaps** from `progress.json` for this topic. Teach ONLY the gaps — don't re-teach what Aaron already knows.

**Teaching method — for EACH gap concept:**

1. **Anchor** (1-2 sentences)
   Connect to something physical Aaron has touched. His D6374 motor, his 3D-printed planetary gearbox, his ODrive controller, or a concept from his MECH courses (330 dynamics, 345 fluids/thermo, 360 machine design, 380 controls).
   - ONLY use analogies that are mechanistically honest. If there isn't a clean analogy, skip this and go straight to the mechanism.
   - BAD: "Iq is like water pressure" (not mechanistically parallel)
   - GOOD: "You've felt the motor resist when you try to turn the shaft by hand. That resistance is proportional to the current the controller has to push through." (directly connects to the physics)

2. **Trace the mechanism** (the core — spend the most time here)
   Walk the cause → effect chain, one link at a time. After each link, ask Aaron to predict or explain the next link.
   - "Current flows through stator windings → [what does that create?]"
   - Aaron answers → confirm or correct → "That magnetic field interacts with the rotor magnets → [what happens?]"
   - Keep going until the full chain is built
   - If Aaron gets a link wrong, don't just correct — explain WHY the wrong model fails and WHY the correct model works

3. **Prove with numbers** (1-2 minutes)
   Use Aaron's actual hardware values:
   - Motor: D6374-150KV, $K_t = 0.0551$ Nm/A, $K_v = 150$ RPM/V, 7 pole pairs
   - Gearbox: 5:1 planetary, ~90% efficiency
   - Controller: ODrive v3.6, 8 kHz FOC loop
   - Supply: 24V nominal

   Plug values into the equation just derived. "So if $I_q = 3.2$ A, torque = $0.0551 \times 3.2$ = ...?" Let Aaron calculate.

4. **Predict + verify** (1-2 minutes)
   Pose a "what if" that tests whether the model is truly understood, not just memorized:
   - "What if we used a 300KV motor instead? What happens to Kt? To torque at the same current? Why?"
   - "What if I told you Iq reads 2.5A at no-load low speed — is that good or bad? What does it tell you?"
   - Aaron reasons through it. If wrong, trace back to which link in the chain broke.

**Do NOT move to the next concept until the current one clicks.** If Aaron says "I think I get it," probe:
- "Okay, quick check: [question that requires applying the concept, not just recalling it]"
- If he nails it → move on
- If he fumbles → "Not quite — let's look at the [specific link] again"

**After all gaps are taught:**
1. Mark `learn.done = true` and set `learn.date` to today in `progress.json`
2. "Lesson complete. Ready to distill your reference card?"

**Topic pairing:** When teaching paired topics (01+02, 04+05, 06+07), teach them in one session but update BOTH topics' progress separately.

### Step 3: DISTILL

1. Ask Aaron: "In your own words, what are the 3-5 key things you now understand about [topic]? Just tell me — I'll write the card."
2. Aaron explains in conversation
3. Write the reference card to `testing/learn/cards/{XX}-{topic-slug}.md` using this format:

```markdown
# [Topic Name] — Reference Card

> Written by Aaron on [date]
> Reviewed by Claude for accuracy

## Key Concepts

[Aaron's explanations, cleaned up for clarity but preserving his voice and word choices]

## The Chain

[The cause → effect chain(s) for this topic's core relationships, as Aaron traced them]

## Numbers That Matter

[Specific values from his hardware with what they mean — pulled from the lesson]
```

4. Show Aaron the card and ask: "Anything you'd change or add?"
5. Fix any accuracy issues (wrong physics, missing links in the chain)
6. Mark `distill.done = true` in `progress.json`

### Step 4: PRACTICE

1. Read the workbook: `testing/learn/workbooks/{XX}-{topic-slug}.md`
2. Ask Part 2 (Applied Problems), Part 3 (Design Judgment), and Part 4 (Teach It) questions one at a time
3. For each question:
   - Present the question clearly (include any given values)
   - Wait for Aaron's answer
   - Grade immediately: **Solid** (correct with good reasoning), **Partial** (right direction but missing key details or reasoning), **Redo** (fundamentally wrong or blank)
   - If Partial or Redo: briefly explain what was missing, trace back to the relevant mechanism
   - Move to next question
4. Track scores as you go
5. Mark `practice.done = true` in `progress.json`
6. Transition: "Practice done. Let me compile the grade summary."

### Step 5: GRADE (includes review)

1. Present a summary table:

```
## Topic XX Grade Summary

| Question | Grade | Notes |
|----------|-------|-------|
| P1a      | Solid | — |
| P1b      | Partial | Missed efficiency factor |
| D1       | Redo  | Didn't connect to pole pair count |
| T1       | Partial | Good intuition, needs mechanism depth |

**Overall: XS YP ZR**
```

2. **Part 1 re-check:** For any gaps from Diagnose that were marked as major misunderstandings, ask 1-2 quick verification questions to confirm the lesson stuck:
   - "Quick check from earlier — why is $I_d$ set to zero?" (if that was a gap)
   - Grade these informally — just confirm the model is there

3. **Live probing on Partial/Redo:** For each Partial or Redo grade, ask a follow-up that targets the specific mechanism Aaron missed. Re-teach if needed (briefly — this is a review, not a full lesson).

4. Save score to `progress.json`: `topics.{XX}.steps.grade.score = { "solid": X, "partial": Y, "redo": Z }`
5. Mark `grade.done = true`

**Redo policy:** No gates. If Aaron has multiple Redo grades, the re-teaching here addresses them. The Interview Drill is the final check. Flag persistent gaps but let the topic progress.

### Step 6: INTERVIEW DRILL

1. Announce: "Interview drill — I'm your Tesla interviewer now. No notes, no reference. Just you and the physics."

2. Ask 5-7 rapid-fire first-principles questions on this topic:
   - Start with "explain X" (tests recall and communication)
   - Follow with "why?" probes (tests depth)
   - Then "what if?" scenarios (tests flexibility of understanding)
   - Then "how would you verify?" (tests engineering judgment)
   - End with a cross-topic connection if applicable (tests integration)

3. **Probe style:**
   - Don't accept surface answers. If Aaron says "because of Lorentz force," ask "walk me through that — what's the Lorentz force doing specifically in your motor?"
   - If Aaron breaks (can't answer), teach the gap briefly, then move to the next question
   - Keep pace brisk — this should feel like a real interview, not a leisurely tutoring session

4. After the drill, give a brief assessment:
   - "Interview-ready on this topic: Yes / Almost / Not yet"
   - If Almost/Not yet: "The gap is [specific concept]. Revisit with 'drill me on XX' after reviewing your reference card."

5. Mark `drill.done = true` in `progress.json`

6. **Check for newly unlocked milestones:** After marking drill complete, evaluate all unlocks. If any newly unlocked, announce it:
   - "UNLOCKED: [label]! You've earned this — [brief encouragement tied to what they can now do]"

---

## Progress Updates

**After EVERY step completion:**
1. Read current `progress.json`
2. Update the relevant step's `done` field to `true` and set `date` to today
3. Update `streak.last_activity` to today
4. Recalculate streak if needed (if last_activity was yesterday, increment `streak.current`; if it was today, no change; if older, set to 1)
5. If `streak.current > streak.longest`, update `streak.longest`
6. Check all unlocks — if all required_topics have all 6 steps done (and flag met if required), set `unlocked: true`
7. Write updated JSON back to `testing/learn/progress.json`

**Use this Bash command pattern to read progress.json:**
```bash
cat testing/learn/progress.json
```

**Use Python to write updates** (avoids JSON formatting issues):
```bash
python -c "
import json
with open('testing/learn/progress.json', 'r') as f:
    data = json.load(f)
# ... make changes ...
with open('testing/learn/progress.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

---

## Session Resumption

When `/learn` is invoked and `progress.json` already has progress:
- Render dashboard showing current state
- Identify where Aaron left off (first topic with incomplete steps, first incomplete step)
- Offer to continue: "You're on Topic XX, step [step]. Pick up where you left off?"
- Aaron can also jump to any topic/step with commands

---

## Teaching Quality Rules

These rules are non-negotiable. They define the difference between "running through motions" and "actually building first-principles understanding."

1. **Never present information without building the causal chain.** Don't say "Kt = 8.27/Kv because of unit conversion." Instead: "Kv is in RPM/V. Kt needs to be in Nm/A. To convert RPM to rad/s you divide by 60 and multiply by 2π. So Kt = 1/(Kv × 2π/60) = 60/(2π × Kv) = 9.55/Kv... wait, that gives 9.55. The 8.27 comes from using peak line-to-line voltage rather than phase voltage — there's a √3/2 factor. Let's trace through that..."

2. **Never accept "I think I get it" without probing.** Always follow up with a question that requires APPLYING the concept, not just recalling it.

3. **Use Aaron's hardware values, not abstract variables.** "$K_t = 0.0551$ Nm/A" is more real than "$K_t$". "Your 5:1 gearbox" is more real than "gear ratio N."

4. **When Aaron gets something wrong, explain WHY the wrong model fails.** Don't just correct — contrast. "You said X. That would mean [consequence]. But we know [observation], which contradicts that. The actual mechanism is Y, which explains [observation] because..."

5. **Trace back to physics, not to authority.** Never say "the textbook says..." or "it's defined as...". Always trace to the physical mechanism. If a definition exists, explain why that definition captures the physics.

6. **No filler, no cheerleading.** Don't say "Great question!" or "That's a really important concept!" Just teach. Aaron will know it's important because he's using it.

7. **Use MathJax notation** ($..$ for inline, $$...$$ for display) since Aaron reads in Obsidian.

---

## Hardware Context (for teaching)

Always available for real-number examples:

| Parameter | Value | What it means |
|-----------|-------|--------------|
| Motor | D6374-150KV | Large outrunner BLDC, designed for drones/e-bikes |
| $K_v$ | 150 RPM/V | Relatively low — high torque, moderate speed |
| $K_t$ | 0.0551 Nm/A | Each amp of $I_q$ produces 55.1 mNm of torque |
| Pole pairs | 7 | 7 electrical cycles per mechanical revolution |
| Gear ratio | 5:1 | Output turns 5x slower, 5x more torque (minus losses) |
| Efficiency | ~90% | Estimated; will be measured in test campaign |
| Controller | ODrive v3.6 | FOC at 8 kHz, reports $I_q$, $I_d$, encoder position |
| Supply voltage | 24V nominal | Sets the ceiling for back-EMF and therefore max speed |
| No-load $I_q$ | ~0.4A (expected) | Just overcoming internal friction |
| Gearbox material | PLA (3D printed) | Affects friction, compliance, thermal limits |
````

- [ ] **Step 2: Copy the skill to the backup location**

```bash
mkdir -p claude-tools/skills/learn
cp .claude/skills/learn/SKILL.md claude-tools/skills/learn/SKILL.md
```

- [ ] **Step 3: Verify the skill is discoverable**

Run: `ls .claude/skills/learn/SKILL.md` — should exist.

In a new Claude Code session, `/learn` should appear in the skills list.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/learn/SKILL.md claude-tools/skills/learn/SKILL.md
git commit -m "feat: add /learn skill for QDD learning system v2

Conversational learning system with 6-step workflow, dashboard,
streaks, unlocks, and detailed teaching methodology. All learning
happens in conversation — no file editing required by the user."
```

---

### Task 3: Update CLAUDE.md files with /learn skill

**Files:**
- Modify: `qdd-gearbox/CLAUDE.md` (if it has a skills/commands section)
- Modify: `CLAUDE.md` (root — skills table)

- [ ] **Step 1: Read both CLAUDE.md files to find where skills are listed**

Check `qdd-gearbox/CLAUDE.md` for any skill/command references.
Check root `CLAUDE.md` for the skills table.

- [ ] **Step 2: Add /learn to the root CLAUDE.md skills table**

Add this row to the skills table in `CLAUDE.md`:

```
| **learn** | `/learn` | QDD conversational learning — dashboard, lessons, practice, drills |
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md qdd-gearbox/CLAUDE.md
git commit -m "docs: add /learn skill to CLAUDE.md skills tables"
```

---

### Task 4: Create the nudge notification script

**Files:**
- Create: `claude-tools/scripts/qdd-nudge.ps1`

This PowerShell script checks `progress.json` and shows a Windows toast notification if no study activity was logged today. It's designed to be run by Windows Task Scheduler.

- [ ] **Step 1: Write the nudge script**

Create `claude-tools/scripts/qdd-nudge.ps1`:

```powershell
# QDD Learning System — Evening Nudge
# Checks progress.json for today's activity. Shows toast if none.
# Schedule via Task Scheduler to run at desired time (default: 7pm).

param(
    [string]$ProgressFile = "$env:USERPROFILE\Documents\c-projects\qdd-gearbox\testing\learn\progress.json"
)

# Check if progress file exists
if (-not (Test-Path $ProgressFile)) {
    Write-Host "Progress file not found: $ProgressFile"
    exit 1
}

# Read progress
$progress = Get-Content $ProgressFile -Raw | ConvertFrom-Json
$lastActivity = $progress.streak.last_activity
$today = (Get-Date).ToString("yyyy-MM-dd")

if ($lastActivity -eq $today) {
    Write-Host "Activity logged today. No nudge needed."
    exit 0
}

# Find next step
$nextTopic = $null
$nextStep = $null
$stepOrder = @("diagnose", "learn", "distill", "practice", "grade", "drill")
$stepTimes = @{ "diagnose" = "15"; "learn" = "35"; "distill" = "15"; "practice" = "50"; "grade" = "15"; "drill" = "10" }

foreach ($topicNum in ($progress.topics.PSObject.Properties.Name | Sort-Object)) {
    $topic = $progress.topics.$topicNum
    foreach ($step in $stepOrder) {
        if (-not $topic.steps.$step.done) {
            $nextTopic = $topic.name
            $nextStep = $step
            $nextTime = $stepTimes[$step]
            break
        }
    }
    if ($nextTopic) { break }
}

if (-not $nextTopic) {
    Write-Host "All topics complete!"
    exit 0
}

# Calculate streak status
$streakText = if ($progress.streak.current -gt 0) {
    "Don't break your $($progress.streak.current)-day streak!"
} else {
    "Start a new streak today!"
}

# Show toast notification using WinRT
$title = "QDD Study Reminder"
$message = "No study today. $nextTime min on $nextStep for $nextTopic? $streakText"

# Use PowerShell to create a toast notification
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast>
    <visual>
        <binding template="ToastGeneric">
            <text>$title</text>
            <text>$message</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("QDD Learning System")
$notifier.Show($toast)

Write-Host "Nudge sent: $message"
```

- [ ] **Step 2: Test the script manually**

Run: `powershell -ExecutionPolicy Bypass -File claude-tools/scripts/qdd-nudge.ps1`

Expected: Either "Activity logged today. No nudge needed." (if progress was updated today) or a toast notification appears.

- [ ] **Step 3: Create the Windows scheduled task**

Run in PowerShell (requires elevation — Aaron may need to approve):

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$env:USERPROFILE\Documents\c-projects\claude-tools\scripts\qdd-nudge.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 7:00PM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "QDD-Study-Nudge" -Action $action -Trigger $trigger -Settings $settings -Description "QDD Learning System evening study reminder"
```

Expected: Task "QDD-Study-Nudge" created. Verify: `Get-ScheduledTask -TaskName "QDD-Study-Nudge"`

- [ ] **Step 4: Commit**

```bash
git add claude-tools/scripts/qdd-nudge.ps1
git commit -m "feat: add evening nudge notification script

PowerShell script checks progress.json for today's activity and
shows a Windows toast notification suggesting the smallest next
step if no study was logged. Designed for Task Scheduler at 7pm."
```

---

### Task 5: Create startup shortcut

**Files:**
- Create: Windows Startup folder shortcut

This opens Claude Code in the qdd-gearbox directory on login so `/learn` is one command away.

- [ ] **Step 1: Create the startup shortcut**

Run in PowerShell:

```powershell
$startupPath = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupPath "QDD-Learn.lnk"

# Create shortcut that opens Windows Terminal in qdd-gearbox directory
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wt.exe"
$shortcut.Arguments = "-d `"$env:USERPROFILE\Documents\c-projects\qdd-gearbox`""
$shortcut.Description = "Open terminal in QDD project for /learn"
$shortcut.Save()

Write-Host "Startup shortcut created at: $shortcutPath"
```

Note: This opens a terminal in the right directory. Aaron can then type `claude` and `/learn` to start. We don't auto-launch Claude Code because it might not always be wanted on every boot.

- [ ] **Step 2: Verify the shortcut exists**

Run: `ls "$([Environment]::GetFolderPath('Startup'))/QDD-Learn.lnk"`

- [ ] **Step 3: Commit (nothing to commit — shortcut is outside the repo)**

No git commit needed — the shortcut lives in the Windows Startup folder, not in the repo.

---

### Task 6: Populate gaps for topics 02-04 from existing workbook answers

**Files:**
- Modify: `testing/learn/progress.json`
- Read: `testing/learn/workbooks/02-torque-speed-envelope.md`
- Read: `testing/learn/workbooks/03-thermal.md`
- Read: `testing/learn/workbooks/04-friction-backdrivability.md`

Aaron said he completed Part 1 for workbooks 01-04. Topic 01 gaps are already populated from the grading earlier in this session. We need to read 02-04 workbook files and populate their gaps.

- [ ] **Step 1: Read workbook 02 Part 1 answers**

Read `testing/learn/workbooks/02-torque-speed-envelope.md` — look at Aaron's Part 1 (Concept Check) responses and confidence ratings.

- [ ] **Step 2: Read workbook 03 Part 1 answers**

Read `testing/learn/workbooks/03-thermal.md` — same.

- [ ] **Step 3: Read workbook 04 Part 1 answers**

Read `testing/learn/workbooks/04-friction-backdrivability.md` — same.

- [ ] **Step 4: Analyze gaps and update progress.json**

For each workbook (02-04), identify concepts where Aaron's answer was:
- Blank or "I don't know"
- Vague / wrong direction
- Missing key mechanisms

Update `topics.{02,03,04}.gaps` arrays in `progress.json` with the identified gap concepts.

Use Python to update:
```bash
python -c "
import json
with open('testing/learn/progress.json', 'r') as f:
    data = json.load(f)

# Fill in gaps based on workbook review
data['topics']['02']['gaps'] = [...]  # populated from review
data['topics']['03']['gaps'] = [...]
data['topics']['04']['gaps'] = [...]

with open('testing/learn/progress.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Gaps updated for topics 02-04')
"
```

- [ ] **Step 5: Commit**

```bash
git add testing/learn/progress.json
git commit -m "feat: populate diagnosed gaps for topics 02-04

Read existing Part 1 workbook answers and extracted gap lists
for topics 02 (torque-speed), 03 (thermal), 04 (friction)."
```

---

### Task 7: End-to-end test — run `/learn` and verify dashboard

**Files:** None (testing only)

- [ ] **Step 1: Start a fresh Claude Code session in qdd-gearbox directory**

- [ ] **Step 2: Type `/learn`**

Expected: Skill activates, reads progress.json, renders dashboard showing:
- 0/13 complete
- Topics 01-04 diagnosed (1 dot each), 05-13 not started
- Streak: Day 1 (or reset if next day)
- Today's mission: Learn — Topic 01 Motor Fundamentals
- Unlocks all locked

- [ ] **Step 3: Type "let's go"**

Expected: Claude begins the Step 2 (Learn) lesson for Topic 01, targeting the gaps in progress.json. Uses the teaching methodology: anchor → trace → numbers → predict.

- [ ] **Step 4: Verify progress saves after completing a step**

After completing the learn step, check `testing/learn/progress.json`:
- `topics.01.steps.learn.done` should be `true`
- `streak.last_activity` should be today
- `streak.current` should be updated

- [ ] **Step 5: Document any issues**

If something doesn't work (skill not found, JSON parsing error, dashboard rendering issue), document the problem and fix it before declaring the task complete.

---

## Post-Implementation Notes

- The `/learn` skill is instruction-based, not code-based. Its quality depends on how well Claude follows the encoded teaching methodology. If teaching quality drifts, the fix is refining the SKILL.md instructions, not writing more code.
- Reference cards (`testing/learn/cards/`) are created during the distill step, not pre-created. The directory starts empty.
- The nudge time (7pm) can be adjusted by modifying the scheduled task trigger.
- The startup shortcut opens a terminal, not Claude Code directly. Aaron starts Claude when ready.
