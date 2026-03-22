# Friction & Backdrivability — Workbook 04

> **Format:** Pre/post-lab (T-011 motor-only → Phase 2 motor+gearbox comparison)
> **Reference material:** `testing/learn/campaign-walkthrough.md` (friction section), `testing/campaign/test-campaign-rev00b.md` (T-011, T-006)
> **Estimated time:** 30-40 min (pre-lab), 20-30 min (post-lab after test data)
> **Hardware:** D6374-150KV, $K_t = 0.0551$ Nm/A, $N = 5$

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 04"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

# PRE-LAB — Complete Before Running T-011

## Part 1: Concept Check

### Q1: What is Coulomb friction physically? What causes it in a motor? In a gearbox?

*Your response:*

idk coulomb friction? like rubbing friction? I guess bearings, motor, gear contacts and bearings.

*Confidence:*
- [ ] High — could explain this cold in an interview
- [x] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: What is viscous friction physically? What causes it? Why does it increase with speed?

*Your response:*

Um not sure, like dampers? idk

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q3: Write the combined friction model. On a plot of $\tau_f$ vs $\omega$, what does the y-intercept represent? What does the slope represent?

*Your response:*

i have no idea

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q4: Why do you need to measure friction at multiple speeds? Why isn't one measurement enough?

*Your response:*

im not sure? shouldnt it be lienar with something? or is it not?

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q5: What does "backdrivability" mean for a QDD? Why is low friction the enabler? What's the connection to impedance control?

*Your response:*

more backdriveability, kind of means more sensitivity? more backdriveable the less stuff like friction or inertia affects the sensitivity or somethign? idk i dont nderstand well.

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q6: Gearbox friction at the output vs the motor side — how does the gear ratio affect what you feel? Write the relationship.

*Your response:*

uhhh not sure.

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Solving for friction parameters from data

You measure no-load $I_q$ at two motor speeds:
- At 2 rev/s ($\omega = 12.6$ rad/s): $I_q = 0.30$ A
- At 10 rev/s ($\omega = 62.8$ rad/s): $I_q = 0.50$ A

**(a)** Compute $\tau_f$ at each speed.

**(b)** Solve for $\tau_c$ (Coulomb friction) and $b$ (viscous coefficient). Show your work with two equations, two unknowns.

**(c)** Predict the friction torque at 20 rev/s. What $I_q$ would you expect?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Friction budget for the gearbox

Your requirement is output friction < 1 Nm (R-04).

**(a)** If motor-only friction at the motor side is $\tau_c = 0.015$ Nm, $b = 0.0003$ Nm·s/rad, what's the motor friction at a typical test speed (5 rev/s motor, $\omega = 31.4$ rad/s)?

**(b)** That motor friction, reflected to the output side through the gearbox, is the motor's contribution. How much friction budget does the gearbox get?

**(c)** The CubeMars AK70-10 (commercial QDD benchmark) has output friction ~0.97 Nm. How does your budget compare?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P3: Why the baseline subtraction matters

You run T-006 (motor + gearbox) and get total friction at the output = 0.85 Nm at a given speed.

**(a)** If you didn't have the T-011 motor-only baseline, could you tell how much friction comes from the motor vs the gearbox?

**(b)** With the baseline (motor alone = 0.12 Nm at motor side at that speed), calculate the gearbox-only friction contribution at the output.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

# POST-LAB — Complete After T-011 and T-006 Data

> [COMPLETE AFTER TEST DATA] Fill in these sections after you have real friction measurements.

## Part 3: Design Judgment

### D1: Interpreting your friction overlay

Compare your motor-only friction curve (T-011) to your motor+gearbox curve (T-006).

**(a)** At what speeds does gearbox friction dominate?

**(b)** Is the gearbox friction mostly Coulomb (constant offset) or viscous (increasing slope)? What does this tell you about the friction sources?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: Higher-than-expected gearbox friction

Your gearbox friction is higher than expected. List **3 possible mechanical causes** and for each, describe **how you'd investigate** (what to look for, what to try).

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Backdrivability explained with your data

Using your actual measured friction numbers, explain to someone who asks: "Why can't you just use a normal gearbox for a robot arm?" Ground your answer in the physics and your real measurements.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
