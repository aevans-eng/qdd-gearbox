# Dynamics & System ID — Workbook 08

> **Format:** Applied problems heavy
> **Reference material:** `testing/learn/campaign-walkthrough.md` (Phase 3), `testing/campaign/test-campaign-rev00b.md` (T-015, T-016)
> **Estimated time:** 45-60 min
> **Hardware:** D6374-150KV, $K_t = 0.0551$ Nm/A, $N = 5$, ODrive v3.6 (torque mode, BulkCapture at ~500 Hz)

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 08"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: What is a transfer function $G(s)$? What does the variable $s$ represent physically? (Don't just say "Laplace variable" — explain what it means for interpreting the equation.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: Your plant model is $G(s) = \frac{1}{Js^2 + bs}$. What does each term represent physically? Why is there no constant term in the denominator?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: Name the four step response metrics: rise time, overshoot, settling time, steady-state error. For each, explain what physical property of the system it reveals.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: What is a Bode plot? Describe both graphs (magnitude and phase) and what each tells you about the system's behavior. What is the significance of the -3 dB point?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: Why is bandwidth THE metric for actuator performance in robotics? What does a higher bandwidth actuator let you do that a lower bandwidth one can't?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Estimating inertia from a step response

You put ODrive in torque control mode and apply a step torque of $\tau = 0.5$ Nm. You log motor velocity over time.

The velocity ramps roughly linearly from 0 to 12 rad/s in 0.3 seconds.

**(a)** Estimate the angular acceleration $\alpha$.

**(b)** Calculate $J$ from Newton's rotational law: $\tau = J \cdot \alpha$ (ignoring friction for the initial ramp).

**(c)** If $b = 0.005$ Nm·s/rad (from T-011), write the complete transfer function $G(s) = \frac{1}{Js^2 + bs}$ with your numbers.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Gearbox reflected inertia from real data

With the gearbox attached, the same 0.5 Nm step torque (at motor side) gives velocity ramping from 0 to 2.8 rad/s in 0.3 seconds (measured at motor side).

**(a)** Estimate $J_{total}$ (total inertia seen at motor side).

**(b)** What reflected inertia did the gearbox add? ($J_{gearbox,reflected} = J_{total} - J_{motor}$)

**(c)** If your motor-only $J_{motor}$ from P1 is ~0.0125 kg·m², calculate the expected $N^2 \cdot J_{motor}$. Does your measured reflected inertia match? If not, what does the gearbox contribute beyond reflected motor inertia?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P3: Bandwidth calculation

The -3 dB bandwidth for a system $G(s) = \frac{1}{Js^2 + bs}$ in a velocity control loop can be approximated.

**(a)** For your motor-only $J$ and $b$, calculate the open-loop crossover frequency $\omega_c \approx b/J$ (simplified). Convert to Hz.

**(b)** For your motor+gearbox $J_{total}$ and assuming $b$ increases by 50% with the gearbox, recalculate.

**(c)** How much bandwidth did the gearbox cost, in percentage?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P4: Mystery resonance in the Bode plot

You run a Bode plot (T-016) and see a resonance peak at 15 Hz that your rigid-body $G(s) = \frac{1}{Js^2 + bs}$ doesn't predict. The predicted response is smooth rolloff, but the real data shows a bump at 15 Hz then steeper rolloff.

**(a)** Name 2 possible physical sources of this resonance in a PLA planetary gearbox.

**(b)** How would you modify $G(s)$ to include this resonance? (Describe the structure — you don't need exact numbers.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Model vs reality mismatch

Your measured Bode plot doesn't match the predicted $G(s)$ above 10 Hz. The prediction says -40 dB/dec rolloff, but the real data shows a bump and then steeper rolloff.

**(a)** Is your model "wrong"? Or is it "valid within a range"?

**(b)** What is the model missing? List 2-3 physical effects.

**(c)** How would you report this in a portfolio — as a failure or as insight? What's the professional way to frame model limitations?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: System ID — from textbook to real life

Your audience: a MECH 380 student who's used to being given $G(s)$ in problem sets.

Explain: "In class they hand you the transfer function. In the real world, how do you find it from a physical system?" Use your actuator as the example. Walk through the process from raw data to validated model.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
