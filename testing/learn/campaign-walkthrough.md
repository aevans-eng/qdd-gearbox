# Test Campaign Walkthrough — What You're Doing and Why

> This doc explains the intuition behind each phase of the Rev 00B test campaign. Read this first, then use `test-campaign-rev00b.md` for the actual procedures.
>
> **Assumed knowledge:** You know what your QDD is, what a planetary gearbox does, and you've used ODrive enough to spin the motor. Everything else is explained as it comes up.

---

## The Story in One Paragraph

You built a gearbox. Now you need to answer: *how good is it?* But "good" means different things — low friction? Low backlash? Fast response? Can it do impedance control? You can't answer all of these at once, and some answers depend on others. So the campaign is structured as a ladder: first understand the motor by itself (Phase 0), then measure the gearbox mechanically (Phase 1), then power the whole thing and compare to the motor baseline (Phase 2), then build a mathematical model from the data (Phase 3), and finally use that model to make the actuator behave like a spring you can tune (Phase 4). Each phase gives you the knowledge you need for the next one.

---

## The Concepts You'll Need (As They Come Up)

This section is a reference. Each concept is explained the first time it matters in the campaign, but they're all collected here so you can jump back.

---

### $I_q$ — The Current That Makes Torque

Your motor is a 3-phase brushless DC motor. Three sets of coils, energized in a rotating pattern to spin the rotor. The ODrive's job is to manage this — it runs a control algorithm called **Field-Oriented Control (FOC)** at 8,000 times per second.

FOC breaks the motor's electrical activity into two components:

- **$I_q$** (quadrature current) — the current component that produces torque. This is the useful one. When $I_q$ goes up, the motor pushes harder.
- **$I_d$** (direct current) — the current component aligned with the rotor magnets. In normal operation this should be ~0. It doesn't produce torque — it's wasted energy. (Some advanced drives use $I_d$ for field weakening at high speeds, but ignore that for now.)

**Why you care:** $I_q$ is your torque sensor. You don't have a load cell or torque transducer, but the ODrive tells you exactly how much torque-producing current is flowing. Multiply by $K_t$ and you have torque. This is how you measure friction, cogging, backdriving resistance — everything.

**Analogy:** Think of $I_q$ like a force gauge built into the motor. The ODrive is constantly measuring it whether you ask or not. Your job is to record it and convert it to torque.

---

### $K_t$ — The Torque Constant

$K_t$ converts between current and torque:

$$\tau = K_t \times I_q$$

For your motor (D6374-150KV), the theoretical value is:

$$K_t = \frac{8.27}{K_V} = \frac{8.27}{150} = 0.0551 \text{ Nm/A}$$

**Where the 8.27 comes from:** It's a constant that falls out of motor physics. $K_V$ (the speed constant, in RPM/volt) and $K_t$ (the torque constant, in Nm/A) are inversely related. A motor that spins fast per volt (high $K_V$) produces less torque per amp (low $K_t$), and vice versa. The 8.27 factor handles the unit conversion between RPM and rad/s.

**Why T-009 exists:** Every torque number in this entire campaign comes from $\tau = K_t \times I_q$. If your $K_t$ is wrong, every number downstream is wrong. T-009 is a 5-minute sanity check: spin the motor slowly with no load, read $I_q$, and confirm it's small (just overcoming internal friction). If $I_q$ is huge at low speed with no load, something is misconfigured before you even start.

---

### Cogging Torque — The Motor's Own Bumpiness

Inside the motor, permanent magnets on the rotor pass by iron teeth on the stator. Even with no current flowing, the magnets "prefer" certain angular positions — they snap to alignment with the teeth. This creates a periodic resistance to rotation called **cogging torque**.

**What it feels like:** If you spin the motor shaft slowly by hand with nothing connected, you'll feel gentle bumps — that's cogging. It's small but it's there.

**Why you measure it (T-010):** Later, when you add the gearbox and spin the whole thing, you'll feel bumps too. Are those bumps from the motor cogging, or from the gearbox gears meshing? You can't tell unless you already know what the motor does by itself. Phase 0 establishes this baseline so you can separate motor effects from gearbox effects.

**What it looks like in data:** Plot $I_q$ vs motor angle during a slow constant-speed spin. You'll see a periodic wave — the current rises and falls as the motor fights through each cogging position. The period of this wave tells you the cogging frequency (related to the number of magnets and stator teeth).

---

### Friction: Coulomb + Viscous — Why Things Resist Spinning

When you spin any mechanism, friction resists the motion. For motors and gearboxes, friction has two main components:

**Coulomb friction ($\tau_c$):** A constant resistance that doesn't depend on speed. It takes the same force to overcome whether you're spinning slowly or quickly. This comes from bearings, seals, gear teeth sliding against each other. Think of it as "the force to get things moving."

**Viscous friction ($b \cdot \omega$):** Resistance that increases with speed. The faster you spin, the harder it pushes back. This comes from lubricant shear, air resistance, and eddy currents in the motor. Think of it as "drag."

**The model:**

$$\tau_f = \tau_c + b\omega$$

- $\tau_c$ = Coulomb friction (Nm) — the y-intercept on a friction vs speed plot
- $b$ = viscous friction coefficient (Nm-s/rad) — the slope
- $\omega$ = angular velocity (rad/s)

**What T-011 does:** You spin the motor at several constant speeds, read $I_q$ at each, and compute friction torque. Plot it. If the model is right, you get a roughly straight line. The intercept is Coulomb friction, the slope is viscous friction. You now have a simple equation that predicts motor friction at any speed.

**Why the baseline matters:** In Phase 2, you'll do the same test with the gearbox attached (T-006). The difference between the two curves IS the gearbox's friction contribution. Motor friction doesn't disappear when you add the gearbox — it's still there underneath. You need to subtract it to isolate what the gearbox adds.

---

### Step Response — How Fast Does It React?

A **step response** is the simplest dynamics test: you command the system to jump to a new position and watch what happens.

**Analogy:** Imagine poking a spring-loaded door. It swings, overshoots, swings back, and eventually settles. How fast it swings (rise time), how far past the target it goes (overshoot), and how long until it stops wiggling (settling time) — these tell you about the system's dynamics.

Your actuator does the same thing. Command "go to position X" and log what happens:

- **Rise time ($t_r$):** How long to get from 10% to 90% of the way there. Faster = more responsive.
- **Overshoot (%):** How far past the target it goes. More overshoot = more oscillatory.
- **Settling time ($t_s$):** How long until it stays within 2% of the target. Shorter = better damped.
- **Steady-state error:** Does it land exactly on target, or is it off? If off, backlash or friction is eating into positioning accuracy.

**Why T-014 (motor alone) before T-007 (motor + gearbox):** Same logic as friction. The motor has its own step response. When you add the gearbox, the step response changes — more inertia slows it down, backlash adds oscillation, friction changes the damping. By comparing the two plots side by side, you can see exactly what the gearbox costs in dynamic performance.

---

## Phase 0: Motor Alone — "What Does the Motor Do By Itself?"

**The point:** Establish a baseline for everything. Every test in later phases will be compared against these numbers.

**What you're actually doing:** Take the gearbox off. It's just the motor, encoder, and ODrive on the table. Run four tests:

1. **T-009 ($K_t$ check):** Spin slowly, confirm $I_q$ is small. 5-minute sanity check.
2. **T-010 (cogging profile):** Spin very slowly, log $I_q$ vs angle. Map the motor's bumpiness.
3. **T-011 (friction vs speed):** Spin at 5-6 different speeds, log average $I_q$ at each. Build the friction model.
4. **T-014 (step response):** Command a position jump, log the transient. Capture the motor's dynamics.

**What you walk away with:** Four reference measurements. None of these have pass/fail criteria against your requirements — they're the "before" picture. The "after" picture comes in Phase 2 when the gearbox is attached.

---

## Phase 1: Gearbox Mechanical — "What Can I Measure With My Hands?"

**The point:** Answer the two most critical QDD questions before you even power anything up.

**What you're actually doing:** Gearbox assembled, motor attached but unpowered. Two tests:

1. **T-012 (backlash):** Lock the motor shaft, wiggle the output, measure the angular play. This is R-01 — the single most important number. If backlash is over 0.5 degrees, the gearbox doesn't meet spec.

2. **T-013 (hand backdriving):** With the motor idle, turn the output shaft by hand using a lever arm on a kitchen scale. Read the force. If it takes more than ~0.5 kg at a 200 mm lever (= ~1 Nm), backdrivability fails R-04.

**Why before powering up:** These are the quickest, cheapest measurements and they answer the two requirements that define whether this is a QDD at all. If either fails badly, you know before investing hours in powered tests.

---

## Phase 2: Powered Characterization — "Motor + Gearbox, What Do the Numbers Say?"

**The point:** Repeat the Phase 0 tests with the gearbox attached. Compare. The differences reveal exactly what the gearbox adds.

**What you're actually doing:** Full actuator running. Three tests:

1. **T-006 (friction with gearbox):** Same as T-011 but with gearbox. Subtract the T-011 motor-only curve → the difference is the gearbox's friction. This is your quantitative answer to "how much friction does the gearbox add?"

2. **T-007 (step response with gearbox):** Same as T-014 but with gearbox. Overlay the two plots. Slower rise time = more inertia. More overshoot = backlash or compliance. Different oscillation frequency = the gearbox changed the system's natural frequency.

3. **T-008 (powered backdriving):** Like T-013 but now you have ODrive telemetry. Turn the output by hand while logging $I_q$ and velocity. This gives you a quantitative backdriving torque number with much more detail than the kitchen scale.

**What you walk away with:** A complete before/after picture. "The motor by itself has X friction. With the gearbox, it has Y friction. The gearbox adds Y-X." Same for dynamics. These overlay plots are portfolio-grade figures.

---

## Phase 3: System ID & Dynamics — "What's the Math Behind This System?"

This is where it gets more abstract, but the core idea is practical: **you're building a mathematical model of your actuator so you can design controllers for it.**

---

### Transfer Function — The System's "Personality Equation"

In control theory, a **transfer function** $G(s)$ describes how a system converts input to output. For your actuator:

- **Input:** torque command (Nm)
- **Output:** position or velocity

The transfer function captures everything about the system's behavior — its inertia, its friction, its springiness — in one equation. If you know $G(s)$, you can predict how the system will respond to any input without actually running it.

**Your actuator's transfer function** (simplified, ignoring the electrical dynamics that the ODrive handles internally):

$$G(s) = \frac{1}{Js^2 + bs}$$

**What each piece means:**

- **$J$** = moment of inertia (kg-m$^2$). How hard is it to accelerate rotationally? Heavier flywheel = bigger $J$ = sluggish response. Your gearbox adds reflected inertia: the motor "feels" the gearbox load multiplied by $N^2$ (gear ratio squared = 25).

- **$b$** = viscous friction coefficient (Nm-s/rad). The same $b$ from your friction model. It's the speed-dependent drag.

- **$s$** = the Laplace variable. Don't overthink this. It's a math trick that converts differential equations (hard) into algebra (easier). $s$ basically means "derivative" — $s^2$ means second derivative (acceleration), $s$ means first derivative (velocity).

- **$Js^2$** = "inertia resists acceleration." To speed up a mass, you need force proportional to acceleration.

- **$bs$** = "friction resists velocity." The faster you go, the more drag.

- **The whole thing = $\frac{1}{Js^2 + bs}$** = "for a given torque input, here's how the position responds, accounting for inertia and friction."

**Physical analogy:** Imagine pushing a heavy cart on a slightly sticky floor. $J$ is how heavy the cart is (hard to accelerate), $b$ is how sticky the floor is (drag at speed). The transfer function describes the cart's response to a push — it tells you the cart's complete personality.

---

### System Identification — Finding $G(s)$ From Real Data

In a textbook, you're given $G(s)$. In reality, nobody hands it to you. You have to measure it. That's what **system identification** means.

**What T-015 does:** You already measured $b$ in T-011 (friction vs speed). Now you need $J$ (inertia).

The method is direct:
1. Put ODrive in torque control mode — you command a torque, the motor just pushes with that force. No position or velocity control loop fighting you.
2. Apply a known constant torque (e.g., 0.5 Nm).
3. The motor accelerates. Log velocity vs time.
4. From Newton's rotational law: $\tau = J \cdot \alpha$ → $J = \tau / \alpha$, where $\alpha$ is angular acceleration (the slope of the velocity-vs-time curve).

You now have both $J$ and $b$. Plug them into $G(s) = \frac{1}{Js^2 + bs}$ and you have your plant model — derived from YOUR data, not a textbook.

**Do it twice:** Motor alone → get $J_{motor}$. Motor + gearbox → get $J_{total}$. The difference tells you how much inertia the gearbox reflects to the motor.

---

### Bode Plot — The System's Frequency Report Card

This is the concept that trips people up most, so let's take it slow.

#### The Core Question

Your actuator can track commands. But *how fast* can those commands change before the actuator can't keep up?

If you command "go back and forth slowly" (say, 1 cycle per second), the actuator follows perfectly. If you command "go back and forth at 100 cycles per second," the actuator can't keep up — it's too heavy, too much friction, too much inertia. Somewhere in between, there's a crossover where it starts falling behind. That crossover is the **bandwidth**, and it's the single most important performance number for an actuator.

#### What a Bode Plot Shows

A Bode plot has two graphs stacked vertically, both with **frequency** on the x-axis (log scale, in Hz or rad/s):

**Top graph — Magnitude (Gain):**
- Y-axis: how much of the commanded motion actually shows up at the output, in decibels (dB).
- At low frequencies (slow commands): gain is high — the actuator tracks well. The output matches the input.
- At high frequencies (fast commands): gain drops off — the actuator can't keep up. The output is smaller than the input.
- **The -3 dB point** is the bandwidth. Below this frequency, the system is "good enough." Above it, tracking degrades rapidly.

**Bottom graph — Phase:**
- Y-axis: how much the output *lags behind* the input, in degrees.
- At low frequencies: phase lag is small. The output is nearly in sync with the input.
- At high frequencies: phase lag grows. The output is delayed — it's chasing the input but always behind.
- At -180 degrees phase lag, the output is doing the exact opposite of the input. If the system still has gain at this point, you get instability (oscillation, runaway).

#### Physical Intuition

**Analogy:** Imagine holding a heavy weight on a rubber band and moving your hand up and down.

- **Slowly (low frequency):** The weight follows your hand perfectly. Gain = 1, phase lag = 0.
- **Medium speed:** The weight follows but lags behind a bit, and doesn't quite reach as high as your hand. Gain < 1, some phase lag.
- **Very fast:** The weight barely moves while your hand is going crazy. Gain is very small, phase lag is large.

**The rubber band is friction + compliance. The weight is inertia.** Your actuator works the same way — the motor's inertia and the gearbox's friction determine where the crossover happens.

#### Why the Gearbox Hurts Bandwidth

Adding a gearbox increases reflected inertia (by $N^2 = 25$) and adds friction. Both of these push the bandwidth lower — the system can't respond as quickly to fast commands. This is the fundamental trade-off of gearing: you gain torque but lose speed and responsiveness.

**The killer comparison:** Do the Bode plot for motor alone, then motor + gearbox. Overlay them. The motor-alone curve will have higher bandwidth. The gap between the two curves shows exactly what the gearbox costs in responsiveness. This is why QDDs use low gear ratios (5:1) instead of high ones (50:1 or 100:1 like industrial gearboxes) — they sacrifice some torque multiplication to preserve bandwidth.

#### What T-016 Does

You feed the actuator a sinusoidal (back-and-forth) torque command and sweep the frequency from slow to fast. At each frequency, you measure how much the output actually moves (gain) and how far behind it is (phase). Plot both. That's the Bode plot.

**Two ways to do this:**
- **Chirp:** One continuous sweep from low to high frequency. Faster, but noisier.
- **Sine dwell:** One frequency at a time, hold for several cycles, move to the next. Cleaner data, takes longer.

#### Validating Your Model

Here's where it all connects: you built a transfer function $G(s)$ in T-015 from step response data. That $G(s)$ predicts what the Bode plot *should* look like. Now you actually measure the Bode plot. If the prediction matches the measurement, your model is validated. If it doesn't, the disagreement tells you what the model is missing (backlash? PLA compliance? something else?).

This is the difference between "I found a transfer function in a textbook" and "I derived a model from experimental data and validated it against frequency response measurements." That's what makes it impressive.

---

### Phase Margin & Gain Margin — "How Close to Instability?"

These come from the Bode plot and tell you how robust your system is:

- **Gain margin:** How much you could increase the gain (amplification) before the system goes unstable. Measured at the frequency where phase = -180 degrees.
- **Phase margin:** How much additional phase lag the system could tolerate before going unstable. Measured at the frequency where gain = 0 dB (1:1 tracking).

**Analogy:** If you're driving on a mountain road, phase margin is how far you are from the edge. More margin = safer. A system with 10 degrees of phase margin works but is twitchy and fragile. 45+ degrees is comfortable.

You don't need to compute these formally for the portfolio, but noting them shows you understand stability.

---

## Phase 4: Impedance Control — "Can It Feel Like a Spring?"

This is the whole point of building a QDD. Everything before this was building toward this moment.

---

### What Impedance Control Actually Is

A normal gearbox is a **position device.** You command an angle, it goes there and holds rigid. If something pushes on it, it fights back with all available torque to maintain position. This is great for a CNC machine. It's terrible for a robot that needs to interact with people or unknown environments — it can't "feel" what it's touching, and it'll crush anything it doesn't expect.

**Impedance control** makes the actuator behave like a **programmable spring-damper** instead of a rigid positioner:

$$\tau_{cmd} = -K(\theta - \theta_0) - B\dot{\theta}$$

- $K$ = virtual stiffness (Nm/rad) — how strongly it pushes back toward the setpoint. **You choose this.**
- $B$ = virtual damping (Nm-s/rad) — how much it resists velocity. **You choose this.**
- $\theta_0$ = equilibrium position — where the "spring" is centered
- $\theta$ = current position (from encoder)
- $\dot{\theta}$ = current velocity (from encoder)

**What this means physically:** Push the output shaft away from center. The actuator pushes back proportionally to how far you displaced it ($K$ term) and how fast you moved it ($B$ term). Let go, and it returns to center like a spring. Increase $K$ and it feels stiffer. Decrease $K$ and it feels soft and compliant.

**Why QDDs can do this and regular gearboxes can't:** Impedance control requires the actuator to *feel* external forces. In a high-ratio gearbox (50:1, 100:1), friction and inertia mask external forces — the motor can't sense what's happening at the output. In a QDD (5:1), the low ratio means forces at the output are felt at the motor as relatively large signals. Low friction and low backlash preserve the signal. That's why backdrivability (R-04) and backlash (R-01) are the top requirements — they're prerequisites for impedance control.

---

### Tier A vs Tier B — Two Ways to Get There

**Tier A (T-017): Use ODrive's built-in PID as a spring.**

ODrive's position controller is already a spring-damper in disguise:
- `pos_gain` acts as stiffness $K$
- `vel_gain` acts as damping $B$
- `input_pos` sets the equilibrium position

Set these to low values, command a position, and push the shaft — it behaves like a spring. The control law runs at 8 kHz inside the ODrive, so there's no jitter or delay. This is the most robust approach.

**Tier B (T-018): Compute the impedance law in Python.**

You write the spring-damper equation yourself in a Python loop:
1. Read position and velocity from ODrive
2. Compute $\tau = -K(\theta - \theta_0) - B\dot{\theta}$
3. Send that torque command to ODrive
4. Repeat ~200 times per second

This is "real" impedance control — you have full control over the math. But your Python loop runs at ~200 Hz over USB, not 8 kHz internally. That jitter and delay can cause problems, especially at high stiffness. Start overdamped and low-stiffness.

---

### What Backlash Does to Impedance Control

Remember backlash — the angular play in the gear teeth? Here's where it actually matters:

Near the equilibrium position, when the error is smaller than the backlash deadzone, the gear teeth aren't in contact. The spring law says "push back toward center" but the gears are floating in the gap. This causes **limit cycling** — the controller hunts back and forth across the deadzone, chattering.

**Mitigation:** Add a small constant torque bias to keep the teeth engaged on one flank. Or add a deadband — if the error is smaller than the backlash, command zero torque and accept the dead zone.

This is why measuring backlash (T-012) matters for impedance control, not just for positioning accuracy.

---

### T-019: The Portfolio Payoff

Build a Python GUI with sliders for $K$ and $B$. Run the impedance controller with live-adjustable parameters. Record video of someone pushing the output shaft while adjusting stiffness from "limp noodle" to "rigid joint" in real time.

This is the hero content. It demonstrates: "I designed a QDD actuator, characterized it, identified the plant model, and implemented variable impedance control — the defining capability of quasi-direct-drive actuators."

---

## How It All Connects — The Logic Chain

```
Phase 0 (motor baseline)
  │
  │  "Here's what the motor does alone — friction, cogging, step response"
  │
  ├──► Phase 1 (mechanical checks)
  │      │
  │      │  "Does the gearbox pass the two critical QDD requirements?"
  │      │  Backlash ≤ 0.5° (R-01), Backdrive < 1 Nm (R-04)
  │      │
  │      ▼
  │    Phase 2 (powered comparison)
  │      │
  │      │  "Same tests as Phase 0, but with gearbox"
  │      │  Subtract Phase 0 → isolate gearbox effects
  │      │  Portfolio figures: friction overlay, step response overlay
  │      │
  │      ▼
  │    Phase 3 (system ID)
  │      │
  │      │  "Build the math model from real data"
  │      │  Fit J and b → transfer function G(s)
  │      │  Validate with Bode plot → does prediction match measurement?
  │      │  Key output: bandwidth (how responsive is the actuator?)
  │      │
  │      ▼
  │    Phase 4 (impedance control)
  │         │
  │         │  "Use the model to make it behave like a spring"
  │         │  Tier A (ODrive PID) → Tier B (Python torque loop)
  │         │  Demo: variable stiffness with GUI sliders
  │         │  This is the whole point of a QDD
  │         ▼
  │       Portfolio: "I characterized an actuator, identified the plant,
  │                   and implemented impedance control"
  │
  ▼
Phase 5 (later): torque capacity, thermal, durability, efficiency
  "Can it handle the load? For how long?"
```

---

## Quick Glossary

| Term | Plain English | Units |
|------|--------------|-------|
| $I_q$ | Torque-producing current (your torque sensor) | Amps (A) |
| $I_d$ | Non-torque current (should be ~0) | Amps (A) |
| $K_t$ | Converts current to torque: $\tau = K_t I_q$ | Nm/A |
| $K_V$ | Motor speed rating (inversely related to $K_t$) | RPM/V |
| $\tau$ | Torque | Nm |
| $\omega$ | Angular velocity | rad/s |
| $\tau_c$ | Coulomb friction (constant, speed-independent) | Nm |
| $b$ | Viscous friction coefficient (scales with speed) | Nm-s/rad |
| $J$ | Moment of inertia (rotational mass) | kg-m$^2$ |
| $G(s)$ | Transfer function (system's input-output relationship) | — |
| $s$ | Laplace variable (math shorthand for "derivative") | — |
| Bode plot | Gain + phase vs frequency (the system's frequency report card) | dB, degrees vs Hz |
| Bandwidth | Highest frequency the system can track well (-3 dB point) | Hz |
| Phase margin | How far from instability (more = safer) | degrees |
| $K$ | Virtual stiffness (impedance control) | Nm/rad |
| $B$ | Virtual damping (impedance control) | Nm-s/rad |
| FOC | Field-Oriented Control — the algorithm ODrive runs at 8 kHz | — |
| Chirp | Swept sine wave — frequency increases over time | — |
