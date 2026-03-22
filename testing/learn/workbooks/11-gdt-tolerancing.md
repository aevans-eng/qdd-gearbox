# GD&T & Tolerancing — Workbook 11

> **Format:** Applied problems heavy
> **Reference material:** `drawings/gdt-annotations.md`, `docs/design/tolerance-scheme.md`
> **Estimated time:** 45-60 min
> **Context:** PLA+ FDM gearbox, ISO fit system, QDD with H7 bearing bores and press-fit components

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 11"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: What is a datum reference frame? Name the three datums for your gearbox housing (A, B, C) and explain why each was chosen.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: What's the difference between a size tolerance (e.g., 22.000 ± 0.1 mm) and a geometric tolerance (e.g., ⌖ ∅0.05 | A | B)? Give a real example from your gearbox where the size could be perfect but the geometry is still wrong.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: What does H7 mean in the ISO fit system? Break it down:

- What does "H" mean? (Which part, which direction of deviation?)
- What does "7" mean? (IT grade — how tight?)
- What is the tolerance zone for a 22 mm H7 bore?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: Name 3 geometric characteristics (from the 14 GD&T symbols) and give a real example from your gearbox where each matters. Why can't you achieve the same thing with ± tolerances?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: What's the difference between concentricity (◎) and runout (↗)? Which would you call out for the bearing bore in the housing, and why?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: H7 tolerance zone calculation

Your housing bearing bore is specified as Ø22H7.

**(a)** The IT7 tolerance for 22 mm nominal (18-30 mm range) is 21 µm. For an H hole (fundamental deviation = 0), what is the min and max diameter?

**(b)** A bearing with OD 22.000 mm (tolerance: 0 to -0.008 mm) goes into this bore. What is the range of possible fits (min clearance to max clearance)?

**(c)** Is this a clearance fit, transition fit, or interference fit?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Shaft fit selection

You need a sun gear shaft to fit into a bearing inner race. The bearing ID is 8.000 mm (tolerance: 0 to -0.008 mm). You want a light interference fit (0.005 to 0.020 mm interference).

**(a)** What shaft diameter range do you need?

**(b)** What ISO shaft tolerance class achieves this? (Hint: look at k5 or m5 for 8 mm nominal.)

**(c)** Can your FDM printer achieve this tolerance? If not, what's your plan?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P3: Tolerance stackup

The carrier assembly has 3 features in series: bearing seat → carrier bore → planet pin position. Each has ±0.1 mm tolerance.

**(a)** What's the worst-case stackup? (All errors add in the same direction.)

**(b)** What's the statistical (RSS) stackup? ($\sigma_{total} = \sqrt{\sigma_1^2 + \sigma_2^2 + \sigma_3^2}$, then multiply by 3 for 99.7% coverage.)

**(c)** Your planet-to-sun center distance tolerance affects gear meshing. If the allowable center distance error is ±0.15 mm, does the stackup pass?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P4: FDM vs the spec

Your FDM printer has ±0.2 mm accuracy. You need H7 tolerance on a 22 mm bore (tolerance zone ≈ 0.021 mm — about 10× tighter than your printer).

**(a)** Can you achieve H7 as-printed? Show why numerically.

**(b)** Your compensation strategy: print the bore undersized by a known offset, then ream/sand to size. If your printer consistently prints holes 0.15 mm undersized, what nominal CAD diameter do you model?

**(c)** After compensation, what realistic tolerance can you hold on the bore? Is it closer to IT7, IT10, or IT12?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: "How would you tolerance this part?"

A Tesla interviewer hands you a gearbox carrier and asks: "Tolerance this for production."

Walk through your process:
- **(a)** How do you choose datums?
- **(b)** What features are critical (and what geometric tolerances do they need)?
- **(c)** What features don't need tight tolerances?
- **(d)** How would you verify the tolerances after manufacturing?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Why GD&T exists

Your audience: a student who's only ever used ± mm tolerances on drawings.

Explain: Why does GD&T exist? What problem does it solve that ± tolerances can't? Give one concrete example where a part could be within ± tolerance on every dimension but still not assemble correctly.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
