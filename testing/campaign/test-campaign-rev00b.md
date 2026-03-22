# Test Campaign — Rev 00B Quantitative Characterization

> **Goal:** Systematically characterize the QDD actuator — mechanical, electrical, and controls — building a body of work that demonstrates actuator engineering competence.
>
> **Motor:** ODrive D6374-150KV | **Controller:** ODrive v3.6 | **Encoder:** AS5047P (14-bit)
> **Key constant:** $K_t = 8.27 / K_V = 8.27 / 150 = 0.0551 \text{ Nm/A}$ (verify in Phase 0)

---

## Campaign Overview

```
Phase 0: Motor alone (baseline)           ← "what does the motor do by itself?"
  → Phase 1: Gearbox mechanical            ← "what does the gearbox add mechanically?"
    → Phase 2: Powered characterization    ← "what do the numbers say when it's running?"
      → Phase 3: System ID & dynamics      ← "what's the transfer function? bandwidth?"
        → Phase 4: Impedance control       ← "can it feel like a spring?" (the QDD payoff)
          → Phase 5: Performance limits    ← torque capacity, thermal, durability (later)
```

**Why this order:** Each phase builds on the previous. Without the motor baseline (Phase 0), you can't isolate gearbox effects. Without characterization data (Phase 2), system ID is guessing. Without a plant model (Phase 3), impedance control is trial and error.

---

## What This Proves (Tesla Relevance)

| Phase | Tesla Skill Demonstrated | Posting Language |
|-------|--------------------------|-----------------|
| 0–2 | Hands-on actuator & component testing (motor, gear, sensors) | "Prototype assembling and testing" (Req 259949) |
| 0–2 | Python test scripts | "Python/Matlab test script development" (Req 259949) |
| 3 | Actuator model development | "Actuator model development" (Req 259949) |
| 3–4 | Control theory — motor and motion control | "Control Theory — motor and motion control basics" (preferred) |
| 4 | System-level integration, first principles | "First principles problem solving" |
| All | Systematic V&V methodology | "Own the mechanical design of test equipment from concept to deployment" (Req 255621) |

**What a Tesla engineer sees on your portfolio:** Not "student built a gearbox." Instead: "Student designed a QDD actuator, characterized it against requirements, derived the plant model from real data, and demonstrated impedance control — the defining capability of quasi-direct-drive."

---

## Portfolio Deliverables

Each phase produces something concrete for the portfolio page. These match the standard plots from QDD/SEA actuator papers (MIT Cheetah, Stanford Doggo, BEAR, ANYmal):

| Phase | Deliverable | Format | Research Precedent |
|-------|------------|--------|--------------------|
| 0 | Motor cogging torque profile | $I_q$ vs position plot | Standard motor characterization |
| 0+2 | **Friction model overlay** — motor alone vs motor+gearbox | Coulomb+viscous fit, both curves overlaid | Standard in every actuator paper |
| 1 | Backlash measurement + methodology | Number + photo of dial indicator setup | Deadband/hysteresis is expected |
| 1+2 | **Backlash/hysteresis plot** — output angle vs applied torque (slow ramp) | Shows deadband + PLA compliance | Research says this is "especially important for PLA planetary" |
| 2 | Step response with extracted metrics ($t_r$, OS%, $t_s$) | Annotated time-domain plot | Standard dynamics characterization |
| 3 | **Plant transfer function** (derived from real data, not textbook) | Equation + predicted vs measured Bode | This is the "I did real system ID" proof |
| 3 | **Motor vs motor+gearbox Bode overlay** | Frequency response comparison | Shows exactly what the gearbox costs in bandwidth |
| 4 | **Impedance control demo** — virtual spring at multiple stiffnesses | Video + force-displacement plot | MIT Cheetah paper uses measured vs commanded force trajectories |
| 4 | Impedance control block diagram | TikZ diagram for portfolio page | Standard controls presentation |
| — | **Torque-speed envelope** (continuous + peak) | Performance boundary plot | MIT/Stanford Doggo style — "not just it spins" |

**Bonus portfolio-grade evidence (from research):**
- Tooth flank photos before/after testing (wear documentation)
- Backlash measurement repeated over time (degradation tracking)
- Print orientation and parameters documented alongside mechanical data

---

## Equipment You Have

| Tool | Used For |
|------|----------|
| ODrive v3.6 + odrivetool | Motor control, $I_q$ telemetry (your main instrument) |
| Calipers | Dimensional checks, backlash with lever arm |
| Dial indicator | Backlash measurement at output shaft |
| Kitchen scale (<3 kg) | Force measurement via lever arm → torque |
| Torque wrench | Too high range for 3D prints, but useful for reference |

**Torque from a scale:** Attach a lever arm of known length $L$ to the output shaft. Rest it on the scale. Torque $= F \times L = (m \times 9.81) \times L$. With a 200 mm arm and 3 kg max scale, you can measure up to ~5.9 Nm. Covers backdrivability (requirement: <1 Nm) easily.

**What you DON'T need right now:** Thermocouples (Phase 5), spring scale (kitchen scale + lever arm works), test bench (table + clamp is fine for Phases 0–4).

---

## Safety Checklist (Before ANY Powered Test)

> A 150KV D6374 through a 5:1 gearbox can produce 16 Nm. That will break fingers and strip plastic gears without warning.

- [ ] **Brake resistor connected** — aggressive deceleration without one causes bus overvoltage and ODrive faults. ODrive getting-started docs emphasize this.
- [ ] **Current limits set** — cap `motor.config.current_lim` well below motor max during early tests. Start at 5A, increase incrementally.
- [ ] **Watchdog enabled** — `axis.config.watchdog_timeout` (e.g., 0.5s). If your Python script crashes, ODrive disables the axis instead of holding last command.
- [ ] **E-stop ready** — know how to kill power instantly. `odrv0.axis0.requested_state = AXIS_STATE_IDLE` is software e-stop; physical power switch is better.
- [ ] **Encoder coupling verified** — encoder slip causes "disastrous oscillations or runaway" (ODrive docs). Check coupling is tight before every session.
- [ ] **Hands clear of pinch points** — gearbox output can snap to position. Keep clear during position/torque control.

---

## ODrive v3.6 — What the Research Told Us

> Source: `research/gemini-deep-research/01-actuator-testing-methodology/response.md`

**Key facts that shape this campaign:**

| What | Reality | Implication |
|------|---------|-------------|
| Python polling rate | ~200 Hz reliable, ~500 Hz achievable but jittery | Fine for data logging. Tight for impedance control. |
| Internal control loop | ~8 kHz FOC | Your Python loop is 1–6% of internal rate. Plan accordingly. |
| Built-in oscilloscope | `odrv.oscilloscope` — captures at full 8 kHz rate, read out afterward | Use for high-rate captures (cogging, current ripple). Limited to one signal at a time without firmware mods. |
| `BulkCapture` utility | `odrive.utils.BulkCapture` — ~500 Hz, measures achieved rate | Best tool for multi-signal logging in Phases 0–2. |
| Torque mode | `input_torque` in N·m, first-class in v0.5.6 | Cleanest path for system ID and impedance control. |
| USB protocol | Can't use ASCII and native protocol simultaneously | Stick with native protocol (Python API) for everything. |
| Jitter | Worst-case jitter matters more than average rate for impedance control | Start with overdamped, low-K impedance. Jitter is the enemy. |

**Impedance control implementation tiers (from research):**

| Tier | Method | Loop Rate | Best For |
|------|--------|-----------|----------|
| **A** | Use ODrive's internal PID as spring-damper — command `input_pos` from Python | 8 kHz (internal) | Stable demo, no jitter issues. Start here. |
| **B** | Compute impedance law in Python, send `input_torque` | 100–200 Hz | True impedance control, but limited by USB jitter. |
| **C** | Impedance law on microcontroller (Teensy/STM32), torque commands to ODrive via UART | 500–1000 Hz | Research-grade. Stretch goal. |

**For this campaign:** Start with Tier A for T-017, move to Tier B for T-018/T-019. Tier C is a future upgrade if you want portfolio-level bandwidth numbers.

---

## Phase 0: Motor-Only Baseline

> **Setup:** Motor on the table, no gearbox attached. Just motor + encoder + ODrive.
> **Purpose:** Establish what the motor does by itself so you have a reference.
> **Time estimate:** ~1–2 hours.

### T-009: Verify motor $K_t$ (torque constant)

**Why:** Every torque measurement in this campaign uses $\tau = K_t \times I_q$. If your $K_t$ is wrong, every number downstream is wrong. The 150KV rating gives $K_t = 0.0551$ Nm/A theoretically, but real motors vary. This is a 5-minute sanity check.

**What you're measuring:** $I_q$ at a known constant velocity with no load.

**How:**
1. ODrive in velocity control mode.
2. Command a slow constant velocity (e.g., 2 rev/s).
3. Log $I_q$ for 5 seconds. The average $I_q$ at no-load tells you the motor's internal friction torque.
4. This isn't a direct $K_t$ measurement, but it confirms the motor behaves as expected. If $I_q$ is wildly different from what the datasheet predicts, something's wrong before you even add the gearbox.

**What "good" looks like:** No-load $I_q$ should be small (motor friction only). If it's >1A at low speed, something's wrong (wiring, encoder, configuration).

**Traces to:** Every subsequent test that uses $K_t$.

---

### T-010: Motor cogging & friction profile

**Why:** The motor has its own cogging torque (from magnets passing stator teeth) and friction. You need to know this baseline so you don't blame the gearbox for motor artifacts.

**What you're measuring:** $I_q$ vs rotor position during slow constant-velocity rotation.

**How:**
1. ODrive in velocity control mode.
2. Command a very slow velocity (~0.5 rev/s motor shaft).
3. Log $I_q$ and encoder position at the highest sample rate you can.
4. Run for several full revolutions. Repeat in both directions.
5. Plot $I_q$ vs position — you'll see periodic ripple from cogging.

**What "good" looks like:**
- Periodic $I_q$ ripple at the motor's cogging frequency (14 pole pairs → 42 cogging cycles/rev for a typical 3-phase)
- Peak-to-peak cogging current should be relatively small
- Roughly symmetric CW vs CCW

**Traces to:** T-006 (gearbox friction) — you subtract this baseline.

---

### T-011: Motor friction vs speed (no-load)

**Why:** This is the motor-only version of T-006. Same test, no gearbox. Gives you the $\tau_f(\omega)$ baseline.

**What you're measuring:** Average $I_q$ at several constant speeds, no load.

**How:**
1. ODrive in velocity control mode.
2. Command speeds: 1, 2, 5, 10, 20 rev/s (motor shaft). Let each settle for 2–3 sec, log $I_q$ for 5 sec.
3. Both directions.
4. Compute $\tau_f = K_t \times \overline{I_q}$ at each speed.
5. Plot $\tau_f$ vs $\omega$. Fit: $\tau_f = \tau_c + b\omega$ (Coulomb + viscous).

**What "good" looks like:**
- Roughly linear $\tau_f$ vs $\omega$
- Coulomb component ($\tau_c$, the y-intercept) should be small — this is bearing + seal friction
- No sudden jumps or erratic behavior

**Traces to:** T-006 — the difference between T-011 (motor alone) and T-006 (motor + gearbox) IS the gearbox friction.

---

### T-014: Motor step response (baseline)

**Why:** You need the motor-alone step response to compare against motor+gearbox (T-007). The difference shows how the gearbox affects dynamics — added inertia, friction, backlash all change the response.

**What you're measuring:** Position, velocity, and $I_q$ vs time after a position step command.

**How:**
1. ODrive in position control mode with default PID gains.
2. Command a 1-revolution step.
3. Log position, velocity, $I_q$ at max sample rate throughout the transient.
4. Repeat 3–5 times for consistency.
5. Extract: rise time ($t_r$, 10–90%), overshoot (%), settling time ($t_s$, ±2%), steady-state error.

**What "good" looks like:** Clean second-order response. Overshoot and settling time depend on gains, but the shape should be textbook.

**Controls concept:** This is a time-domain characterization. You're seeing the closed-loop response $\frac{C(s)G(s)}{1 + C(s)G(s)}$ where $C(s)$ is the PID controller and $G(s)$ is the motor plant. You'll extract $G(s)$ in Phase 3.

**Traces to:** T-007 (motor+gearbox step response), Phase 3 (system ID).

---

## Phase 1: Gearbox Mechanical (No Motor Power)

> **Setup:** Gearbox assembled on Rev 00B, motor attached but unpowered.
> **Purpose:** Measure what you can with just hands and instruments.
> **Time estimate:** ~30 min.

### T-012: Backlash measurement

**Why:** Backlash is requirement R-01 (≤ 0.5°). This is the most important single number for a QDD — it directly limits positioning accuracy and impedance control transparency.

**What you're measuring:** Angular play at the output shaft when the input (sun gear / motor shaft) is locked.

**How:**
1. Lock the motor shaft (ODrive in position hold, or physically clamp it).
2. Mount a dial indicator against a lever arm on the output shaft, at a known radius $r$ from center.
3. Rotate the output shaft CW until it stops against the gear mesh. Zero the indicator.
4. Rotate CCW until it stops. Read the indicator.
5. Angular backlash $= \arctan(\delta / r)$ where $\delta$ is the dial indicator reading.
6. Repeat at 4+ angular positions (rotate the output 90° each time) to check for variation around the orbit.

**What "good" looks like:**
- Backlash < 0.5° (hard requirement)
- Relatively uniform around the revolution (big variation = planet or carrier issue)

**Alternate method (if dial indicator setup is awkward):** Use a lever arm and mark positions on paper, or measure arc length with calipers at a known radius.

**Traces to:** R-01, U-08.

---

### T-013: Hand backdriving feel (qualitative + rough quantitative)

**Why:** Quick check of R-04 (backdrivability < 1 Nm) before doing the full powered test (T-008). If it's stiff by hand, you know immediately.

**What you're measuring:** How much force to turn the output shaft by hand, and qualitative feel (smooth vs notchy vs sticky).

**How:**
1. Motor disconnected from ODrive (or ODrive in idle — no active control).
2. Attach a ~200 mm lever arm to the output shaft.
3. Rest the lever arm on the kitchen scale.
4. Slowly press down and read the scale as the shaft just starts to turn.
5. Torque $= (\text{scale reading in kg}) \times 9.81 \times 0.2\text{ m}$
6. Note: smooth or notchy? Any sticky spots? Symmetric CW/CCW?

**What "good" looks like:**
- < 0.5 kg on the scale at 200 mm arm (= ~1 Nm) → passes R-04
- Smooth rotation, no periodic sticking

**Traces to:** R-04, U-09, T-008.

---

## Phase 2: Powered Characterization (Motor + Gearbox)

> **Setup:** Full actuator — motor + gearbox + encoder + ODrive.
> **Purpose:** Quantitative characterization with data logging. Compare to Phase 0 baseline.
> **Time estimate:** ~2 hours.

### T-006: Friction characterization — Coulomb + viscous model
*(Full procedure in test-tracker.md)*

**Key addition:** After you get T-006 data, subtract the T-011 (motor-only) curve. The difference is the gearbox friction contribution.

$$\tau_{gearbox}(\omega) = \tau_{total}(T\text{-}006) - \tau_{motor}(T\text{-}011)$$

This tells you exactly how much friction the gearbox adds at each speed. Plot both curves overlaid — this is a portfolio-quality figure.

### T-007: Step response — motor + gearbox
*(Full procedure in test-tracker.md)*

**Key addition:** Compare directly to T-014 (motor-alone step response). Overlay the two plots. The differences tell you:
- **Slower rise time** → gearbox added inertia (reflected through $N^2$)
- **More overshoot** → backlash or compliance in the gear train
- **Higher steady-state error** → friction or backlash eating into positioning
- **Oscillation at a different frequency** → the gearbox changed the natural frequency

### T-008: Backdriving torque — passive resistance
*(Full procedure in test-tracker.md)*

Compare to T-013 (hand feel). The ODrive telemetry gives you the quantitative version.

---

## Phase 3: System Identification & Dynamics

> **Setup:** Same as Phase 2 — full actuator + ODrive.
> **Purpose:** Derive the plant transfer function from real data. Measure bandwidth. This is where the controls theory connects to hardware.
> **Time estimate:** ~2–3 hours.
> **Prerequisites:** Phase 0 and Phase 2 complete (you need the step response data).

### Why This Phase Matters

In MECH 380 you learn to analyze systems given a transfer function $G(s)$. In real engineering, nobody hands you $G(s)$ — you have to measure it. This phase is where you go from "textbook controls" to "I identified a real plant from experimental data." That's a huge differentiator.

### T-015: Plant identification — direct torque-to-motion

**Why:** Extract the motor's transfer function $G_{motor}(s)$ and the full actuator's transfer function $G_{actuator}(s)$ from experimental data.

**Key insight from research:** You don't need to invert a closed-loop response. ODrive v3.6 supports torque mode directly (`input_torque`), so you can command a known torque and measure the resulting motion — **open-loop plant ID, the cleanest approach.** No PID gain inversion needed.

**The physics (what you should understand):**

Since the ODrive's FOC loop handles electrical dynamics internally (~8 kHz), the plant you're identifying is from torque command to position:

$$G_{plant}(s) = \frac{1}{Js^2 + bs}$$

That's a double integrator with friction. Two unknowns: $J$ (inertia) and $b$ (viscous friction). You already measured $b$ in T-011. So you're really just finding $J$.

**What breaks this simple model for your printed gearbox (from research):**
- **Backlash** — discontinuous deadzone near zero torque
- **Coulomb friction + stiction** — nonlinear near zero velocity
- **Plastic compliance** — PLA teeth act as a torsional spring under load

So: do the linear ID, but also explicitly quantify where the model fails (e.g., "valid above ±0.2 Nm and $|\omega| > 0.5$ rad/s"). Reporting the model's limitations is more impressive than pretending it's perfect.

**How:**
1. Set ODrive to **torque control mode** (`CONTROL_MODE_TORQUE_CONTROL`). No position/velocity loops active.
2. Apply a step torque command (e.g., 0.5 Nm) via `input_torque`. Log position and velocity at ~200–500 Hz using `BulkCapture`.
3. The motor will accelerate — velocity ramps linearly (inertia) with a steady-state slope determined by $b$.
4. Fit $J$ from the acceleration: $J = \tau / \dot{\omega}$ (initial slope of velocity vs time).
5. Repeat for motor alone and motor+gearbox. The gearbox reflects inertia: $J_{out} \approx N^2 J_{motor} + J_{gearbox}$.

**What you get:** Two transfer functions — motor alone and motor+gearbox. The difference tells you the gearbox's reflected inertia and added friction. These are the models you'll use for controller design in Phase 4.

**Traces to:** T-016 (frequency response validates the model), Phase 4 (impedance control needs the plant model).

---

### T-016: Frequency response (Bode plot)

**Why:** The Bode plot shows your system's bandwidth — the frequency range where it can track commands. This is THE metric for actuator performance in robotics. Tesla's recruiting language emphasizes "torque/force sensing and instrumentation" — bandwidth is how you quantify how fast and responsive the actuator is.

**What you're measuring:** Output amplitude and phase vs input frequency.

**Two methods (from research):**

**Method 1: Torque chirp (recommended — cleanest for plant ID)**
1. ODrive in **torque control mode** (`input_torque`).
2. Command a chirp (swept sine) torque: small amplitude (e.g., 0.3 Nm), sweeping from 0.5 Hz to 50+ Hz over 30–60 seconds.
3. Add a small DC bias torque to keep gears engaged on one flank (avoids backlash chattering during sweep).
4. Log `input_torque`, `pos_estimate`, `vel_estimate` at ~500 Hz via `BulkCapture`.
5. Compute FRF using FFT: $G(j\omega) = \frac{X(j\omega)}{\tau(j\omega)}$ where $X$ is position/velocity and $\tau$ is applied torque.
6. Plot Bode diagram: magnitude and phase vs frequency (log scale).

**Method 2: Discrete sine dwell (cleaner at specific frequencies)**
1. Same setup, but command steady sinusoidal torque at individual frequencies: 0.5, 1, 2, 5, 10, 20, 50 Hz.
2. Log 5+ full cycles at each frequency. Compute gain and phase from the data.
3. More time-consuming but gives cleaner points if the chirp FFT is noisy.

**What "good" looks like:**
- Flat gain at low frequencies (system tracks well)
- Bandwidth (−3 dB crossover) somewhere reasonable — depends on inertia and friction
- No sharp resonance peaks (would indicate compliance or backlash issues)
- Phase margin > 30° at the gain crossover frequency (stable with margin)

**Do this twice:** Motor alone AND motor+gearbox. Overlay the Bode plots. The gearbox will reduce bandwidth (more inertia) and may introduce resonance (PLA gear compliance). This comparison is portfolio gold.

**Validation:** If your identified $G(s)$ from T-015 is correct, the predicted Bode plot should match the measured Bode plot. Overlay both — agreement validates your model, disagreement tells you what the model is missing.

**Controls connection (MECH 380):** This is the frequency-domain view of the same system you characterized in the time domain (step response). The Bode plot IS the transfer function, just viewed differently.

**Traces to:** R-11 (speed capability), Phase 4 (bandwidth limits impedance control performance).

---

## Phase 4: Impedance Control

> **Setup:** Full actuator + ODrive. Output shaft accessible for interaction (pushing/pulling by hand or with spring scale).
> **Purpose:** Demonstrate the defining capability of a QDD — transparent force interaction.
> **Time estimate:** ~2–3 hours.
> **Prerequisites:** Phase 3 (you need the plant model for tuning).

### Why This Is The Whole Point

A regular gearbox is a position device — you command an angle, it goes there, and if something pushes back it fights to hold position. A QDD is a force device — it can feel what's pushing on it and respond naturally. This is how robot arms interact safely with humans and adapt to contact.

Impedance control makes the actuator behave like a virtual spring-damper:

$$\tau_{cmd} = -K(\theta - \theta_0) - B\dot{\theta}$$

Where:
- $K$ = virtual stiffness (Nm/rad) — you choose this
- $B$ = virtual damping (Nm·s/rad) — you choose this
- $\theta_0$ = equilibrium position
- $\theta$ = current position (from encoder)
- $\dot{\theta}$ = current velocity (from encoder)

The actuator feels like a spring: push it, it pushes back proportionally. Let go, it returns to center. Increase $K$ and it feels stiffer. Decrease $K$ and it feels compliant. This is what Tesla's Optimus uses to handle objects without crushing them.

### T-017: Virtual spring (Tier A — ODrive internal loops)

**Why:** Simplest impedance controller — use ODrive's built-in position PID as a spring-damper. This is Tier A from the research: the most robust approach because it runs at the internal 8 kHz loop rate with no USB jitter.

**The idea:** ODrive's position controller IS a spring-damper: `pos_gain` acts as $K$ (stiffness) and `vel_gain` acts as $B$ (damping). By setting these gains and commanding an equilibrium position (`input_pos`), you get impedance control "for free" at 8 kHz.

**How:**
1. Set ODrive to position control mode.
2. Set `controller.config.pos_gain` to a low value (e.g., 5.0 — this is your virtual stiffness in turns, roughly $K / (2\pi)$).
3. Set `controller.config.vel_gain` for damping.
4. Command `controller.input_pos` = current position (equilibrium).
5. Push the output shaft by hand — it should resist gently and return.
6. From Python, adjust gains in real time and log position + $I_q$.

**What to measure:**
- Slowly push the shaft and log force (lever arm + scale) vs displacement → should be linear with slope $\approx K$
- Release and watch the return — should be smooth, not oscillatory (if oscillatory, increase `vel_gain`)
- Repeat at several gain settings

**What "good" looks like:**
- Linear force-displacement relationship
- Smooth feel, no cogging or sticking
- Returns to setpoint when released
- Feels different at different gain values

**What "bad" looks like (and from research, what to expect with backlash):**
- **Limit cycling / chatter near center** → backlash deadzone causes the controller to "hunt" across the gap. **Mitigation:** add a small position deadband, or bias torque to keep teeth engaged on one flank.
- **Doesn't return to center** → Coulomb friction exceeds spring restoring force. Increase K or accept the dead zone.
- **Buzzing / vibration** → gain too high for the mechanical compliance. Reduce gain.

**Safety:** Start with very low gains. A 16 Nm actuator can hurt you. Watchdog enabled. Current limits set. E-stop ready.

### T-018: True impedance control (Tier B — Python torque loop)

**Why:** Move from "springy position control" (Tier A) to real impedance control: you compute the control law and send torque commands directly. This gives you true control over the impedance, but now you're limited by your Python loop rate (~100–200 Hz).

**How:**
1. Set ODrive to **torque control mode** (`CONTROL_MODE_TORQUE_CONTROL`).
2. In a Python control loop:
   ```python
   while running:
       pos = odrv0.axis0.encoder.pos_estimate  # turns
       vel = odrv0.axis0.encoder.vel_estimate  # turns/s
       # Convert to radians
       theta = pos * 2 * math.pi
       omega = vel * 2 * math.pi
       # Impedance law
       tau = -K * (theta - theta_0) - B * omega
       # Clamp torque for safety
       tau = max(-tau_max, min(tau_max, tau))
       odrv0.axis0.controller.input_torque = tau
       time.sleep(0.005)  # ~200 Hz
   ```
3. Start with **overdamped, low stiffness**: $K = 1$ Nm/rad, $B = 0.5$ Nm·s/rad (research says start overdamped because backlash + friction look like time delay).
4. **Backlash mitigation (from research):** Add a small torque bias (e.g., 0.1 Nm) to keep gears engaged on one flank. Or add a deadband: if $|error| < backlash$, command zero torque.
5. Sweep $K$ and $B$ combinations. Document the feel and log data.
6. Log and plot: position vs time after a displacement (should show damped oscillation), torque vs displacement (stiffness curve).

**Choosing K and B (from research):**
- Full-scale torque (16 Nm) at ±5.7° deflection → $K \approx 160$ Nm/rad (upper limit)
- Full-scale torque at ±2.9° → $K \approx 320$ Nm/rad (likely too stiff for Python loop)
- Choose $B$ for approximately critically damped behavior: $B \approx 2\sqrt{K \cdot J_{reflected}}$
- In practice, start much lower and increase until feel is good

**Controls connection:** This IS impedance control. The target impedance $Z(s) = K + Bs$. You're placing closed-loop poles. This maps directly to MECH 380 — you're doing controller design on your own hardware.

### T-019: Variable impedance demo (stretch goal)

**Why:** The killer demo — change stiffness in real time. Show the actuator going from "limp noodle" to "rigid joint" with a slider.

**How:**
1. Build a simple Python GUI (tkinter) with sliders for $K$ and $B$.
2. Run the impedance controller with live-adjustable parameters.
3. Record video of someone interacting with the output while adjusting stiffness.
4. This is the portfolio hero content — a video of smooth, intuitive force interaction with a 3D-printed actuator.

---

## PLA Gearbox Health Monitoring (All Phases)

> From research: "The right mindset is not 'what is the lifespan,' but 'how do I detect degradation early and quantify it.'"

**Run these checks at the start and end of every test session:**

- [ ] **Backlash measurement** (T-012 method) — track growth over time. Backlash increase = wear or creep.
- [ ] **No-load friction at reference speed** (e.g., 5 rev/s) — increasing $I_q$ for the same speed = wear.
- [ ] **Visual tooth inspection** — photograph tooth flanks under consistent lighting. Look for:
  - Whitening at tooth roots (stress cracking along layer lines)
  - Pitting or material removal on contact faces
  - Deformation / rounding of tooth tips
- [ ] **Housing temperature** (IR thermometer or hand feel) — PLA glass transition is ~60°C. If housing hits 45–55°C, teeth are softening. Stop and let it cool.

**Log these in a running table in `testing/data/health-log.csv`:**
```
date, session, backlash_deg, friction_Iq_at_5revs, housing_temp_C, notes
```

This becomes portfolio-grade wear documentation. Showing degradation tracking over time is more impressive than a single data point.

---

## Phase 5: Performance Limits (Later)

These are important but depend on Phases 0–4 being clean. Don't start here.

| Test | What | Needs | Traces To |
|------|------|-------|-----------|
| Torque capacity | Max torque before gearbox fails or slips | Load cell or heavy weights, careful safety setup | R-06, R-07 |
| Thermal derating | Continuous torque vs time until thermal steady state | IR thermometer at minimum, thermocouples ideal | R-08 |
| Durability | Run time before failure | Time, endurance test script, health monitoring data | R-05, R-10 |
| Efficiency | Input power vs output power | Load cell on output + input $I_q$ measurement | R-09 |
| Torque-speed envelope | Continuous and peak torque across speed range | Multiple test points at various speeds | Portfolio standard |

**PLA-specific failure modes to watch for (from research):**
- Tooth-root fatigue cracking (layer-line delamination at tooth root)
- Tooth face wear / pitting → increased backlash and noise
- Creep / permanent deformation under sustained load at elevated temperature
- Print orientation determines failure mode — teeth perpendicular to layers are weakest at the root

---

## ODrive Data Logging Cheat Sheet

Key signals to log:

| Signal | What It Tells You | ODrive Path |
|--------|-------------------|-------------|
| $I_q$ measured | Torque-producing current | `odrv0.axis0.motor.current_control.Iq_measured` |
| $I_q$ setpoint | Commanded torque current | `odrv0.axis0.motor.current_control.Iq_setpoint` |
| $I_d$ measured | Field current (should be ~0) | `odrv0.axis0.motor.current_control.Id_measured` |
| Encoder position | Rotor angle (turns) | `odrv0.axis0.encoder.pos_estimate` |
| Encoder velocity | Rotor speed (turns/s) | `odrv0.axis0.encoder.vel_estimate` |
| Input torque | Commanded torque (Nm) | `odrv0.axis0.controller.input_torque` |
| Vbus voltage | Supply voltage | `odrv0.vbus_voltage` |

### Option 1: BulkCapture (~500 Hz, multi-signal — use for most tests)

```python
from odrive.utils import BulkCapture
import odrive

odrv0 = odrive.find_any()
# ... configure axis, enter closed loop ...

# Capture at 500 Hz for 5 seconds
cap = BulkCapture(
    lambda: [
        odrv0.axis0.motor.current_control.Iq_measured,
        odrv0.axis0.encoder.pos_estimate,
        odrv0.axis0.encoder.vel_estimate,
    ],
    data_rate=500,
    duration=5.0
)
# cap.data is a list of [Iq, pos, vel] samples
# Save to CSV with timestamps
```

> BulkCapture measures and reports achieved rate. If it warns about rate drop, reduce data_rate.

### Option 2: Oscilloscope buffer (8 kHz, single signal — use for cogging/current ripple)

```python
from odrive.utils import oscilloscope_dump
# Captures whatever signal the firmware oscilloscope is configured to record
# Dumps to CSV at full control-loop rate
oscilloscope_dump(odrv0, num_vals=odrv0.oscilloscope.size, filename='scope.csv')
```

> Limited to one signal at a time without firmware mods. Best for high-rate single-channel captures.

### Option 3: Manual polling (~200 Hz, flexible — fallback)

```python
import odrive, time, csv

odrv0 = odrive.find_any()

with open('test_data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['time_s', 'Iq_A', 'pos_turns', 'vel_turns_s'])
    t0 = time.time()
    for _ in range(1000):  # ~5 sec at 200 Hz
        writer.writerow([
            round(time.time() - t0, 4),
            odrv0.axis0.motor.current_control.Iq_measured,
            odrv0.axis0.encoder.pos_estimate,
            odrv0.axis0.encoder.vel_estimate,
        ])
        time.sleep(0.005)
```

> **Important:** ~200 Hz is the reliable tier on Windows. Don't push past 500 Hz — jitter becomes worse than lower rate. Stick to native protocol (Python API), not ASCII.

---

## Execution Roadmap

### This week: Phase 0 (~1–2 hours)
- [ ] Set up ODrive with motor only (no gearbox)
- [ ] T-009: Verify $K_t$ / sanity check motor at low speed
- [ ] T-010: Log cogging profile (slow spin, $I_q$ vs position)
- [ ] T-011: Friction vs speed curve (5–6 speed points, both directions)
- [ ] T-014: Motor-alone step response (3–5 reps)
- [ ] Save all data CSVs in `testing/data/phase0/`

### Next session: Phase 1 (~30 min)
- [ ] T-012: Backlash with dial indicator
- [ ] T-013: Hand backdriving on scale

### Following session: Phase 2 (~2 hours)
- [ ] T-006: Friction characterization (powered, with gearbox)
- [ ] T-007: Step response (motor + gearbox)
- [ ] T-008: Backdriving torque (powered measurement)
- [ ] Compare Phase 2 data to Phase 0 baseline — generate overlay plots
- [ ] Save all data CSVs in `testing/data/phase2/`

### Phase 3 (~2–3 hours)
- [ ] T-015: Fit transfer function from step response data (Python + scipy)
- [ ] T-016: Frequency sweep → Bode plot (motor alone, then motor+gearbox)
- [ ] Validate: does the Bode plot match the predicted $G(s)$?
- [ ] Save data in `testing/data/phase3/`

### Phase 4 (~2–3 hours)
- [ ] T-017: Virtual spring impedance controller
- [ ] T-018: Virtual spring-damper
- [ ] T-019: Variable impedance demo with GUI (stretch goal)
- [ ] Record demo video for portfolio
- [ ] Save data + video in `testing/data/phase4/`

---

## What You'll Know By The End

| After Phase | You'll Have | You'll Understand |
|-------------|-------------|-------------------|
| 0 | Motor baseline (friction, cogging, step response) | What the motor does by itself — the reference for everything |
| 1 | Backlash number, backdriving torque | Whether the gearbox meets the two most critical QDD requirements |
| 2 | Friction model, system step response, motor vs gearbox comparison | Exactly what the gearbox costs in friction and dynamics |
| 3 | Plant transfer function, Bode plot, bandwidth | The mathematical model of your actuator — derived from YOUR data |
| 4 | Working impedance controller, virtual spring demo | The reason QDDs exist — transparent force interaction |

This progression goes from "I built a gearbox" to "I characterized an actuator system, identified the plant model, and implemented impedance control." That's the story for Tesla.

---

## Reference Papers & Resources

> From `research/gemini-deep-research/01-actuator-testing-methodology/response.md`

**Actuator design & characterization (read these):**
- MIT Proprioceptive Actuator (Cheetah) — impact mitigation, IMF metric, force tracking: `fab.cba.mit.edu/classes/865.18/motion/papers/mit-cheetah-actuator.pdf`
- Stanford Doggo — open-source QDD quadruped: `arxiv.org/abs/1905.04254` + `github.com/Nate711/StanfordDoggoProject`
- ANYmal platform — torque-controllable compliant joints: `dbellicoso.github.io/publications/files/hutter2017anymaltoward.pdf`

**Impedance control & bandwidth:**
- High-bandwidth active impedance, Z-width vs torque bandwidth: `mdpi.com/2076-0825/8/4/71`

**ODrive v0.5.6 docs:**
- Getting started: `docs.odriverobotics.com/v/0.5.6/getting-started.html`
- Commands & API: `docs.odriverobotics.com/v/0.5.6/commands.html`
- USB protocol: `docs.odriverobotics.com/v/0.5.6/usb.html`
- API reference: `docs.odriverobotics.com/v/0.5.6/fibre_types/com_odriverobotics_ODrive.html`

**FDM gear testing:**
- PLA gear fatigue vs infill: `sciencedirect.com/science/article/pii/S245232162300358X`
- PLA thermal limits (HDT ~59°C, Tg ~60°C): `um-support-files.ultimaker.com/materials/2.85mm/tds/PLA/Ultimaker-PLA-TDS-v5.00.pdf`

**Tesla Optimus (public):**
- Actuator integration hiring signal: `tesla.com/careers/search/job/mechanical-engineer-actuator-integration-optimus-258780`
- IEEE Spectrum expert commentary (harmonic drive + inverted roller screw): `spectrum.ieee.org/robotics-experts-tesla-bot-optimus`
- Actuator patent: `patents.google.com/patent/WO2024072984A1/en`
