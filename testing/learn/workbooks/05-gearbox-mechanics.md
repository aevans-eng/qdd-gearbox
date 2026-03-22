# Gearbox Mechanics — Workbook 05

> **Format:** Applied problems heavy
> **Reference material:** `calc/gear_geometry.py`, `calc/tooth_stress.py`, `docs/original-documentation-jan4/trade-studies.md`
> **Estimated time:** 45-60 min
> **Hardware:** 5:1 planetary, PLA+ FDM, 20° pressure angle, D6374-150KV ($\tau_{motor,peak} = 0.88$ Nm)

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 05"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: In your planetary gear set, which element is fixed, which is the input, and which is the output? Describe the power flow path.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q2: Derive the gear ratio for a simple planetary: $N = 1 + Z_{ring}/Z_{sun}$. Why is it NOT just $Z_{ring}/Z_{sun}$? What does the "+1" account for?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q3: What is reflected inertia? Why does it scale with $N^2$ instead of $N$? (Use the energy argument.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q4: What is contact ratio? Why does a higher contact ratio mean smoother, quieter operation? What happens if contact ratio drops below 1?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### Q5: What is pressure angle (20° for your gears)? How does it affect the tradeoff between tooth strength and radial (separating) force?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Planetary tooth counts and assembly condition

Your planetary has a gear ratio of $N = 5$.

**(a)** Using $N = 1 + Z_{ring}/Z_{sun}$, if $Z_{sun} = 16$, what is $Z_{ring}$?

**(b)** What is $Z_{planet}$? (Hint: $Z_{ring} = Z_{sun} + 2 \cdot Z_{planet}$)

**(c)** How many equally-spaced planets can you fit? (Assembly condition: $(Z_{sun} + Z_{ring})$ must be divisible by the number of planets.)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Reflected inertia calculation

Your motor rotor inertia is $J_{motor} = 0.003$ kg·m².

**(a)** If you attach a load with $J_{load} = 0.001$ kg·m² at the output, what reflected inertia does the motor see? ($J_{reflected} = N^2 \cdot J_{load}$)

**(b)** What is the total inertia the motor must accelerate? ($J_{total} = J_{motor} + J_{reflected}$)

**(c)** At what $J_{load}$ does the reflected inertia equal the motor's own inertia? Is that a large or small load?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P3: Tooth stress check

Your motor peak torque is 0.88 Nm. Through $N = 5$, $\eta = 0.9$: output torque = ?

**(a)** Calculate the peak output torque.

**(b)** At the ring gear pitch circle (assume pitch diameter $d_{ring}$), calculate the tangential tooth force: $F_t = \tau_{out} / (d_{ring}/2)$.

**(c)** Using the Lewis bending stress equation $\sigma_b = F_t / (m \cdot b_{face} \cdot Y)$, estimate the tooth bending stress. (Use reasonable values for your gear module $m$, face width $b_{face}$, and Lewis form factor $Y \approx 0.3$.) Is this within PLA+ limits (~40-50 MPa)?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P4: Output torque with losses

**(a)** Your motor produces 0.88 Nm peak. Through $N = 5$ at $\eta = 0.90$, what's the output torque?

**(b)** If gearbox efficiency drops to $\eta = 0.78$ (worn gears, poor lubrication), what's the output torque now?

**(c)** That lost torque became heat/friction. How much power is being lost to friction at 100 RPM output? ($P_{loss} = \tau_{loss} \cdot \omega$)

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Choosing a gear ratio for a QDD

You're designing a QDD joint for a robotic arm. Two options: 4:1 or 6:1.

For each ratio, analyze: **(a)** output torque, **(b)** output speed, **(c)** reflected inertia ($N^2$), **(d)** backdrivability (how does ratio affect friction at output?), **(e)** bandwidth impact.

Which would you choose and why? Consider the tradeoffs explicitly.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Reflected inertia explained

Your audience: someone who understands gear ratios (torque up, speed down) but doesn't know why inertia behaves differently (scales with $N^2$, not $N$).

Explain reflected inertia using the energy conservation argument. Why is $N^2$ the right scaling? What does it physically mean for the motor?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
