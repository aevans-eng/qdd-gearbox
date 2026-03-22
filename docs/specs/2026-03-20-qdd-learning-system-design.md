# QDD Learning System — Design Spec

**Date:** 2026-03-20
**Goal:** Turn QDD project knowledge into structured, graded deliverables that prepare Aaron for Tesla Optimus interviews and deep project understanding.

---

## Overview

Two-phase system:
1. **Phase 1 — Workbook assignments** (build understanding)
2. **Phase 2 — Website first-principles section** (cement by teaching)

Each of 13 topics gets a workbook. Aaron completes it open-book while taking notes, then brings it for written grading + live review (tutor skill). Completed topics feed into website explainers.

---

## Workbook Structure

**Location:** `qdd-gearbox/testing/learn/workbooks/`
**Naming:** `01-motor-fundamentals.md`, `02-torque-speed-envelope.md`, etc.

Each workbook has 4 sections:

### 1. Concept Check (5-8 questions)
Interview-style. "Explain X in 2-3 sentences." Tests cold articulation — can you say this in a Tesla interview?

### 2. Applied Problems (2-4 problems)
Tied to Aaron's actual QDD hardware (D6374-150KV, planetary gearbox, ODrive v3.6). Not abstract — grounded in real numbers.

### 3. Design Judgment (1-2 scenarios)
Open-ended, no single right answer. Tests first-principles reasoning and engineering judgment.

### 4. Teach It (1 prompt)
"Explain [topic] to a mech eng student who's never worked with actuators." Becomes the seed for website Phase 2.

### Answer Format
```markdown
### Q1: [Question text]

> **Your answer:**
> [write here]
>
> **Confidence:** [high / medium / low]
```

Confidence tag guides live review — low-confidence answers get probed first even if correct.

### Section Weighting by Format
The "Primary Format" in the topic table controls how questions are distributed across sections:
- **Interview Q&A heavy** → 7-8 Concept Check questions, 2 Applied Problems
- **Applied problems heavy** → 5 Concept Check, 3-4 Applied Problems
- **Design judgment heavy** → 5 Concept Check, 2 Applied, 2 Design Judgment scenarios
- **Pre/post-lab** → pre-lab Concept Check + Applied before testing, post-lab Design Judgment + Teach It after data

### Grading Workflow
Aaron fills in answers directly in the workbook markdown file, then starts a new Claude session referencing the completed workbook. Written grading happens first (all answers scored), then live review (tutor skill) targets gaps.

---

## Topic Sequence

Dependency order. Each topic builds on previous ones.

| # | Topic | Primary Format | Rationale |
|---|-------|---------------|-----------|
| 1 | Motor fundamentals ($K_t$, $K_v$, $I_q$/$I_d$, FOC, back-EMF) | Interview Q&A heavy | Need these answers cold |
| 2 | Torque-speed envelope (saturation, voltage limits, continuous vs peak) | Applied problems heavy | Best learned by calculating with real numbers |
| 3 | Thermal ($I^2R$, iron losses, lumped models, derating) | Applied + design judgment | "It depends" thinking matters most here |
| 4 | Friction & backdrivability (Coulomb+viscous, gear losses, transparency) | Pre/post-lab (T-011 motor-only → Phase 2 motor+gearbox comparison) | Learn by doing — tied to test execution |
| 5 | Gearbox mechanics (ratios, reflected inertia, contact ratio, tooth stress) | Applied problems heavy | Designed the gearbox — own the math |
| 6 | Measurement & instrumentation ($I_q$ as torque proxy, calibration, error) | Design judgment heavy | No formula — engineering reasoning |
| 7 | Testing methodology (V&V hierarchy, system vs component, traceability) | Design judgment + scenarios | Systems thinking |
| 8 | Dynamics & system ID (transfer functions, step response, Bode) | Applied problems heavy | Math that needs practice |
| 9 | Impedance control (virtual spring/damper, bandwidth, why QDD) | Interview Q&A + applied | Cornelius said this matters |
| 10 | Backlash & compliance (hysteresis, limit cycles, preload) | Pre/post-lab (Phase 1 backlash measurement tests) | Learn when you measure it |
| 11 | GD&T & tolerancing (datums, FCFs, tolerance stackups) | Applied problems heavy | "Tolerance this gear mesh" needs practice |
| 12 | DFM & manufacturing (material selection, process, cost reasoning) | Design judgment heavy | Reasoning, not formulas |
| 13 | FEA literacy (setup, validation, failure modes, when to trust) | Design judgment + scenarios | Engineering judgment |

**Topics 4 & 10** have pre-lab questions now, post-lab questions added after test data exists.

**Suggested pace:** ~2 topics/week from study time budget. Topics 1-5 first (foundational for Phase 0 execution).

---

## Grading System

### Written Grading (per answer)
- **Correctness** — is the physics/engineering right?
- **Depth** — surface-level or real understanding? Shallow restatement vs. mechanistic explanation.
- **Clarity** — interview-ready phrasing? Rambling gets flagged.

### Answer Ratings
- **Solid** — knows it, move on
- **Partial** — right idea, missing something important
- **Redo** — fundamental gap, needs another attempt before live review

### Live Review (tutor skill)
After written grading:
- **Low confidence answers** probed first, even if correct
- **Partial answers** get follow-up questions that guide toward the gap (not just told the answer)
- **Solid answers** get one curveball — a "what if" twist to test beyond memorization

### Completion Criteria
Topic is done when every answer is Solid and curveballs are survived. No participation trophies.

### Progress Tracking
Tracker file in workbooks folder: `_progress.md`

```markdown
| # | Topic | Status | Written Grade | Live Review | Date Completed | Notes |
|---|-------|--------|--------------|-------------|----------------|-------|
| 1 | Motor fundamentals | Not started | — | — | — | — |
```

**Status values:** Not started → In progress → Grading → Live review → Complete
**Written Grade column:** count of Solid / Partial / Redo across all answers (e.g., "8S 2P 0R")

---

## Phase 2: Website First-Principles Section

### Trigger
The website infrastructure (page, route, layout) gets set up after topics 1-5 are all passed. After that, any individual completed topic can become an explainer immediately — no need to wait for others.

### Location
`aaronevans.ca/first-principles/` — not in main nav, accessible via direct link.

### Explainer Structure (per topic)
1. **The question** — what real problem does this concept solve?
2. **The physics** — derive from first principles, using QDD motor numbers as running example
3. **The gotcha** — what goes wrong if you get this wrong, or the non-obvious subtlety
4. **Your data** — reference actual QDD test results where applicable

### Character
Not a blog. Not textbook summaries. Short, dense, well-formatted pages with math and diagrams. A personal engineering reference that happens to be public.

---

## File Inventory

```
qdd-gearbox/testing/learn/workbooks/
├── _progress.md                      # Topic status tracker
├── 01-motor-fundamentals.md
├── 02-torque-speed-envelope.md
├── 03-thermal.md
├── 04-friction-backdrivability.md
├── 05-gearbox-mechanics.md
├── 06-measurement-instrumentation.md
├── 07-testing-methodology.md
├── 08-dynamics-system-id.md
├── 09-impedance-control.md
├── 10-backlash-compliance.md
├── 11-gdt-tolerancing.md
├── 12-dfm-manufacturing.md
└── 13-fea-literacy.md
```

---

## Reference Material Per Topic

| Topic | Primary Sources |
|-------|----------------|
| 1-3 | `testing/learn/motor-physics-primer.md`, `calc/thermal.py` |
| 4 | `testing/learn/campaign-walkthrough.md` (friction model), campaign Phase 0 |
| 5 | `calc/gear_geometry.py`, `calc/tooth_stress.py`, `calc/bearing_life.py` |
| 6 | `testing/learn/campaign-walkthrough.md` ($I_q$ as sensor), `research/gemini-deep-research/01-actuator-testing-methodology/response.md` |
| 7 | `testing/methodology/testing-fundamentals.md`, `testing/qdd-rtm.xlsx` |
| 8 | Campaign Phase 3 (`testing/campaign/test-campaign-rev00b.md`), MECH 380 course material |
| 9 | Campaign Phase 4, `research/gemini-deep-research/01-actuator-testing-methodology/response.md` (impedance tiers section) |
| 10 | Campaign Phase 1, `testing/learn/campaign-walkthrough.md` |
| 11 | `drawings/` (GD&T annotation notes), MECH 360 course material |
| 12 | `docs/design/` (DFM docs, material/process decisions), `docs/original-documentation-jan4/trade-studies.md` |
| 13 | New reference material needed — no existing FEA docs in project. Source from course material or create primer. |
