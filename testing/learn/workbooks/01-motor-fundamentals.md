# Motor Fundamentals — Workbook 01

> **Format:** Interview Q&A heavy
> **Reference material:** `testing/learn/motor-physics-primer.md`, `testing/learn/campaign-walkthrough.md`
> **Estimated time:** 45-60 min
> **Hardware:** D6374-150KV, $K_t = 0.0551$ Nm/A, $K_v = 150$ RPM/V, 7 pole pairs, ODrive v3.6 (8 kHz FOC)

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 01"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: What is Field-Oriented Control (FOC)? Why does ODrive use it instead of simpler commutation methods?

*Your response:*
I think its just a more complex way to control the motor, better control over its behavior? or maybe better feedback aswell? idk


*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q2: What is the physical difference between $I_q$ and $I_d$? Why is $I_d$ set to zero in normal operation?

*Your response:*
Not sure exactly what it is, but i think Iq is quadrature current, the current that produces current in the motor somehow? like i guess it goes in the coils and creates a magnetic field in the right direction. but Id creates radial forces somehow? not sure how though.


*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: The relationship $\tau = K_t \cdot I_q$ is linear. What physical law makes it so? Where does the linearity come from at the fundamental level?

*Your response:*

I have no idea.

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q4: $K_t$ and $K_e$ are numerically equal in SI units. Why? What conservation law connects them?

*Your response:*

Not sure what Ke is, i think Kt is like torque constant? which i guess is like amplitude? idk

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q5: What does $K_v = 150$ RPM/V mean physically? How does it relate to $K_t$? Where does the 8.27 constant come from in $K_t = 8.27/K_v$?

*Your response:*
I guess Kv is like a performance metric? like a higher kv means a higher rpm  for a given volt, but if current generates torque, Actually i udnno i have no idea


*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q6: If you told ODrive your motor has 8 pole pairs but it actually has 7, what goes wrong? Walk through the mechanism — why does the wrong pole pair count corrupt $I_q$ readings?

*Your response:*
Im not really sure what this means or what pole pairs means. i have no idea, i guess because resistance is maybe different? 


*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q7: What is the difference between total phase current and $I_q$? Under what conditions would they differ?

*Your response:*

I have no idea what total phase current is.

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q8: When is $\tau = K_t \cdot I_q$ NOT perfectly linear? Name 2-3 effects and whether they matter for your test campaign.

*Your response:*

Im not familiar with that formula, im not really sure. but I guess back emf? at high rpms? thats the biggest one, or maybe low rpms, where theres cogging? which i guess is when the force of friction is hgih compared to the rpms or soemthing? 

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Current to torque — and what happens when $K_v$ is wrong

Your motor reads $I_q = 3.2$ A at steady state under load.

**(a)** What torque is the motor producing at the motor shaft?

**(b)** What torque is that at the gearbox output? (assume $N = 5$, $\eta = 0.9$)

**(c)** If your motor's actual $K_v$ is 140 instead of 150, what is the real $K_t$? By what percentage are your torque calculations off?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: No-load current interpretation

At no-load, the motor reads $I_q = 0.4$ A at 5 rev/s (motor shaft).

**(a)** What friction torque does this correspond to?

**(b)** Is 0.4 A at no-load reasonable for a D6374? What if it read 2.5 A — what would that tell you?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Diagnosing a bad T-009 result

You're setting up ODrive for the first time. T-009 shows $I_q = 2.5$ A at no-load, low speed. This is way too high.

List **3 possible causes** ranked by likelihood. For each, describe **how you'd diagnose it** (what you'd check, what you'd expect to see).

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Explain $I_q$ as a built-in torque sensor

Your audience: a mechanical engineering student who knows statics and dynamics but has never touched a BLDC motor or motor controller.

Explain what $I_q$ is, why it's proportional to torque, and why you can use it as a built-in torque sensor for your entire test campaign. Use plain language — they don't know FOC, back-EMF, or motor control vocabulary.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
