# Testing Fundamentals — QDD Actuator

> Framework for systematic hardware testing. Individual test procedures live in separate files.

---

## Variables & Nomenclature

Quick reference for every variable you'll encounter across motor characterization, gearbox testing, impedance control, and data analysis.

### Motor & Electrical

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $K_v$ | Velocity constant | RPM/V | Motor speed per volt (no load) | 150 |
| $K_t$ | Torque constant | Nm/A | Torque produced per amp of $I_q$. $K_t = 8.27 / K_v$ | 0.0551 |
| $I_q$ | Quadrature current | A | The torque-producing current component (FOC) | Measured |
| $I_d$ | Direct current | A | Non-torque current component — should be ~0 in normal operation | ~0 |
| $I_{lim}$ | Current limit | A | Max current allowed by controller config | Start at 5, increase |
| $R_{phase}$ | Phase resistance | Ω | Winding resistance per phase — determines $I^2R$ losses | TBD (measure) |
| $L_{phase}$ | Phase inductance | H | Winding inductance per phase — affects current loop tuning | TBD (measure) |
| $V_{bus}$ | Bus voltage | V | DC supply voltage to ODrive | Depends on battery/PSU |
| $\lambda$ / $K_e$ | Back-EMF constant | V·s/rad | Voltage generated per unit speed. Numerically equal to $K_t$ in SI | 0.0551 |

### Torque & Force

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $\tau_m$ | Motor torque | Nm | Torque at motor shaft: $\tau_m = K_t \cdot I_q$ | Measured |
| $\tau_{out}$ | Output torque | Nm | Torque at gearbox output: $\tau_{out} = \tau_m \cdot N \cdot \eta$ | Measured |
| $\tau_{peak}$ | Peak output torque | Nm | Max short-duration output torque | 16 |
| $\tau_{cont}$ | Continuous output torque | Nm | Sustained output torque (thermally limited) | 12 |
| $\tau_f$ | Friction torque | Nm | Resistive torque from gearbox — the QDD transparency metric | < 1.0 (requirement) |
| $\tau_c$ | Coulomb friction | Nm | Speed-independent friction component: $\tau_f = \tau_c + b\omega$ | Measured |
| $F_t$ | Tangential tooth force | N | Force at gear pitch circle — used in stress calcs | Calculated |

### Speed & Position

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $\omega_m$ | Motor angular velocity | rad/s | Motor shaft speed | Measured |
| $\omega_{out}$ | Output angular velocity | rad/s | Gearbox output speed: $\omega_{out} = \omega_m / N$ | Measured |
| $n_m$ | Motor speed | RPM | Motor shaft speed in RPM | Up to 3000 |
| $n_{out}$ | Output speed | RPM | Output speed in RPM | Up to 600 |
| $\theta$ | Angular position | rad or ° | Shaft position from encoder | Measured |
| $\Delta\theta$ | Backlash | ° | Lost motion at output when reversing direction | ≤ 0.5 (requirement) |

### Gearbox Parameters

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $N$ | Gear ratio | — | Output torque multiplier / speed divider | 5:1 |
| $\eta$ | Efficiency | — | Power out / power in (0 to 1) | > 0.90 (requirement) |
| $\phi$ | Pressure angle | ° | Gear tooth geometry angle | 20 |
| $m$ | Module | mm | Tooth size parameter: $m = d/z$ | Per gear set |
| $z$ | Tooth count | — | Number of teeth on a gear | Per gear |
| $b$ (gear) | Face width | mm | Axial width of gear teeth | Per gear |
| $CR$ | Contact ratio | — | Average teeth in mesh — higher = smoother | Calculated |

### Thermal

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $T_w$ | Winding temperature | °C | Hottest point in motor — the thermal limit | < 120 |
| $T_h$ | Housing temperature | °C | Motor/gearbox housing temp | < 80 |
| $T_{amb}$ | Ambient temperature | °C | Room temperature | 25 |
| $R_{th}$ | Thermal resistance | K/W | Temperature rise per watt of heat input | Per path |
| $C_{th}$ | Thermal capacitance | J/K | Heat energy stored per degree of temp rise | Per node |
| $P_{loss}$ | Power loss | W | Heat generated: $P = I_q^2 \cdot R_{phase}$ (copper loss) | Calculated |

### Control & Impedance

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $K_p$ | Proportional gain | — | Position/velocity loop P gain | Tuned |
| $K_i$ | Integral gain | — | Position/velocity loop I gain | Tuned |
| $K_d$ | Derivative gain | — | Position/velocity loop D gain (or velocity P) | Tuned |
| $K_{imp}$ | Impedance stiffness | Nm/rad | Virtual spring constant for impedance control | Tuned |
| $B_{imp}$ | Impedance damping | Nm·s/rad | Virtual damper for impedance control | Tuned |
| $b$ (friction) | Viscous friction coefficient | Nm·s/rad | Speed-dependent friction: $\tau_f = \tau_c + b\omega$ | Measured |
| $f_{loop}$ | Control loop rate | Hz | How fast the control loop runs | 8000 (ODrive internal) |

### Encoder & Measurement

| Symbol | Name | Units | Description | Our Value |
|--------|------|-------|-------------|-----------|
| $CPR$ | Counts per revolution | counts/rev | Encoder resolution | 16384 (14-bit) |
| $\sigma$ | Standard deviation | (varies) | Spread of repeated measurements — quantifies noise/repeatability | Calculated |
| $n$ | Sample count | — | Number of measurements in a test | Per test |

### Key Relationships

$$\tau_m = K_t \cdot I_q \qquad \tau_{out} = \tau_m \cdot N \cdot \eta \qquad K_t = \frac{8.27}{K_v}$$

$$P_{mech} = \tau \cdot \omega \qquad P_{elec} = V \cdot I \qquad \eta = \frac{P_{out}}{P_{in}}$$

$$\tau_f = \tau_c + b\omega \qquad \text{(Coulomb + viscous friction model)}$$

---

## Testing Flow

```
Requirements → Unknowns → Prioritize → Sequence → Measure → Test → Decide
```

Every test traces back to a requirement or unknown. If you can't draw the line, question whether the test is worth running.

```
Requirement (01-requirements.md)
  → Unknown (what you don't know about meeting it)
    → Question (specific, measurable)
      → Acceptance criteria (defined BEFORE testing)
        → Test procedure (separate file)
          → Result + Decision (logged)
```

---

## 1. Requirements — Define "Good"

Every test traces to a requirement from `01-requirements.md`:

| Requirement | Target | Hard/Soft |
|-------------|--------|-----------|
| Backlash | ≤ 0.5° | Hard |
| Backdrivability | Backdriveable under human impulse | Hard |
| Durability | Can't break itself in < 1 min | Hard |
| Peak torque | ≥ 16 Nm | Hard |
| Continuous torque | ≥ 12 Nm | Hard |
| Thermal | No melting in < 5 min | Hard |
| Cost | < $120 CAD | Hard |
| Efficiency | > 90% | Soft |
| Weight | < 2 kg | Soft |
| Speed | ≥ 600 RPM continuous | Soft |

If a test doesn't verify a requirement or resolve an unknown, ask why you're running it.

---

## 2. Unknowns — What Don't You Know?

List everything you're uncertain about. Be specific — "does it work?" is not an unknown. "Does the planet-sun mesh cause binding at certain angular positions?" is.

**Categories:**

| Category | What it covers |
|----------|---------------|
| **Functional** | Does it do what it's supposed to? (ratio under load, backlash, etc.) |
| **Structural** | Will it survive? (shoulder strength, shaft diameter, tooth stress) |
| **Assembly/fit** | Do parts work together correctly? (mesh quality, constraints, alignment) |
| **Performance** | How well does it perform? (torque, drag, efficiency, backdrivability) |
| **Degradation** | What happens over time? (wear, loosening, thermal creep) |

**Current unknowns:**

| Unknown | Category | Source |
|---------|----------|--------|
| Planet positioning relative to sun/ring — geometry vs. assembly? | Assembly/fit | Prototype notes |
| How tight to actually make the gears (quantitatively) | Assembly/fit | Observation |
| Lid causing drag — over-constraint? | Assembly/fit | Prototype notes |
| Carrier bearing shoulder deformation under torque | Structural | Prototype notes |
| Carrier halves need indexing? | Assembly/fit | Observation |
| Gearbox structural capacity (can it handle motor torque × 5:1?) | Structural | Design assumption |
| Output shaft strength (self-tap sufficient, diameter adequate) | Structural | Design assumption |
| Backlash measurement | Performance | Requirement |
| Backdrivability | Performance | Requirement |
| Durability under sustained use | Degradation | Requirement |

---

## 3. Prioritize — Risk × Uncertainty

For each unknown, assess:

| Factor | High | Low |
|--------|------|-----|
| **Risk** | System doesn't function, breaks, fails hard requirement | Minor performance hit, cosmetic, soft requirement |
| **Uncertainty** | Never tested, no analysis, pure guess | Calculated, similar to known-good designs |
| **Cost to test** | Needs fixtures, instrumentation, time | Visual inspection, hand feel, calipers |

**Matrix:**

| | High risk | Low risk |
|---|---|---|
| **High uncertainty** | TEST FIRST | Test when convenient |
| **Low uncertainty** | Verify early | Monitor / skip |

**But priority alone isn't enough — you also need sequencing.**

---

## 4. Test Levels & Dependencies

Priority tells you *what matters most*. Dependencies tell you *what order is possible*.

### Test Levels (V-model, bottom-up)

| Level | What you're checking | Must pass before... |
|-------|---------------------|---------------------|
| **Component** | Individual parts meet spec (dimensions, tolerances, material) | Interface tests |
| **Interface** | Parts work together (mesh quality, bearing fit, lid fit) | Subsystem tests |
| **Subsystem** | Assembly functions (spins freely, correct ratio, no binding) | System tests |
| **System** | Full actuator meets requirements (torque, backlash, backdrivability) | Deployment |

You cannot meaningfully test a higher level until the levels below it pass.

### Dependency Rule

If test A failing would make test B's results meaningless, A must pass first. This creates a directed graph:

```
Component dimensions OK
  → Gear mesh quality OK (interface)
    → Free rotation / no binding (subsystem)
      → Backlash measurement (system)
      → Efficiency measurement (system)
      → Backdrivability (system)

Carrier shoulder integrity OK (component)
  → Carrier assembly holds under load (interface)
    → Torque capacity (system)
    → Durability (system)
```

### Combining Priority + Dependencies

Position in the dependency chain can override the priority matrix. A medium-priority component test outranks a high-priority system test if the system test depends on it.

**Practical rule:** Within each test level, use the risk × uncertainty matrix. Across levels, always resolve lower levels first.

### Applied to QDD gearbox right now

**Resolve first (component/interface level):**
- Planet positioning / mesh quality — gearbox won't function if this is wrong
- Lid over-constraint / drag source — blocks all performance testing
- Carrier shoulder integrity — structural failure risk, FDM strength is unpredictable

**Resolve after fundamentals work (subsystem/system level):**
- Backlash — important for design requirements, but meaningless to measure while gears bind. Fix mesh first, then quantify.
- Torque capacity — motor torque is known (off-the-shelf × 5:1 ratio), so the real question is structural: can the gearbox handle it?
- Backdrivability, efficiency, durability — all depend on the assembly functioning correctly first

---

## 5. Turn Questions into Measurements

For each prioritized unknown, define three things *before* picking any instrument:

1. **Question** — What specifically are you trying to answer?
2. **Quantity** — What physical measurement resolves it?
3. **Acceptance criteria** — What number or observation means pass/fail?

Only then choose the measurement method.

---

## 6. Design the Test Procedure

| Element | Define |
|---------|--------|
| **Prerequisites** | What lower-level tests must pass first? |
| **Setup** | Physical configuration — what's fixed, what moves |
| **Controls** | What's held constant (load, speed, temp) |
| **Variables** | What you're changing or observing |
| **Repetitions** | How many measurements for confidence |
| **Recording** | How you capture results (notebook, photo, data) |
| **Pass/Fail** | Written down BEFORE running the test |

If you can't explain the setup in 30 seconds, it's not well-defined enough.

---

## 7. Interpret and Act

Every test result leads to exactly one of:

| Result | Action |
|--------|--------|
| **Pass** | Requirement verified, move on |
| **Fail + clear root cause** | Design change, re-test |
| **Inconclusive** | Test design was wrong — revise and re-test |
| **Unexpected finding** | New unknown discovered — add to unknowns table |

Document the result AND the decision. A test without a documented decision is wasted effort.

Format: `[measurement] → [vs. target] → [root cause if fail] → [action]`

---

## What's Next

1. Verify the unknowns table is complete — pull from prototype notes, requirements, design assumptions
2. Map each unknown to a test level (component / interface / subsystem / system)
3. Build the dependency graph for your specific unknowns
4. Take the top items at the lowest unresolved level, work through Step 5 (question → quantity → criteria)
5. Write individual test procedure files

---

## Tesla Relevance

This process — requirements traceability, unknowns identification, risk-based prioritization, test level sequencing, measurement planning — is standard hardware V&V. The Optimus actuator team traces every test to a requirement, prioritizes by risk, sequences by dependency, and documents decisions.

Relevant posting language:
- "Hands on actuator and component (motor, gear, sensors) testing" (Req 250470)
- "Prototype assembling and testing" (Req 250470)
- "Python/Matlab test script and actuator model development" (Req 250470)
- "Own the mechanical design of test equipment from concept to deployment" (Req 255621)
