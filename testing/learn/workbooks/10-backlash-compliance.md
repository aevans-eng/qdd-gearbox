# Backlash & Compliance — Workbook 10

> **Format:** Pre/post-lab (Phase 1 backlash measurement tests)
> **Reference material:** `testing/learn/campaign-walkthrough.md`, `testing/campaign/test-campaign-rev00b.md` (T-012, T-013)
> **Estimated time:** 25-35 min (pre-lab), 20-30 min (post-lab after test data)
> **Hardware:** 5:1 PLA+ planetary, dial indicator, kitchen scale + 200 mm lever arm

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 10"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

# PRE-LAB — Complete Before Running Phase 1 Tests

## Part 1: Concept Check

### Q1: What is backlash in a gear system? What physical feature of the gear teeth causes it? Can you eliminate it completely?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: Why is backlash the #1 specification for a QDD? How does it affect (a) positioning accuracy, (b) impedance control transparency, and (c) force sensing?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: What's the difference between backlash (deadband/lost motion) and compliance (elastic deflection of PLA teeth under load)? Both cause output error — how do they differ mechanically?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: Describe the T-012 measurement method: what's locked, what moves, how is the angular play captured? Why do you measure at 4+ positions around the revolution?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: What is a hysteresis plot (output angle vs applied torque)? Sketch the expected shape. What does the flat region near zero torque represent? What does the slope after engagement represent?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Converting a dial indicator reading to angular backlash

Your dial indicator reads **0.15 mm** of linear play at a radius of **40 mm** from the output shaft center.

**(a)** Calculate the angular backlash in degrees: $\Delta\theta = \arctan(\delta / r)$.

**(b)** Does this pass the ≤ 0.5° requirement (R-01)?

**(c)** If you moved the indicator to a radius of 80 mm, what linear reading would correspond to the same angular backlash? Why does a longer lever arm give better measurement resolution?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Backlash through the gear ratio

**(a)** If output backlash is 0.3°, what is the backlash at the motor side (through 5:1)?

**(b)** Your encoder has 16384 CPR. How many encoder counts does 0.3° of output backlash correspond to at the motor?

**(c)** Why does backlash at the output cause a "dead zone" in encoder-based position control? The encoder is on the motor side — can it even see the backlash?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

# POST-LAB — Complete After Phase 1 Test Data

> [COMPLETE AFTER TEST DATA] Fill in these sections after you have T-012 and T-013 measurements.

## Part 3: Design Judgment

### D1: Non-uniform backlash around the revolution

Your backlash varies from **0.2° to 0.6°** depending on the output shaft position.

**(a)** What does this non-uniformity tell you about the gearbox assembly? (Hint: think about what changes as the output rotates.)

**(b)** List 2 possible causes: one related to the planets, one related to the carrier/housing.

**(c)** If you had to choose one number to report, would you use the max, the min, or the average? Why?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: Backlash growth over time

After 2 hours of testing, you re-measure backlash and it's grown from **0.3° to 0.45°**.

**(a)** Is this expected for PLA gears? What's happening physically — wear, creep, or something else?

**(b)** At this rate of growth, how long before you exceed the 0.5° requirement?

**(c)** Should you be concerned? What would you do about it?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Backlash and impedance control — your real numbers

Using your actual measured backlash, explain to a controls engineer:

"Here's the backlash in my QDD. Here's how it affects impedance control. Here's what I did about it (or plan to do)."

Ground your explanation in physics, not hand-waving.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
