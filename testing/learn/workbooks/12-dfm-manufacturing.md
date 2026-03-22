# DFM & Manufacturing — Workbook 12

> **Format:** Design judgment heavy
> **Reference material:** `docs/design/manufacturing-tips.md`, `docs/design/tolerance-scheme.md`, `docs/original-documentation-jan4/trade-studies.md`
> **Estimated time:** 30-45 min
> **Context:** FDM PLA+ gearbox, heat-set inserts, ±0.2 mm printer accuracy, budget < $120 CAD

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 12"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: What does DFM (Design for Manufacturability) mean in practice? Give 3 specific examples from your gearbox where the design was constrained or changed because of how it's manufactured.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: Why does print orientation matter for FDM gears? Which orientation gives the strongest tooth roots? What happens if you print gear teeth perpendicular to the layer lines?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: What is a calibration coupon and why should you print one with every batch of parts? What do you measure on it?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: Heat-set inserts: why use them in 3D prints instead of self-tapping screws? What are the key design rules (pilot hole diameter, depth, perimeter wall thickness)?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: Your FDM printer achieves ±0.2 mm. CNC machining achieves ±0.025 mm. What design changes does FDM's lower accuracy force? Name 3 specific adaptations.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Bore compensation for press-fit bearing

You need to press-fit a bearing into a PLA housing. The bearing OD is 22.000 mm. Your printer consistently prints holes **0.15 mm undersized** (a 22.00 mm modeled hole comes out as ~21.85 mm).

**(a)** What nominal bore diameter should you model in CAD to get a printed bore of ~22.00 mm?

**(b)** You actually want a light press fit — the bore should be 0.02-0.05 mm smaller than the bearing OD. What CAD diameter targets this?

**(c)** How would you verify the printed bore before pressing in the bearing?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Backlash vs printer accuracy

Your gear teeth need to mesh with minimal backlash (target: 0.05 mm at the pitch circle).

**(a)** Your printer accuracy is ±0.2 mm per feature. Two meshing features (tooth and gap on mating gear) means ±0.4 mm worst case. Can you achieve 0.05 mm backlash as-printed?

**(b)** What is the realistic minimum achievable backlash with this printer?

**(c)** How does this inform your backlash requirement (R-01: ≤ 0.5°)? Is the requirement achievable with FDM, or does it require post-processing?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Redesigning for CNC production

A Tesla interviewer asks: "You 3D printed this gearbox. How would you redesign it for aluminum CNC production?"

Walk through the changes:
- **(a)** What changes in geometry? (Features that are easy in FDM but hard in CNC, and vice versa.)
- **(b)** What changes in tolerances? (What gets tighter? What stays the same?)
- **(c)** What changes in assembly method?
- **(d)** Rough cost comparison: your PLA prototype cost vs estimated CNC production cost for one unit.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: Diagnosing a manufacturing-related failure

Your gearbox carrier is cracking at the bearing shoulder after testing. It's PLA, printed with teeth perpendicular to the layer lines.

**(a)** What failure mode is this? (Hint: inter-layer adhesion under tension.)

**(b)** Propose 3 fixes, ranked by effort:
  - One that changes print parameters only (no CAD changes)
  - One that changes the part geometry
  - One that changes the material

**(c)** Which would you try first and why?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Why FDM for a gearbox?

Your audience: someone who's never 3D printed anything and asks: "Why would you make a gearbox out of plastic when metal is obviously stronger?"

Explain your reasoning — why you chose FDM for this project, what limitations it introduced, and how you worked around them. Make it clear this was a deliberate engineering choice, not laziness.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
