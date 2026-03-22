# QDD Learning System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create 13 workbook assignments + progress tracker covering motor physics through FEA literacy, grounded in Aaron's QDD hardware.

**Architecture:** Each workbook is a standalone markdown file with 4 sections (Concept Check, Applied Problems, Design Judgment, Teach It). Questions use Aaron's actual motor/gearbox parameters. Answer blocks use the `> **Your answer:**` format with confidence tags.

**Tech Stack:** Markdown files, MathJax notation ($...$, $$...$$), grounded in QDD reference docs.

**Spec:** `docs/specs/2026-03-20-qdd-learning-system-design.md`

---

## File Structure

All files created in `qdd-gearbox/testing/learn/workbooks/`:

```
workbooks/
├── _progress.md                      # Status tracker (Task 1)
├── 01-motor-fundamentals.md          # Task 2
├── 02-torque-speed-envelope.md       # Task 3
├── 03-thermal.md                     # Task 4
├── 04-friction-backdrivability.md    # Task 5
├── 05-gearbox-mechanics.md           # Task 6
├── 06-measurement-instrumentation.md # Task 7
├── 07-testing-methodology.md         # Task 8
├── 08-dynamics-system-id.md          # Task 9
├── 09-impedance-control.md           # Task 10
├── 10-backlash-compliance.md         # Task 11
├── 11-gdt-tolerancing.md             # Task 12
├── 12-dfm-manufacturing.md           # Task 13
└── 13-fea-literacy.md                # Task 14
```

## Workbook Template

Every workbook follows this exact structure:

```markdown
# [Topic Name] — Workbook [NN]

> **Format:** [Interview Q&A heavy | Applied problems heavy | etc.]
> **Reference material:** [file paths]
> **Estimated time:** [30-60 min]

---

## Part 1: Concept Check

[5-8 interview-style questions with answer blocks]

## Part 2: Applied Problems

[2-4 problems using real QDD numbers: D6374-150KV, Kt=0.0551, N=5, ODrive v3.6]

## Part 3: Design Judgment

[1-2 open-ended scenarios]

## Part 4: Teach It

[1 prompt — explain topic to a non-expert]
```

Answer block format:
```markdown
### Q1: [Question]

> **Your answer:**
>
>
> **Confidence:** high / medium / low
```

## Hardware Constants (use across all workbooks)

- Motor: D6374-150KV, Kt = 0.0551 Nm/A, Ke = 0.0551 V·s/rad
- Kv = 150 RPM/V, 7 pole pairs (14 magnets)
- Gearbox: 5:1 planetary, PLA+ FDM, 20° pressure angle
- Controller: ODrive v3.6, 8 kHz FOC, 14-bit encoder (16384 CPR)
- Target: backlash ≤ 0.5°, friction < 1 Nm, peak torque ≥ 16 Nm
- Bus voltage: ~24V typical

---

### Task 1: Create folder and progress tracker

**Files:**
- Create: `testing/learn/workbooks/_progress.md`

- [ ] **Step 1: Create workbooks directory**

```bash
mkdir -p /c/Users/aaron/Documents/c-projects/qdd-gearbox/testing/learn/workbooks
```

- [ ] **Step 2: Write progress tracker**

Create `_progress.md` with the schema from the spec:

```markdown
# QDD Learning System — Progress Tracker

> Start at topic 1, work sequentially. Bring completed workbooks to Claude for grading + live review.
> **Status flow:** Not started → In progress → Grading → Live review → Complete

| # | Topic | Status | Written Grade | Live Review | Date Completed | Notes |
|---|-------|--------|--------------|-------------|----------------|-------|
| 1 | Motor fundamentals | Not started | — | — | — | — |
| 2 | Torque-speed envelope | Not started | — | — | — | — |
| 3 | Thermal | Not started | — | — | — | — |
| 4 | Friction & backdrivability | Not started | — | — | — | — |
| 5 | Gearbox mechanics | Not started | — | — | — | — |
| 6 | Measurement & instrumentation | Not started | — | — | — | — |
| 7 | Testing methodology | Not started | — | — | — | — |
| 8 | Dynamics & system ID | Not started | — | — | — | — |
| 9 | Impedance control | Not started | — | — | — | — |
| 10 | Backlash & compliance | Not started | — | — | — | — |
| 11 | GD&T & tolerancing | Not started | — | — | — | — |
| 12 | DFM & manufacturing | Not started | — | — | — | — |
| 13 | FEA literacy | Not started | — | — | — | — |
```

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/_progress.md
git commit -m "feat(learning): add workbook progress tracker for QDD learning system"
```

---

### Task 2: Workbook 01 — Motor Fundamentals

**Files:**
- Create: `testing/learn/workbooks/01-motor-fundamentals.md`
- Reference: `testing/learn/motor-physics-primer.md`, `testing/learn/campaign-walkthrough.md`

**Format:** Interview Q&A heavy (7-8 Concept Check, 2 Applied)

- [ ] **Step 1: Write workbook**

**Concept Check questions (8) — things Tesla will ask cold:**
1. Explain FOC — what is it, why does ODrive use it (not just "it controls the motor")
2. What's the physical difference between Iq and Id? Why is Id set to zero?
3. Why is τ = Kt × Iq linear? What physical law makes it so? (Lorentz force)
4. Kt and Ke are numerically equal — why? What conservation law connects them?
5. What does Kv = 150 mean physically? How does it relate to Kt?
6. Where does the 8.27 constant come from in Kt = 8.27/Kv?
7. If you told ODrive your motor has 8 pole pairs but it actually has 7, what goes wrong and why?
8. What's the difference between total phase current and Iq? When would they differ?

**Applied Problems (2):**
1. Your motor reads Iq = 3.2A at steady state under load. What torque is the motor producing? What if your Kv is actually 140 instead of 150 — how does that change the answer?
2. At no-load, the motor reads Iq = 0.4A at 5 rev/s. What's the friction torque? Is this reasonable for a D6374?

**Design Judgment (1):**
1. You're setting up ODrive for the first time and T-009 shows Iq = 2.5A at no-load, low speed. List 3 possible causes ranked by likelihood, and how you'd diagnose each.

**Teach It (1):**
- Explain to a mech eng student who knows statics/dynamics but has never touched a BLDC motor: what is Iq and why can you use it as a built-in torque sensor?

- [ ] **Step 2: Verify question count matches spec** (8 CC, 2 AP, 1 DJ, 1 TI = 12 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/01-motor-fundamentals.md
git commit -m "feat(learning): add workbook 01 — motor fundamentals"
```

---

### Task 3: Workbook 02 — Torque-Speed Envelope

**Files:**
- Create: `testing/learn/workbooks/02-torque-speed-envelope.md`
- Reference: `testing/learn/motor-physics-primer.md` (sections 2-3)

**Format:** Applied problems heavy (5 Concept Check, 4 Applied)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. What is back-EMF physically? Why does a spinning motor generate voltage?
2. Why does torque capacity decrease with speed? (voltage headroom)
3. What limits the motor's maximum no-load speed? (Vbus = Vbemf)
4. Explain continuous vs peak torque — what physical constraint separates them?
5. What happens electrically when you try to command full torque at max speed?

**Applied Problems (4):**
1. Calculate Vbemf at 2000 RPM motor speed. How much voltage headroom remains on a 24V bus?
2. At what motor speed does Vbemf = 24V? What's the output speed through the 5:1 gearbox? Can you produce any torque at this speed?
3. Calculate the stall torque (ω=0) with a 10A current limit. Then calculate the no-load speed. Sketch the speed-torque line between them.
4. Your actuator needs to produce 12 Nm continuous at the output at 200 RPM output. What motor-side Iq is needed? (account for N=5, assume η=0.9). Is this within the speed-torque envelope?

**Design Judgment (1):**
1. You want to increase your actuator's max output speed. You could: (a) increase bus voltage, (b) use a lower Kv motor, (c) change the gear ratio. Analyze the trade-offs of each.

**Teach It (1):**
- Explain the motor speed-torque curve to someone who understands DC circuits but not motors. Why is it a straight line? What sets the two endpoints?

- [ ] **Step 2: Verify** (5 CC, 4 AP, 1 DJ, 1 TI = 11 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/02-torque-speed-envelope.md
git commit -m "feat(learning): add workbook 02 — torque-speed envelope"
```

---

### Task 4: Workbook 03 — Thermal

**Files:**
- Create: `testing/learn/workbooks/03-thermal.md`
- Reference: `testing/learn/motor-physics-primer.md` (section 4), `calc/thermal.py`

**Format:** Applied + design judgment (5 Concept Check, 3 Applied, 2 Design Judgment)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. Name the three main heat sources in a BLDC motor. Which depends on current? Which on speed?
2. Why does copper loss scale with I² (not I)? What real-world consequence does the squaring have?
3. A stalled motor at 5A generates more heat than a spinning motor at 5A. True or false? Explain.
4. What is thermal resistance (Rth)? What determines it physically in your 3D-printed housing?
5. Why does PLA matter thermally? What temperature should worry you and why? (Tg ≈ 60°C)

**Applied Problems (3):**
1. Motor Rphase = 0.170 Ω. Calculate copper loss at Iq = 5A, 10A, and 15A. How does this compare to your motor's ~350W max input?
2. Steady-state thermal: if Rth (winding to ambient) = 3.5 K/W and ambient = 25°C, what Iq gives Twinding = 120°C? What continuous output torque does that correspond to (through 5:1 gearbox, η=0.9)?
3. Your PLA housing has Tg ≈ 60°C. If Rth (winding to housing) = 1.2 K/W, at what copper loss does the housing reach 55°C? (ambient 25°C). What Iq is that?

**Design Judgment (2):**
1. You need more continuous torque but your housing is already hitting 50°C. List 3 approaches to increase continuous torque without exceeding thermal limits. Which would you try first and why?
2. Your motor datasheet rates continuous current at 8A. Your thermal model predicts your PLA housing limits you to 5A continuous. Is the datasheet wrong? Explain the discrepancy.

**Teach It (1):**
- Explain to a fellow student why "continuous torque" exists — why can't you just run the motor at peak torque forever?

- [ ] **Step 2: Verify** (5 CC, 3 AP, 2 DJ, 1 TI = 11 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/03-thermal.md
git commit -m "feat(learning): add workbook 03 — thermal"
```

---

### Task 5: Workbook 04 — Friction & Backdrivability (Pre/Post-Lab)

**Files:**
- Create: `testing/learn/workbooks/04-friction-backdrivability.md`
- Reference: `testing/learn/campaign-walkthrough.md` (friction section), `testing/campaign/test-campaign-rev00b.md` (T-011, T-006)

**Format:** Pre/post-lab (pre-lab Concept Check + Applied before testing, post-lab Design Judgment + Teach It after data)

- [ ] **Step 1: Write workbook**

Structure as two parts: PRE-LAB (complete before running T-011) and POST-LAB (complete after getting T-011 + T-006 data).

**PRE-LAB — Concept Check (6):**
1. What is Coulomb friction physically? What causes it in a motor? In a gearbox?
2. What is viscous friction physically? What causes it?
3. Write the combined friction model equation. What's the y-intercept? What's the slope?
4. Why do you need to measure friction at multiple speeds? (Can't separate τc and b from one point)
5. What does "backdrivability" mean for a QDD? Why is low friction the enabler?
6. How does the gearbox affect friction at the output vs the motor side? (scaling by N)

**PRE-LAB — Applied Problems (3):**
1. You measure Iq = 0.3A at 2 rev/s and Iq = 0.5A at 10 rev/s (no-load). Compute τf at each speed, then solve for τc and b.
2. Your requirement is output friction < 1 Nm. If motor-only friction is 0.022 Nm (at motor side), how much friction budget does the gearbox get at the output?
3. CubeMars AK70-10 (commercial QDD) has output friction ~0.97 Nm. Your requirement is < 1 Nm. How does your gearbox compare as a design target?

**POST-LAB — Design Judgment (2):**
(Placeholder — to be completed after T-011 and T-006 data)
1. Compare your motor-only friction curve to motor+gearbox curve. Where does the gearbox friction dominate? Is it mostly Coulomb or viscous?
2. Your gearbox friction is higher than expected. List 3 possible mechanical causes and how you'd investigate each.

**POST-LAB — Teach It (1):**
- Using your actual data, explain backdrivability to someone who asks "why can't you just use a normal gearbox?" Use your measured numbers.

- [ ] **Step 2: Verify** (6 CC, 3 AP pre-lab; 2 DJ, 1 TI post-lab = 12 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/04-friction-backdrivability.md
git commit -m "feat(learning): add workbook 04 — friction & backdrivability (pre/post-lab)"
```

---

### Task 6: Workbook 05 — Gearbox Mechanics

**Files:**
- Create: `testing/learn/workbooks/05-gearbox-mechanics.md`
- Reference: `calc/gear_geometry.py`, `calc/tooth_stress.py`, `docs/original-documentation-jan4/trade-studies.md`

**Format:** Applied problems heavy (5 Concept Check, 4 Applied)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. In a planetary gear set, which gear is fixed, which is input, which is output? How does power flow?
2. Derive the gear ratio for your planetary: N = 1 + Zring/Zsun. Why is it not just Zring/Zsun?
3. What is reflected inertia and why does it scale with N² (not N)?
4. What is contact ratio? Why does higher contact ratio mean smoother operation?
5. What is pressure angle (20° for your gears)? How does it affect tooth strength vs friction?

**Applied Problems (4):**
1. Your sun gear has Z_sun teeth, ring has Z_ring teeth. Calculate the number of planets possible and the planet tooth count. Verify the assembly condition.
2. Calculate the reflected inertia: if Jmotor = 0.003 kg·m², what load inertia at the output would make the total reflected inertia equal to 2× the motor inertia? Is this a lot or a little?
3. Lewis bending stress: given your gear module m, face width b, and a tangential tooth force from 16 Nm output torque, is the tooth stress within PLA+ allowable limits?
4. Your motor produces 0.88 Nm peak. Through 5:1 at 90% efficiency, what's the output torque? What tangential force does this produce at the pitch circle of the ring gear?

**Design Judgment (1):**
1. You're choosing between 4:1 and 6:1 gear ratio for a QDD. How does each choice affect: torque output, speed, reflected inertia, backdrivability, and bandwidth? Which would you pick for a robotic arm joint and why?

**Teach It (1):**
- Explain reflected inertia (N² scaling) to someone who understands gear ratios but doesn't know why inertia is different from torque. Use the energy argument.

- [ ] **Step 2: Verify** (5 CC, 4 AP, 1 DJ, 1 TI = 11 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/05-gearbox-mechanics.md
git commit -m "feat(learning): add workbook 05 — gearbox mechanics"
```

---

### Task 7: Workbook 06 — Measurement & Instrumentation

**Files:**
- Create: `testing/learn/workbooks/06-measurement-instrumentation.md`
- Reference: `testing/learn/campaign-walkthrough.md`, `research/gemini-deep-research/01-actuator-testing-methodology/response.md`

**Format:** Design judgment heavy (5 Concept Check, 2 Applied, 2 Design Judgment)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. Why can Iq be used as a torque sensor? What assumptions does this rely on?
2. What could make Iq an inaccurate torque estimate? List 3 sources of error.
3. ODrive polls at ~200 Hz via Python, but the FOC loop runs at 8 kHz. Why does this matter for your measurements?
4. What's the difference between accuracy and repeatability? Which matters more for comparing motor-only vs motor+gearbox?
5. Your encoder has 16384 CPR. What angular resolution is that in degrees? Through 5:1 gearbox, what output resolution?

**Applied Problems (2):**
1. You measure Iq for 5 seconds at 200 Hz. That's 1000 samples. The mean is 0.42A with std dev 0.08A. What's the 95% confidence interval on the mean? What torque range does that correspond to?
2. Your kitchen scale reads in 1g increments. At a 200mm lever arm, what's your torque resolution? Is this sufficient to resolve your 1 Nm backdrivability requirement?

**Design Judgment (2):**
1. A colleague says "just use a torque transducer instead of relying on Iq." You don't have one. Argue for why Iq is adequate for your campaign, AND identify the one test where an external torque measurement would add the most value.
2. You notice Iq measurements are noisier at higher speeds. List 2 possible physical causes and 2 possible measurement causes. How would you distinguish between them?

**Teach It (1):**
- Explain to a lab partner why you trust current measurements as torque data. What would make you stop trusting them?

- [ ] **Step 2: Verify** (5 CC, 2 AP, 2 DJ, 1 TI = 10 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/06-measurement-instrumentation.md
git commit -m "feat(learning): add workbook 06 — measurement & instrumentation"
```

---

### Task 8: Workbook 07 — Testing Methodology

**Files:**
- Create: `testing/learn/workbooks/07-testing-methodology.md`
- Reference: `testing/methodology/testing-fundamentals.md`, `testing/qdd-rtm.xlsx`

**Format:** Design judgment + scenarios (5 Concept Check, 2 Applied, 2 Design Judgment)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. Name the four test levels in V-model order (bottom to top). Why must lower levels pass before upper levels?
2. What's the difference between a requirement, an unknown, and an acceptance criterion? Give one example of each from your QDD project.
3. Why do you define acceptance criteria BEFORE running the test?
4. What does "traceability" mean in a test campaign? Why does every test need to trace to a requirement or unknown?
5. Explain the risk × uncertainty priority matrix. Give an example of a high-risk, high-uncertainty item from your gearbox.

**Applied Problems (2):**
1. Your RTM has 13 requirements and 19 tests. Draw the dependency chain: which Phase 0 tests must pass before which Phase 2 tests can run? Identify any test that has no dependency (if any exist).
2. You have 2 hours of lab time. Prioritize these three tests using the risk × uncertainty framework: (a) backlash measurement, (b) thermal test at peak torque, (c) verify gear mesh quality by hand. Explain your ordering.

**Design Judgment (2):**
1. Your gearbox fails the backlash test at Phase 1 (measures 0.8° vs 0.5° requirement). Should you still proceed to Phase 2 powered testing? Argue both sides, then make a recommendation.
2. T-006 results show friction that's 3× higher than your model predicts. The result is "inconclusive" — list 3 possible explanations (test design issue, hardware issue, model issue) and how you'd triage them.

**Teach It (1):**
- Explain to a student who's never run a test campaign: why can't you just test everything at once? What's the value of phased testing?

- [ ] **Step 2: Verify** (5 CC, 2 AP, 2 DJ, 1 TI = 10 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/07-testing-methodology.md
git commit -m "feat(learning): add workbook 07 — testing methodology"
```

---

### Task 9: Workbook 08 — Dynamics & System ID

**Files:**
- Create: `testing/learn/workbooks/08-dynamics-system-id.md`
- Reference: `testing/learn/campaign-walkthrough.md` (Phase 3), `testing/campaign/test-campaign-rev00b.md` (T-015, T-016)

**Format:** Applied problems heavy (5 Concept Check, 4 Applied)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. What is a transfer function G(s)? What does s represent physically?
2. Your plant model is G(s) = 1/(Js² + bs). What does each term represent? Why is there no constant term in the denominator?
3. What are the step response metrics (rise time, overshoot, settling time)? What does each tell you about the system?
4. What is a Bode plot? What do the two graphs (magnitude and phase) tell you?
5. What is bandwidth (-3dB point) and why is it THE metric for actuator performance?

**Applied Problems (4):**
1. You apply a step torque of 0.5 Nm. Velocity ramps from 0 to 12 rad/s in 0.3 seconds (roughly linear). Estimate J. If b = 0.005 Nm·s/rad (from T-011), write G(s).
2. With the gearbox attached, the same test gives velocity ramping to 2.8 rad/s in 0.3 seconds (at motor side). Estimate Jtotal. What reflected inertia did the gearbox add? Compare to N² × Jmotor.
3. Your G(s) predicts a -3dB bandwidth. Calculate it for your motor-only J and b. Then for motor+gearbox. How much bandwidth did the gearbox cost?
4. You run a Bode plot and see a resonance peak at 15 Hz that your rigid-body G(s) doesn't predict. Name 2 possible physical sources of this resonance in a PLA gearbox.

**Design Judgment (1):**
1. Your measured Bode plot doesn't match the predicted G(s) above 10 Hz. The prediction says -40dB/dec rolloff, but the real data shows a bump then steeper rolloff. Is your model wrong? What's the model missing? How would you update it?

**Teach It (1):**
- Explain system ID to a MECH 380 student: "In class they give you G(s). In real life, how do you find it?" Use your actuator as the example.

- [ ] **Step 2: Verify** (5 CC, 4 AP, 1 DJ, 1 TI = 11 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/08-dynamics-system-id.md
git commit -m "feat(learning): add workbook 08 — dynamics & system ID"
```

---

### Task 10: Workbook 09 — Impedance Control

**Files:**
- Create: `testing/learn/workbooks/09-impedance-control.md`
- Reference: `testing/learn/campaign-walkthrough.md` (Phase 4), `testing/campaign/test-campaign-rev00b.md` (T-017, T-018), `research/gemini-deep-research/01-actuator-testing-methodology/response.md` (impedance section)

**Format:** Interview Q&A + applied (7 Concept Check, 3 Applied)

- [ ] **Step 1: Write workbook**

**Concept Check (7):**
1. What is impedance control? How does it differ from position control?
2. Write the impedance control law: τ = -K(θ - θ₀) - Bθ̇. What does each variable represent physically?
3. Why can a QDD do impedance control but a 50:1 gearbox can't? (transparency, friction, reflected inertia)
4. What's the difference between Tier A (ODrive PID as spring) and Tier B (Python torque loop)? Trade-offs?
5. Why does USB jitter matter for impedance control? At what stiffness does it become a problem?
6. Why does Tesla care about impedance control for Optimus? What task requires it? (human-robot interaction, unknown environments)
7. Cornelius (UVic → Tesla Optimus) suggested extending QDD to a robotic arm. Why does impedance control matter for an arm?

**Applied Problems (3):**
1. You want full-scale torque (16 Nm) at ±5.7° deflection. What K is needed? What B gives critical damping if Jreflected = 0.075 kg·m²?
2. Your Python loop runs at 200 Hz. What's the loop period? If the actuator has a natural frequency of 8 Hz, how many control updates per oscillation cycle? Is this enough?
3. You set K = 50 Nm/rad, B = 2 Nm·s/rad. Someone displaces the output 0.1 rad. What torque does the actuator command? If they push with 5 Nm of force, where does the equilibrium land?

**Design Judgment (1):**
1. Your impedance controller chatters near the center position. The output makes a buzzing sound. Diagnose: is this backlash, too-high stiffness, too-low damping, or something else? List your diagnostic steps.

**Teach It (1):**
- Explain impedance control to a mech eng student using only the spring analogy: "Imagine the actuator IS a spring. You get to choose how stiff. Why is that useful for a robot?"

- [ ] **Step 2: Verify** (7 CC, 3 AP, 1 DJ, 1 TI = 12 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/09-impedance-control.md
git commit -m "feat(learning): add workbook 09 — impedance control"
```

---

### Task 11: Workbook 10 — Backlash & Compliance (Pre/Post-Lab)

**Files:**
- Create: `testing/learn/workbooks/10-backlash-compliance.md`
- Reference: `testing/learn/campaign-walkthrough.md`, `testing/campaign/test-campaign-rev00b.md` (T-012, Phase 1)

**Format:** Pre/post-lab (Phase 1 backlash measurement tests)

- [ ] **Step 1: Write workbook**

**PRE-LAB — Concept Check (5):**
1. What is backlash in a gear system? Where does it come from physically?
2. Why is backlash the #1 spec for a QDD? How does it affect positioning and impedance control?
3. What's the difference between backlash (deadband) and compliance (PLA tooth deflection under load)?
4. Describe the T-012 measurement method. Why measure at 4+ angular positions around the revolution?
5. What is a hysteresis plot (output angle vs applied torque)? What does the flat region near zero torque represent?

**PRE-LAB — Applied Problems (2):**
1. Your dial indicator reads 0.15mm at a radius of 40mm from center. What angular backlash is that in degrees? Does it pass the 0.5° requirement?
2. If backlash is 0.3° at the output, what is it at the motor side (through 5:1)? Why does this matter for encoder-based position control?

**POST-LAB — Design Judgment (2):**
(Complete after T-012 and T-013 data)
1. Your backlash varies from 0.2° to 0.6° depending on output position. What does this non-uniformity tell you about the gearbox? List 2 possible causes.
2. After 2 hours of testing, you re-measure backlash and it's grown from 0.3° to 0.45°. Is this expected for PLA? What's happening physically? Should you be concerned?

**POST-LAB — Teach It (1):**
- Using your actual measured backlash number, explain to a controls engineer: "Here's the backlash in my QDD. Here's how it affects impedance control. Here's what I did about it."

- [ ] **Step 2: Verify** (5 CC, 2 AP pre-lab; 2 DJ, 1 TI post-lab = 10 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/10-backlash-compliance.md
git commit -m "feat(learning): add workbook 10 — backlash & compliance (pre/post-lab)"
```

---

### Task 12: Workbook 11 — GD&T & Tolerancing

**Files:**
- Create: `testing/learn/workbooks/11-gdt-tolerancing.md`
- Reference: `drawings/gdt-annotations.md`, `docs/design/tolerance-scheme.md`

**Format:** Applied problems heavy (5 Concept Check, 4 Applied)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. What is a datum reference frame? Name the three datums for your gearbox housing and why each was chosen.
2. Explain the difference between a size tolerance (±0.1mm) and a geometric tolerance (⌖ 0.05). When do you need the geometric one?
3. What does H7 mean in the ISO fit system? Break down: H = hole basis, 7 = IT7 grade. What's the tolerance zone?
4. Name 3 geometric characteristics (from the 14 GD&T symbols) and give a real example from your gearbox where each matters.
5. What's the difference between concentricity and runout? Which would you use for the bearing bore in the housing?

**Applied Problems (4):**
1. Your housing bearing bore is Ø22H7. Look up or calculate the tolerance zone for 22mm nominal at IT7. What's the min/max diameter?
2. You need the sun gear shaft to fit into a bearing with 0.01-0.04mm clearance. What shaft tolerance class achieves this? (Hint: hole-basis fit system)
3. Tolerance stackup: the carrier assembly has 3 features in series (bearing seat → carrier bore → planet pin). Each has ±0.1mm tolerance. What's the worst-case stackup? What's the statistical (RSS) stackup?
4. Your FDM printer has ±0.2mm accuracy. You need H7 tolerance on a 22mm bore (tolerance zone ≈ 0.021mm). Can you achieve this as-printed? What compensation strategy do you use?

**Design Judgment (1):**
1. A Tesla interviewer hands you a gearbox part and asks: "How would you tolerance this for production?" Walk through your process: datum selection, critical features, which tolerances to call out, and how you'd verify them.

**Teach It (1):**
- Explain to a student who only knows ±mm tolerances: why does GD&T exist? What problem does it solve that ± can't?

- [ ] **Step 2: Verify** (5 CC, 4 AP, 1 DJ, 1 TI = 11 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/11-gdt-tolerancing.md
git commit -m "feat(learning): add workbook 11 — GD&T & tolerancing"
```

---

### Task 13: Workbook 12 — DFM & Manufacturing

**Files:**
- Create: `testing/learn/workbooks/12-dfm-manufacturing.md`
- Reference: `docs/design/manufacturing-tips.md`, `docs/design/tolerance-scheme.md`, `docs/original-documentation-jan4/trade-studies.md`

**Format:** Design judgment heavy (5 Concept Check, 2 Applied, 2 Design Judgment)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. What does DFM (Design for Manufacturability) mean? Give 3 examples from your gearbox where design was constrained by manufacturing.
2. Why does print orientation matter for FDM gears? Which orientation gives the strongest tooth roots?
3. What is a calibration coupon and why should you print one with every batch of parts?
4. Heat-set inserts: why use them in 3D prints instead of just self-tapping screws? What are the design rules (pilot hole, depth, perimeter)?
5. How does FDM tolerance (±0.2mm) compare to CNC machining (±0.025mm)? What design changes does this force?

**Applied Problems (2):**
1. You need a press-fit bearing into a PLA housing. The bearing OD is 22.000mm. Your printer consistently prints holes 0.15mm undersized. What nominal bore diameter should you model in CAD? What's your expected interference?
2. Your gear teeth need to mesh with 0.05mm backlash. Your printer accuracy is ±0.2mm per feature. Two meshing features = ±0.4mm worst case. Can you achieve 0.05mm backlash as-printed? What's the realistic minimum?

**Design Judgment (2):**
1. A Tesla interviewer asks: "You 3D printed this gearbox. How would you redesign it for aluminum CNC production?" Walk through: what changes in geometry, tolerances, assembly method, and cost? What stays the same?
2. Your gearbox carrier is cracking at the bearing shoulder after testing. It's PLA, printed with teeth perpendicular to layer lines. Diagnose the failure mode and propose 3 design/manufacturing fixes ranked by effort.

**Teach It (1):**
- Explain to someone who's never 3D printed: "Why did I choose FDM for a gearbox when it's clearly worse than machining? And how did I work around the limitations?"

- [ ] **Step 2: Verify** (5 CC, 2 AP, 2 DJ, 1 TI = 10 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/12-dfm-manufacturing.md
git commit -m "feat(learning): add workbook 12 — DFM & manufacturing"
```

---

### Task 14: Workbook 13 — FEA Literacy

**Files:**
- Create: `testing/learn/workbooks/13-fea-literacy.md`
- Reference: No existing FEA docs in project — this workbook is built from first principles + course material (MECH 360)

**Format:** Design judgment + scenarios (5 Concept Check, 2 Applied, 2 Design Judgment)

- [ ] **Step 1: Write workbook**

**Concept Check (5):**
1. What does FEA solve, at a high level? What physical equation is it approximating? (equilibrium, compatibility, constitutive)
2. What is meshing? Why does mesh density matter? What happens if your mesh is too coarse? Too fine?
3. Name 3 types of boundary conditions and when you'd use each (fixed, pinned, symmetry, pressure, displacement).
4. What is a stress singularity? Where do they appear and why should you ignore them?
5. How do you know if your FEA results are correct? Name 2 validation approaches.

**Applied Problems (2):**
1. You want to FEA the carrier bearing shoulder. Describe your setup: what geometry do you model (full part? simplified?), what loads do you apply (where does the 16 Nm come from?), what boundary conditions, what material properties for PLA+?
2. Your FEA shows a peak stress of 35 MPa at a tooth root. PLA+ tensile strength is ~50 MPa. What safety factor is that? Is it sufficient? What does the safety factor NOT tell you about fatigue?

**Design Judgment (2):**
1. Your FEA shows the gear teeth pass stress analysis, but the prototype breaks after 10 minutes of testing. List 4 reasons the FEA could "pass" while reality "fails." (Hint: material model, load case, fatigue, print defects)
2. A Tesla interviewer asks: "When do you trust FEA and when don't you?" Give a 2-minute answer that shows engineering judgment, not textbook recitation. Reference a real example from your QDD project.

**Teach It (1):**
- Explain to a non-engineer: "FEA lets me simulate stress on a computer before I break the real thing. But it's not magic — here's when it lies to you."

- [ ] **Step 2: Verify** (5 CC, 2 AP, 2 DJ, 1 TI = 10 total)

- [ ] **Step 3: Commit**

```bash
git add testing/learn/workbooks/13-fea-literacy.md
git commit -m "feat(learning): add workbook 13 — FEA literacy"
```

---

## Execution Notes

- **Parallelizable tasks:** Tasks 2-14 are independent — any subset can be written in parallel by subagents. However, workbooks should be internally consistent, so each workbook is one atomic task.
- **Quality check per workbook:** Every question must use Aaron's actual hardware numbers where applicable. No generic textbook problems. Questions should be answerable from the reference material (open-book) but require synthesis, not just copying.
- **Post-lab sections** (tasks 5 and 11) have placeholder questions — these get filled in after Aaron has test data. Mark them clearly with `[COMPLETE AFTER TEST DATA]` tags.
- **After all workbooks are written:** Update the QDD project STATE.md to reflect the learning system is ready.
