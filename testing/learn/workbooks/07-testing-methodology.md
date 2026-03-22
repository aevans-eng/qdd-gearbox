# Testing Methodology — Workbook 07

> **Format:** Design judgment + scenarios
> **Reference material:** `testing/methodology/testing-fundamentals.md`, `testing/qdd-rtm.xlsx`
> **Estimated time:** 30-45 min
> **Context:** 13 requirements, 19 tests across 5 phases, V-model test hierarchy

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 07"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: Name the four test levels in the V-model hierarchy (bottom to top). Give one example from your QDD project at each level. Why must lower levels pass before upper levels?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: What's the difference between a requirement, an unknown, and an acceptance criterion? Give one concrete example of each from your QDD project.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: Why do you define acceptance criteria BEFORE running the test? What goes wrong if you define them after seeing the data?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: What does "traceability" mean in a test campaign? Why does every test need to trace back to a requirement or unknown?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: Explain the risk × uncertainty priority matrix. What goes in each quadrant? Give an example of a high-risk, high-uncertainty item from your gearbox.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Dependency chain mapping

Your campaign has 5 phases. Draw (or describe) the dependency chain:

**(a)** Which Phase 0 tests must pass before which Phase 2 tests can run?

**(b)** Can Phase 1 tests run in parallel with Phase 0? Why or why not?

**(c)** Is there any test in the campaign that has no upstream dependency? If so, which one and why?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Prioritization under time constraints

You have **2 hours** of lab time. You need to choose between these three activities:

- **(a)** T-012: Backlash measurement (30 min, requires assembly, answers R-01)
- **(b)** Thermal test at peak torque (90 min, requires Phase 2 complete, answers R-08)
- **(c)** Visual inspection of gear mesh quality (15 min, no prerequisites, answers U-01)

Using the risk × uncertainty framework and the dependency rules, **order these three** and explain your reasoning. Which do you actually do in the 2 hours?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Should you proceed past a failed Phase 1?

Your gearbox fails the backlash test at Phase 1: measures **0.8°** vs the 0.5° requirement.

**(a)** Argue FOR proceeding to Phase 2 powered testing anyway.

**(b)** Argue AGAINST proceeding — why stop here?

**(c)** Make your recommendation. What would you actually do?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: Inconclusive test results

T-006 (friction characterization) results show friction that's **3× higher than your model predicts**. The result is "inconclusive."

List 3 possible explanations — one from each category:
- **(a)** Test design issue (the test itself was flawed)
- **(b)** Hardware issue (something is physically wrong)
- **(c)** Model issue (your friction model is wrong)

For each, describe how you'd triage it.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Why phased testing matters

Your audience: a student who's never run a test campaign and asks: "Why can't you just test everything at once? Wouldn't that be faster?"

Explain the value of phased testing using your QDD campaign as the example. Why does the order matter?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
