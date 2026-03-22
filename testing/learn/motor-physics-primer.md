# Motor Physics Primer — The Stuff You Need to Know Before Testing

> **What this is:** The foundational physics connecting electricity, torque, speed, and heat in your BLDC motor. Written because you realized you don't fully understand *why* things are related, and that matters before running tests.
>
> **How to read this:** Sequentially. Each section builds on the last. The goal is that by the end, when someone asks "is current proportional to torque?" or "does heat scale with speed?", you can answer confidently and explain *why*.

---

## The Big Picture: Three Domains, Connected

Your actuator lives at the intersection of three physical domains. Everything you'll ever measure or care about falls into one of them, and the interesting stuff happens at the boundaries where they connect.

```
    ELECTRICAL               MECHANICAL              THERMAL
    ──────────               ──────────              ───────
    Voltage (V)              Torque (τ)              Temperature (T)
    Current (I)              Speed (ω)               Heat flow (Q)
    Resistance (R)           Inertia (J)             Thermal resistance (Rth)
    Inductance (L)           Friction (b, τc)        Thermal capacitance (Cth)
    Power (V·I)              Power (τ·ω)             Power dissipated (Ploss)
         │                        │                        │
         │    ┌───────────────────┘                        │
         │    │  τ = Kt · Iq                               │
         │    │  V_bemf = Ke · ω                           │
         ▼    ▼                                            │
      ELECTROMECHANICAL ──── losses ──────────────────► HEATING
      (the motor converts     (not all power              (waste heat
       between these two)      makes it through)           must go somewhere)
```

**The key insight:** The motor is an energy converter. Electrical power goes in, mechanical power comes out, and the difference becomes heat. Understanding this energy flow is the foundation for everything.

---

## 1. Current and Torque — Are They Proportional?

**Short answer:** Yes, through FOC. $\tau = K_t \cdot I_q$ is linear.

**But you need to understand what that actually means and why.**

### Where torque comes from physically

Your motor has permanent magnets on the rotor and coils of wire (windings) on the stator. When current flows through a winding, it creates a magnetic field. That field interacts with the permanent magnet field and creates a force — the Lorentz force. More current = stronger magnetic field = more force.

This is genuinely a linear relationship at the fundamental physics level. The force on a current-carrying wire in a magnetic field is:

$$F = I \cdot L \cdot B$$

- $I$ = current through the wire
- $L$ = length of wire in the field
- $B$ = magnetic field strength (from the permanent magnets)

$L$ and $B$ are fixed by the motor's geometry and magnets. So force scales linearly with current. Torque is just force times the radius at which it acts, so torque also scales linearly with current.

**That linear scaling factor is $K_t$:**

$$\tau = K_t \cdot I_q$$

$K_t$ bundles up all the geometry ($L$, $B$, radius, number of turns, number of poles) into one constant. For your motor, $K_t = 0.0551$ Nm/A.

### Why $I_q$ specifically, not total current

Your motor has three phase wires, each carrying a different current waveform. The total current flowing is a messy combination of all three. FOC (Field-Oriented Control) is a mathematical transformation that takes those three messy currents and decomposes them into two clean components:

- **$I_q$** — the component that's perpendicular to the rotor magnets. This is the one that creates torque. It's called "quadrature" because it's 90° (a quarter turn) from the magnet axis.
- **$I_d$** — the component aligned with the rotor magnets. This one does NOT create torque. It either strengthens or weakens the magnetic field (field weakening). For normal operation, ODrive sets $I_d = 0$.

**So: total phase current ≠ torque-producing current.** Only $I_q$ matters for torque. ODrive's FOC algorithm extracts $I_q$ for you at 8 kHz. When you read `Iq_measured` from ODrive, that's the real torque-producing current.

### When is $\tau = K_t \cdot I_q$ NOT perfectly linear?

The linear model is very good, but not perfect:

| Effect | What happens | Magnitude |
|--------|-------------|-----------|
| **Magnetic saturation** | At very high currents, the iron in the stator saturates — it can't carry more magnetic flux. $K_t$ effectively drops. | Only matters at extreme currents, well above continuous rating |
| **Temperature** | As windings heat up, resistance changes, which affects the current loop. $K_t$ itself (a magnetic property) is relatively stable until magnets start demagnetizing (~150°C) | Small effect in normal operating range |
| **Cogging** | The torque ripple from magnet-tooth interaction adds a position-dependent disturbance on top of the $K_t \cdot I_q$ signal | Small but measurable — that's what T-010 maps |

**For your purposes:** Treat $\tau = K_t \cdot I_q$ as exact. The nonlinearities are second-order effects that matter for precision robotics, not for your characterization campaign.

### Why this matters for your tests

Your buddy's question was basically: "if current is just proportional to torque, why do we need to verify $K_t$?" The answer is:

1. **The proportionality constant matters.** Every torque number you calculate depends on it. A 10% error in $K_t$ means 10% error in every torque measurement.
2. **You're trusting a nameplate spec.** $K_t = 8.27/K_v = 8.27/150 = 0.0551$ assumes the motor's $K_v$ rating is accurate. Cheap motors have tolerances. The motor could be 145 KV or 155 KV.
3. **The ODrive configuration matters.** If pole pairs are set wrong, or the encoder calibration is off, the FOC won't correctly decompose $I_q$ — you'll get a number, but it won't mean what you think.

**What "pole pairs set wrong" means:** Your motor has permanent magnets arranged around the rotor in alternating north-south pairs. The D6374 likely has 7 pole pairs (14 individual magnets: N-S-N-S-N-S... around the circumference). One full mechanical revolution of the shaft = 7 complete electrical cycles inside the motor.

FOC needs to know exactly where the magnets are at every instant so it can aim the current at the right angle — specifically 90° from the magnet axis, which is where you get maximum torque (that's what $I_q$ is). It figures out magnet position by combining the encoder angle with the pole pair count: if the encoder says the shaft is at 30° mechanical, and there are 7 pole pairs, the electrical angle is $30° \times 7 = 210°$ electrical.

If you tell ODrive the motor has 8 pole pairs but it actually has 7, the math is out of sync. ODrive thinks the magnets are at one angle, but they're actually somewhere else. The current it labels "$I_q$" is no longer aimed 90° from the magnets — part of it makes torque, part of it produces useless $I_d$, and the proportions shift as the motor rotates. Result: erratic torque, high current for low output, and the $I_q$ reading doesn't correspond to actual torque anymore.

ODrive detects pole pairs automatically during its calibration sequence (the motor twitches back and forth when you first set it up). So this shouldn't be an issue if calibration completes successfully — it's mainly a risk if someone manually overrides the motor config.

T-009 is a sanity check for all of this: if you spin with no load and $I_q$ is unreasonably large, one of these things is wrong.

---

## 2. Voltage and Speed — The Other Side of the Motor

### Back-EMF: the motor is also a generator

Here's something that often surprises people: **a motor and a generator are the same device.** When you put current in, you get torque out (motor). When you spin the shaft, you get voltage out (generator). Both happen simultaneously.

When the motor is spinning, the magnets passing the coils induce a voltage called **back-EMF** (electromotive force):

$$V_{bemf} = K_e \cdot \omega$$

- $K_e$ = back-EMF constant (V·s/rad)
- $\omega$ = angular velocity (rad/s)

**Here's the beautiful part:** $K_e = K_t$ (in SI units). They're the same physical constant, just measured from different directions. The motor's ability to convert current to torque is identical to its ability to convert speed to voltage. This falls out of energy conservation.

$$K_t = K_e = \frac{8.27}{K_v} = 0.0551 \text{ (Nm/A or V·s/rad)}$$

### Why back-EMF limits top speed

The ODrive can only push current into the motor if the supply voltage exceeds the back-EMF. Think of it like trying to push water into a pipe that already has pressure — you need more pressure than what's already there.

$$V_{bus} > V_{bemf} + I \cdot R$$

As speed increases, $V_{bemf}$ rises. Eventually it approaches $V_{bus}$ and there's no voltage headroom left to push current through. The motor can't produce torque anymore. This is the speed ceiling.

**Your motor at max speed:**
- At 3000 RPM motor-side (600 RPM output × 5:1): $\omega = 314$ rad/s
- $V_{bemf} = 0.0551 \times 314 = 17.3$ V
- You need at least ~20 V supply to maintain torque at this speed (plus margin for the $IR$ drop)

### The speed-torque tradeoff

At any given supply voltage, there's a tradeoff:

$$V_{bus} = V_{bemf} + I_q \cdot R = K_e \cdot \omega + I_q \cdot R$$

Rearranging:

$$I_q = \frac{V_{bus} - K_e \cdot \omega}{R}$$

- **At zero speed ($\omega = 0$):** All voltage drives current → maximum torque (stall torque)
- **At max speed:** All voltage fights back-EMF → zero current → zero torque (no-load speed)
- **In between:** It's a linear tradeoff

This gives the classic **motor speed-torque curve** — a straight line from stall torque (high torque, zero speed) to no-load speed (zero torque, max speed). Every operating point lives on or below this line.

---

## 3. Power — Where Energy Goes

### Electrical power in

$$P_{elec} = V \cdot I$$

More precisely, the power that does useful work:

$$P_{elec,useful} = V_{bemf} \cdot I_q = (K_e \cdot \omega) \cdot I_q$$

### Mechanical power out

$$P_{mech} = \tau \cdot \omega = (K_t \cdot I_q) \cdot \omega$$

Since $K_t = K_e$, these are the same expression. **The useful electrical power equals the mechanical power** — this is energy conservation. The motor converts between them perfectly (in the ideal case).

### Where power is lost

In reality, not all electrical power becomes mechanical power. The losses:

| Loss type | Equation | Depends on | Where the heat goes |
|-----------|----------|------------|-------------------|
| **Copper loss ($I^2R$)** | $P_{cu} = I_q^2 \cdot R$ | Current² | Windings (hottest point) |
| **Iron/core loss** | $P_{fe} \approx k \cdot \omega^{1.5\text{–}2}$ | Speed | Stator laminations |
| **Friction loss** | $P_{fric} = \tau_f \cdot \omega$ | Speed | Bearings, gears |
| **Windage** | Small | Speed² | Air |

**The total power balance:**

$$P_{electrical} = P_{mechanical} + P_{copper} + P_{iron} + P_{friction}$$

$$V \cdot I = \tau_{out} \cdot \omega + I_q^2 R + P_{iron} + \tau_f \cdot \omega$$

This is conservation of energy. Every watt goes somewhere. If you measure the input and the output, the difference is losses. If you know the losses, you know efficiency:

$$\eta = \frac{P_{mechanical}}{P_{electrical}} = \frac{\tau_{out} \cdot \omega}{V \cdot I}$$

---

## 4. Heat — What Actually Generates It?

This is the question you had: is heat proportional to velocity? proportional to current? The answer is **it depends on which loss mechanism you're talking about.**

### Copper loss: proportional to CURRENT SQUARED

$$P_{cu} = I_q^2 \cdot R$$

This is the **dominant heat source** in most motor operating conditions. It's the heat generated by pushing current through a resistive wire — the same physics as a toaster.

Key things to notice:
- **Squared relationship.** Double the current → 4× the heat. This is why continuous torque ratings exist — high current is thermally brutal.
- **Independent of speed.** A stalled motor (zero speed) at full current generates maximum copper loss with zero mechanical output. 100% of the power becomes heat. This is the worst thermal case.
- **Depends on winding resistance.** $R$ increases with temperature (~0.4%/°C for copper), so hot motors generate even more heat — a positive feedback loop that can lead to thermal runaway if not managed.

### Iron loss: proportional to SPEED

$$P_{fe} \approx k_1 \cdot f + k_2 \cdot f^2$$

where $f$ is the electrical frequency (proportional to speed).

Iron losses come from the changing magnetic field in the stator:
- **Hysteresis loss** ($k_1 \cdot f$): energy lost to repeatedly magnetizing and demagnetizing the iron. Scales with frequency (speed).
- **Eddy current loss** ($k_2 \cdot f^2$): currents induced in the iron by the changing field. Scales with frequency squared.

**For your motor:** Iron losses are smaller than copper losses at low-to-moderate speeds. They become significant at high speeds. You'll see this as: the motor gets warm even at low current if spinning fast.

### Friction loss: proportional to SPEED

$$P_{fric} = \tau_f \cdot \omega = (\tau_c + b\omega) \cdot \omega = \tau_c \cdot \omega + b\omega^2$$

Friction converts mechanical energy to heat. It's in the bearings, the gear mesh, and the seals.

### Putting it all together: the thermal picture

| Operating condition | Dominant heat source | Why |
|--------------------|---------------------|-----|
| **High torque, low speed** (stall or near-stall) | $I^2R$ copper loss | Massive current, barely moving — nearly all power is heat |
| **Low torque, high speed** | Iron loss + friction | Low current means low $I^2R$, but high speed means high iron/friction losses |
| **High torque, high speed** | All of them | This is peak power, peak thermal stress |
| **Low torque, low speed** | Very little heat | The easy case — everything is cool |

**The answer to "is heat proportional to speed?":** No, not directly. The dominant heat source ($I^2R$) doesn't depend on speed at all — it depends on current (which means torque). But there ARE speed-dependent losses (iron, friction) that add heat at high RPM even with low torque. The full picture is: **heat comes from both current and speed, through different mechanisms, and $I^2R$ usually dominates.**

### Why this matters for your QDD

Your 3D-printed PLA+ housing is a terrible heat conductor compared to aluminum. The thermal resistance from winding to ambient is much higher than a commercial motor. This means:

1. Your continuous torque rating is **lower** than the motor's datasheet spec
2. The motor will reach thermal limits **faster**
3. Heat management is a **real design constraint**, not a footnote

The thermal test in your campaign (eventually) needs to answer: "how much continuous torque can I actually sustain before the housing hits 80°C?"

---

## 5. The Motor Equations — All in One Place

Here are the fundamental equations and how they connect. Every test in your campaign measures or depends on one of these.

### The electrical equation (what happens in the wires)

$$V = I_q \cdot R + L \cdot \frac{dI_q}{dt} + K_e \cdot \omega$$

In words: supply voltage = resistive drop + inductive rise + back-EMF

- At steady state ($dI/dt = 0$): $V = I_q \cdot R + K_e \cdot \omega$
- The ODrive's current controller handles this equation internally at 8 kHz. You command $I_q$, it figures out the voltage.

### The mechanical equation (what happens at the shaft)

$$\tau_{motor} = J \cdot \dot{\omega} + b \cdot \omega + \tau_c \cdot \text{sign}(\omega) + \tau_{load}$$

In words: motor torque = inertia × acceleration + viscous friction + Coulomb friction + external load

- $K_t \cdot I_q$ is on the left side (motor torque produced)
- Everything on the right side is where that torque goes

Rearranging to solve for acceleration:

$$\dot{\omega} = \frac{K_t \cdot I_q - b\omega - \tau_c \cdot \text{sign}(\omega) - \tau_{load}}{J}$$

**This is Newton's second law for rotation.** If you know current, friction, and load, you can predict acceleration. This is the equation your transfer function $G(s)$ comes from.

### The thermal equation (what happens to temperature)

$$C_{th} \cdot \frac{dT}{dt} = P_{loss} - \frac{T - T_{amb}}{R_{th}}$$

In words: temperature rises when heat generation exceeds heat dissipation

- $C_{th}$ = thermal mass (how much energy it takes to raise temperature)
- $P_{loss}$ = total heat generated ($I^2R$ + iron + friction)
- $R_{th}$ = thermal resistance (how hard it is for heat to escape)
- At steady state: $T_{final} = T_{amb} + P_{loss} \cdot R_{th}$

**The steady-state result is powerful:** If you know $R_{th}$ (measure it once), you can predict the final temperature for any power dissipation level. This is how continuous ratings are calculated.

### The energy equation (the connection between all three)

$$\underbrace{V \cdot I}_{P_{elec}} = \underbrace{\tau \cdot \omega}_{P_{mech}} + \underbrace{I_q^2 R}_{P_{copper}} + \underbrace{P_{iron} + P_{friction}}_{P_{other losses}}$$

**Every watt is accounted for.** This is the master equation. Efficiency is $P_{mech} / P_{elec}$.

---

## 6. How the Gearbox Changes Everything

When you bolt the gearbox onto the motor, every parameter transforms through the gear ratio $N$ (= 5 for your QDD).

### Torque multiplication

$$\tau_{out} = \tau_{motor} \cdot N \cdot \eta_{gearbox}$$

The gearbox multiplies torque by $N$, minus whatever is lost to friction ($\eta$). This is the whole point of the gearbox.

### Speed reduction

$$\omega_{out} = \frac{\omega_{motor}}{N}$$

Speed divides by $N$. The motor spins 5× faster than the output.

### Reflected inertia (this one surprises people)

$$J_{reflected} = J_{load} \cdot N^2$$

The motor "feels" the output-side inertia multiplied by $N^2 = 25$. This is NOT $N$, it's $N$ squared.

**Why squared?** Think about it from energy. Kinetic energy is $\frac{1}{2}J\omega^2$. If you spin the motor 5× faster than the load, the motor's $\omega$ is 5× bigger, and energy goes as $\omega^2$, so the motor has to supply 25× as much energy per unit of load inertia. The "effective" inertia the motor sees is 25× the actual load inertia.

**What this means for your QDD:** Even a small gearbox inertia becomes significant when reflected to the motor side. This is why T-015 (system ID) measures $J$ with and without the gearbox — the difference reveals the reflected inertia, and it directly affects bandwidth.

### Reflected friction

$$\tau_{f,reflected} = \frac{\tau_{f,gearbox}}{N}$$

Gearbox friction, when felt at the motor side, is divided by $N$. But at the output side, it's the raw gearbox friction. The requirement R-04 ($\tau_f < 1$ Nm) is measured at the output.

### The bandwidth penalty

Adding the gearbox increases the total reflected inertia ($J_{motor} + N^2 \cdot J_{gearbox+load}$) and adds friction. Both reduce bandwidth — the system responds more sluggishly to fast commands. This is the QDD tradeoff: low gear ratio (5:1) preserves some bandwidth, unlike a 50:1 gearbox that would be very sluggish.

---

## 7. Connecting This Back to Your Tests

Now you can see why each Phase 0 test exists and what physics it probes:

### T-009: $K_t$ sanity check

**Physics being probed:** $\tau = K_t \cdot I_q$

**What you're really asking:** "Is the proportionality constant between current and torque configured correctly?"

**Why it matters:** Every torque number in every subsequent test depends on this being right. It's the foundation.

**What "pass" looks like:** Motor spinning slowly, no load → $I_q$ is small (just overcoming internal friction). If $K_t$ were wrong (say ODrive thinks it's a different motor), $I_q$ would be unreasonably large or the motor would behave erratically.

### T-010: Cogging profile

**Physics being probed:** Magnetic interaction between permanent magnets and stator iron teeth

**What you're really asking:** "What does the motor's torque ripple look like as a function of angle?"

**Why it matters:** Two reasons:
1. **Baseline separation.** In Phase 2, bumps in the torque signal could be motor cogging OR gearbox tooth mesh effects. You need the motor-only profile to tell them apart.
2. **Force transparency.** In impedance control, the motor $I_q$ is your force sensor. Cogging is a disturbance that looks like an external force. If you know the cogging map, you can cancel it with feedforward compensation.

### T-011: Friction vs speed

**Physics being probed:** $\tau_f = \tau_c + b\omega$ (Coulomb + viscous friction model)

**What you're really asking:** "How much torque does the motor waste fighting its own friction, and how does that change with speed?"

**Why it matters:**
1. **Efficiency prediction.** Friction is a direct power loss: $P_{fric} = \tau_f \cdot \omega$. Knowing $\tau_c$ and $b$ lets you predict friction loss at any operating point.
2. **Phase 2 subtraction.** When you add the gearbox and repeat this test (T-006), the increase in friction IS the gearbox's contribution. Without the motor-only baseline, you can't isolate it.
3. **Transfer function.** The viscous coefficient $b$ appears directly in the plant model $G(s) = \frac{1}{Js^2 + bs}$. You need it for system ID and controller design.
4. **Backdrivability.** The friction torque at the output (motor friction + gearbox friction) is what someone feels when they push on the actuator. It's the core QDD metric.

**Your buddy's question answered:** "Why measure friction at multiple speeds? Isn't one measurement enough?"

No — because friction has TWO components. One measurement gives you one equation with two unknowns ($\tau_c$ and $b$). You need at least two speeds to solve for both. Doing 5–6 speeds lets you fit a line and see if the model is actually linear or if something more complex is going on.

---

## 8. Common Misconceptions (Things That Tripped You Up)

| Misconception | Reality |
|--------------|---------|
| "Current is proportional to torque" | **Correct — but specifically $I_q$, not total phase current.** FOC extracts the torque-producing component. Total current includes $I_d$ (which should be ~0) and reactive components. |
| "Heat is proportional to speed" | **Partially wrong.** The dominant heat source ($I^2R$) depends on current, not speed. Speed-dependent losses (iron, friction) exist but are usually secondary. A stalled motor at high current generates MORE heat than a spinning motor at low current. |
| "More speed = more torque needed" | **Only if accelerating or fighting friction.** At constant speed with no load, you only need enough torque to overcome friction. Speed itself doesn't require torque — acceleration does ($\tau = J\dot{\omega}$). |
| "The gearbox multiplies torque by $N$" | **Almost.** It multiplies by $N \cdot \eta$, where $\eta < 1$. Friction steals some of the multiplication. If $\eta = 0.9$ and $N = 5$, effective multiplication is 4.5. |
| "$K_t$ and $K_v$ are different properties" | **They're the same property measured from different directions.** $K_t$ (Nm/A) = $K_e$ (V·s/rad). The motor's ability to make torque from current is identical to its ability to make voltage from speed. |
| "The motor can produce any torque at any speed" | **No — there's a speed-torque curve.** At high speed, back-EMF eats into the available voltage, leaving less headroom to push current. Torque capacity decreases linearly with speed. |
| "Efficiency is constant" | **No — it varies with operating point.** At low speed and low torque, friction dominates → low efficiency. At high speed and high torque, you're closer to the motor's sweet spot → higher efficiency. There's an optimal operating region. |

---

## 9. The Questions You Should Be Able to Answer

After reading this, test yourself. If you can answer these, you've got the fundamentals:

1. If you double $I_q$, what happens to torque? What happens to copper loss?
2. Why does a stalled motor at high current get hotter than a spinning motor at the same current?
3. What's the difference between $I_q$ and total phase current?
4. If you spin the motor shaft by hand with no power applied, why do you feel resistance? Where does the energy go?
5. Why does the gearbox reduce bandwidth? (Hint: $N^2$)
6. If T-011 shows friction is 0.3 Nm at all speeds (flat line, no slope), what does that tell you about the friction model?
7. Your motor is at 3000 RPM and you want more torque. What's limiting you? (Hint: back-EMF)
8. Why can't you just measure friction at one speed and call it done?
9. If the motor $K_v$ is actually 140 instead of 150, is your $K_t$ higher or lower than you think? What does that mean for your torque calculations?
10. Where does the heat go in a 3D-printed housing vs an aluminum one? Why does that matter?

<details>
<summary><b>Answers</b></summary>

1. Torque doubles (linear). Copper loss quadruples ($I^2$ relationship). This is why high torque is thermally expensive.

2. Trick question — at the same current, copper loss ($I^2R$) is the same. But the stalled motor has zero mechanical output, so ALL electrical power is heat. The spinning motor converts some power to useful mechanical work, so less becomes heat. Same $I^2R$ but different total thermal picture.

3. Total phase current is the raw current flowing in each motor wire. $I_q$ is the mathematical component (extracted by FOC) that produces torque. $I_d$ is the component that doesn't produce torque. In normal operation $I_d \approx 0$, so $I_q \approx$ total current magnitude, but they're conceptually different.

4. Back-EMF (generator effect) and cogging. The magnets passing the coils induce voltage and create resistive forces. Eddy currents in the stator also resist motion. The energy goes to heat in the windings and stator iron.

5. Reflected inertia scales as $N^2$. For $N=5$, the motor sees 25× the output-side inertia. Higher inertia = slower acceleration = lower bandwidth. This is the fundamental gearing tradeoff.

6. Pure Coulomb friction ($\tau_c = 0.3$ Nm, $b = 0$). No viscous component — friction doesn't increase with speed. This would be unusual for a motor (usually there's some viscous component from oil, eddy currents). Might indicate dry bearings or dominant mechanical contact friction.

7. Back-EMF. At 3000 RPM, $V_{bemf} = K_e \cdot \omega = 0.0551 \times 314 = 17.3$ V. If your supply is 24 V, you only have ~6.7 V left to push current through the resistance. Current (and therefore torque) is limited by voltage headroom.

8. Because friction has two components: Coulomb ($\tau_c$, constant) and viscous ($b\omega$, speed-dependent). One measurement gives one equation with two unknowns. You need multiple speeds to separate them and fit the model.

9. If $K_v$ is actually 140, then $K_t = 8.27/140 = 0.0591$ Nm/A (higher than the 0.0551 you're using). Your torque calculations would *underestimate* actual torque by ~7%. Every $\tau = K_t \cdot I_q$ result would be 7% low.

10. PLA+ has much higher thermal resistance than aluminum. Heat generated in the windings takes longer to reach the surface and dissipate. The motor reaches thermal limits faster, meaning lower continuous torque rating. This is a real design constraint for your 3D-printed gearbox housing.

</details>

---

## Where to Go From Here

This primer covers the **physics**. For how these concepts connect to your specific tests, see:

- `campaign-walkthrough.md` — what each test does and why, in campaign context
- `testing-fundamentals.md` — the variables table and testing methodology
- `actuator-characterization-guide.md` (in `learning/skill-building/actuator-testing/`) — deeper dive on characterization techniques with Tesla interview relevance

The next time you're in the lab staring at ODrive telemetry, the numbers should make physical sense. If $I_q$ reads 2A at no load, you know that's suspicious (Section 1). If the motor is warm at high speed but low torque, you know it's iron loss (Section 4). If the gearbox makes the step response sluggish, you know it's reflected inertia (Section 6).

That's the goal — not memorizing equations, but having the physical intuition to look at data and know whether it makes sense.
