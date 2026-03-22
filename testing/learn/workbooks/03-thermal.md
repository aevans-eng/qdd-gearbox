# Thermal — Workbook 03

> **Format:** Applied + design judgment
> **Reference material:** `testing/learn/motor-physics-primer.md` (section 4), `calc/thermal.py`
> **Estimated time:** 45-60 min
> **Hardware:** D6374-150KV, $R_{phase} \approx 0.170\;\Omega$, PLA+ housing ($T_g \approx 60°C$), $N = 5$, $\eta = 0.9$

---

> **How to use this workbook**
> 1. Read the question, then write your answer in the response area (the blank space under each question)
> 2. Check one confidence box — be honest, this tells Claude where to probe during live review
> 3. When done, bring this file to a Claude session for grading: "Grade my workbook 03"
> 4. Claude grades your written answers first, then does a live review with follow-up questions

## Part 1: Concept Check

### Q1: Name the three main heat sources in a BLDC motor. For each, state whether it depends primarily on current, speed, or both.

*Your response:*

Friction, bearings, resistance, current passign through coils, not sure what else. I guess friction depends on speed? or does it? ya i guess maybe linearly? idk, current passign through coils i guess only dependent on current? but V=IR so maybe its depednent on both??

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q2: Copper loss scales with $I^2$, not $I$. Why the squaring? What real-world consequence does this have for high-torque operation?

*Your response:*
I have zero idea or intuitiion


*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q3: True or false: "A stalled motor at 5 A generates more total heat than a spinning motor at 5 A." Explain your reasoning.

*Your response:*

Im not sure to be honest. maybe because its not creating work with the electric power? so it has to be disspitated as heat?

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q4: What is thermal resistance ($R_{th}$)? What determines it physically in your 3D-printed PLA+ housing compared to an aluminum one?

*Your response:*

Whats Rth?

*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [x] Low — not sure, need to study more

---

### Q5: Why does PLA matter thermally for your gearbox? At what temperature should you worry, and what happens physically when you exceed it?

*Your response:*

PLA will start to creep, or plastically deform (ig they are the same), or just melt. which can fuse gears, increase wear, change geometries?

*Confidence:*
- [ ] High — could explain this cold in an interview
- [x] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 2: Applied Problems

### P1: Copper loss scaling

$R_{phase} = 0.170\;\Omega$.

**(a)** Calculate copper loss ($P_{cu} = I_q^2 \cdot R$) at $I_q$ = 5 A, 10 A, and 15 A.

**(b)** How does the 15 A loss compare to the 5 A loss? (Express as a ratio.)

**(c)** Your motor's approximate max electrical input is ~350 W. At 15 A, what fraction of that input is pure copper loss?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P2: Continuous torque from thermal limits

Assume $R_{th}$ (winding to ambient) = 3.5 K/W, ambient $T_{amb}$ = 25°C, winding limit $T_{max}$ = 120°C.

**(a)** What maximum continuous power loss can the motor sustain? (Steady-state: $T_{max} = T_{amb} + P_{loss} \cdot R_{th}$)

**(b)** Assuming copper loss dominates: what continuous $I_q$ does that correspond to?

**(c)** What continuous output torque is that through the 5:1 gearbox at $\eta = 0.9$?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### P3: PLA housing temperature limit

Your PLA+ housing has $T_g \approx 60°C$. Assume $R_{th}$ (winding to housing surface) = 1.2 K/W and ambient = 25°C.

**(a)** You want to keep the housing below 55°C (safety margin below $T_g$). What's the max allowable temperature rise at the housing?

**(b)** What copper loss produces that temperature rise at the housing? (Use $\Delta T_{housing} = P_{cu} \cdot R_{th,winding \to housing}$ — this is a simplification assuming most heat flows outward.)

**(c)** What $I_q$ is that? What continuous output torque?

**(d)** Compare this to the motor datasheet's rated continuous current. Why is your housing the bottleneck?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 3: Design Judgment

### D1: Increasing continuous torque under thermal constraints

Your PLA housing is already hitting 50°C during sustained 8 Nm output. You need 12 Nm continuous.

List **3 approaches** to increase continuous torque without exceeding thermal limits. For each, describe: what it does physically, how much it might help, and why you'd try it (or not) first.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

### D2: The datasheet vs reality mismatch

Your motor datasheet rates continuous current at 8 A. Your thermal model (with PLA housing) says you're limited to ~5 A continuous.

Is the datasheet wrong? Explain the discrepancy. What assumptions does the datasheet make that don't hold for your setup?

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more

---

## Part 4: Teach It

### T1: Why continuous torque exists

Your audience: a fellow student who asks "Why can't you just run the motor at peak torque forever? It can clearly produce that torque."

Explain the thermal reason, using the I² relationship and steady-state temperature as the core concepts. Keep it under 5 sentences.

*Your response:*



*Confidence:*
- [ ] High — could explain this cold in an interview
- [ ] Medium — get the idea, might fumble details
- [ ] Low — not sure, need to study more
