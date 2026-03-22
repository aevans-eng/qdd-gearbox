# Measurement & Instrumentation — Workbook 06

> **Format:** Design judgment heavy
> **Reference material:** `testing/learn/campaign-walkthrough.md`, `research/gemini-deep-research/01-actuator-testing-methodology/response.md`
> **Estimated time:** 30-45 min
> **Hardware:** ODrive v3.6 (8 kHz FOC, ~200 Hz Python polling), AS5047P encoder (14-bit, 16384 CPR), kitchen scale (1 g resolution)

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 06"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: Why can $I_q$ be used as a torque sensor? What assumptions does this rely on? (Name at least 2.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: What could make $I_q$ an inaccurate torque estimate? List 3 sources of error.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: ODrive's FOC loop runs at 8 kHz, but your Python polling runs at ~200 Hz. Why does this mismatch matter for your measurements? When does it matter most?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: What's the difference between accuracy and repeatability? If you're comparing motor-only vs motor+gearbox friction, which matters more and why?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: Your encoder has 16384 counts per revolution (14-bit).

**(a)** What angular resolution is that in degrees?

**(b)** Through the 5:1 gearbox, what effective output resolution do you get?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Statistical confidence in a measurement

You measure $I_q$ for 5 seconds at 200 Hz. That's 1000 samples. The mean is 0.42 A with standard deviation 0.08 A.

**(a)** What is the standard error of the mean? ($SE = \sigma / \sqrt{n}$)

**(b)** What is the 95% confidence interval on the mean? ($\bar{x} \pm 1.96 \cdot SE$)

**(c)** Convert that confidence interval to a torque range using $K_t = 0.0551$ Nm/A. How precise is your torque measurement?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Kitchen scale torque resolution

Your kitchen scale reads in 1 g increments. You use a lever arm of 200 mm.

**(a)** What is the minimum resolvable torque? ($\tau_{min} = 0.001 \text{ kg} \times 9.81 \times 0.200\text{ m}$)

**(b)** Your backdrivability requirement is < 1 Nm. How many scale increments is that? Is the resolution sufficient?

**(c)** If you wanted to resolve 0.05 Nm differences, what lever arm length would you need?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Defending your measurement approach

A colleague says: "You should use a torque transducer instead of relying on $I_q$. Current-based torque estimation isn't real measurement."

**(a)** Argue **for** why $I_q$ is adequate for your campaign. What makes it defensible?

**(b)** Identify the **one test** in your campaign where an external torque measurement (load cell, transducer) would add the most value. Why that test specifically?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: Diagnosing noisy measurements

You notice $I_q$ measurements are noisier at higher motor speeds.

**(a)** List 2 possible **physical** causes (things happening in the motor/gearbox).

**(b)** List 2 possible **measurement** causes (things happening in the sensing/data chain).

**(c)** How would you distinguish between physical and measurement noise? Describe one diagnostic test.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Trusting current as torque data

Your audience: a lab partner who's skeptical about using current readings as torque measurements.

Explain why you trust $I_q$ as torque data for this campaign. What conditions would make you **stop** trusting it?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
