# FEA Literacy — Workbook 13

> **Format:** Design judgment + scenarios
> **Reference material:** MECH 360 course material, general FEA principles
> **Estimated time:** 30-45 min
> **Context:** PLA+ FDM gearbox under ~16 Nm peak torque, gear tooth stress, carrier shoulder loads

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 13"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: What does FEA solve, at a high level? What physical equations is it approximating? (Think: equilibrium, compatibility, constitutive law — what does each mean?)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: What is meshing in FEA? Why does mesh density matter? What goes wrong if the mesh is too coarse? What's the downside of making it extremely fine?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: Name 3 types of boundary conditions (e.g., fixed support, pinned, symmetry, applied pressure, prescribed displacement). For each, describe when you'd use it and give an example from your gearbox.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: What is a stress singularity? Where do they typically appear in an FEA model? Why should you recognize them and not treat them as real stress values?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: How do you know if your FEA results are trustworthy? Name 2 validation approaches you can use before trusting the numbers.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Setting up an FEA for the carrier bearing shoulder

You want to analyze the carrier bearing shoulder — it's PLA, and you suspect it might fail under the 16 Nm output torque.

Describe your FEA setup:

**(a)** What geometry do you model? Full part, simplified section, or 2D? Why?

**(b)** What loads do you apply? Where does the 16 Nm manifest as force on the shoulder? (Trace the load path.)

**(c)** What boundary conditions? What's fixed and what's free?

**(d)** What material properties do you use for PLA+? Are they isotropic? (Hint: FDM is not isotropic.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Interpreting FEA results

Your FEA shows a peak von Mises stress of **35 MPa** at a gear tooth root. PLA+ tensile strength is approximately **50 MPa**.

**(a)** What safety factor is that? ($SF = \sigma_{allowable} / \sigma_{actual}$)

**(b)** Is this safety factor sufficient for a 3D-printed part under cyclic loading? Why or why not?

**(c)** What does the safety factor NOT tell you about fatigue life? What additional information would you need?

**(d)** The peak stress is at a sharp fillet. If you refined the mesh at that fillet, the stress would likely increase. Why? Is the 35 MPa an upper bound or lower bound of reality?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: When FEA lies

Your FEA shows the gear teeth pass stress analysis (SF > 1.5). But the prototype breaks after 10 minutes of sustained testing.

List **4 reasons** the FEA could "pass" while reality "fails":

- At least one related to the **material model**
- At least one related to the **load case**
- At least one related to **fatigue**
- At least one related to **manufacturing/print defects**

For each, explain why FEA missed it and what you'd change in the analysis.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: "When do you trust FEA?"

A Tesla interviewer asks: "When do you trust FEA results and when don't you?"

Give a **2-minute answer** that demonstrates engineering judgment. Reference a real example from your QDD project. Include:
- When FEA is reliable (what conditions make it trustworthy)
- When it's not (what conditions should make you skeptical)
- What you do to bridge the gap (validation, testing, conservative assumptions)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: FEA for non-engineers

Your audience: a non-engineer (friend, family) who asks what FEA is.

Explain in plain language: "FEA lets me simulate stress on a computer before I break the real thing. But it's not magic — here's how it works, and here's when it lies to you." Keep it under 1 minute of spoken explanation.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
