# Impedance Control — Workbook 09

> **Format:** Interview Q&A + applied
> **Reference material:** `testing/learn/campaign-walkthrough.md` (Phase 4), `testing/campaign/test-campaign-rev00b.md` (T-017, T-018), `research/gemini-deep-research/01-actuator-testing-methodology/response.md` (impedance section)
> **Estimated time:** 45-60 min
> **Hardware:** D6374-150KV, $K_t = 0.0551$ Nm/A, $N = 5$, ODrive v3.6 (~200 Hz Python loop, 8 kHz internal)

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 09"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: What is impedance control? How does it differ from position control? Describe the fundamental difference in what the controller is trying to achieve.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: Write the impedance control law: $\tau = -K(\theta - \theta_0) - B\dot{\theta}$. What does each variable represent physically? What happens when you increase $K$? When you increase $B$?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: Why can a QDD (5:1 ratio) do impedance control but a 50:1 gearbox can't? Explain in terms of transparency, friction, and reflected inertia.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: Your project uses two implementation approaches — Tier A (ODrive's internal PID used as a spring) and Tier B (Python computing the torque command). What is each doing? What are the tradeoffs?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: Why does USB jitter matter for impedance control? At what stiffness values does jitter become a stability problem? Why?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q6: Why does Tesla care about impedance control for Optimus? Give a specific task or scenario where a robot NEEDS compliant joints rather than stiff position control.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q7: Cornelius (UVic grad → Tesla Optimus) suggested extending your QDD into a robotic arm or robot dog with impedance control. Why does impedance control matter specifically for a limb joint? What goes wrong without it?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Choosing K and B

You want full-scale torque (16 Nm) at ±5.7° deflection (±0.1 rad).

**(a)** What virtual stiffness $K$ is needed? ($K = \tau_{max} / \theta_{max}$)

**(b)** If $J_{reflected} \approx 0.075$ kg·m² (motor + gearbox reflected), what $B$ gives critical damping? ($B_{crit} = 2\sqrt{K \cdot J}$)

**(c)** Why would you start with $B$ higher than critical damping (overdamped)? What happens if you start underdamped?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Control loop timing

Your Python impedance loop runs at 200 Hz.

**(a)** What is the loop period in milliseconds?

**(b)** If your actuator has a natural frequency of 8 Hz, how many control updates happen per oscillation cycle?

**(c)** A rule of thumb is you need at least 10× the natural frequency in control rate. Does 200 Hz satisfy this? What if you increase $K$ and the natural frequency rises to 20 Hz?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P3: Force-displacement under impedance control

You set $K = 50$ Nm/rad, $B = 2$ Nm·s/rad, equilibrium at $\theta_0 = 0$.

**(a)** Someone slowly displaces the output by 0.1 rad and holds it (static: $\dot{\theta} = 0$). What torque does the actuator command?

**(b)** If they push with a constant 5 Nm, where does the equilibrium land? ($\theta_{eq}$ where spring force balances applied force)

**(c)** They suddenly let go. Describe qualitatively what happens — does the output oscillate, return smoothly, or something else? (Consider whether $B = 2$ makes this overdamped, underdamped, or critically damped for your $J$.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Diagnosing impedance controller chattering

Your impedance controller buzzes/chatters near the center position. The output makes an audible humming sound when it should be holding still at equilibrium.

**(a)** List 3 possible causes (at least one from mechanics, one from controls).

**(b)** For each, describe the diagnostic step — what would you check or try?

**(c)** What's the most likely cause given your PLA gearbox with known backlash?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Impedance control as a programmable spring

Your audience: a mech eng student who understands springs and dampers but has never heard of impedance control.

Explain it using only the spring analogy: "Imagine the actuator IS a spring. You get to choose how stiff." Why is this useful for a robot that needs to interact with people or unknown objects?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
