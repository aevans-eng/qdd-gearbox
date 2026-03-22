# Research Request: QDD Actuator Testing, Characterization, and Impedance Control

## Context

I'm an engineering student building a quasi-direct-drive (QDD) actuator: a 3D-printed (FDM PLA+) 5:1 planetary gearbox coupled with an ODrive D6374-150KV BLDC motor, ODrive v3.6 controller, and AS5047P magnetic encoder. I'm about to start a systematic test campaign covering mechanical characterization, system identification, and impedance control. I need practical, implementation-level information — not textbook theory.

## Research Topics (in priority order)

### 1. ODrive v3.6 Data Logging & Control Loop Implementation

I need to log Iq, position, velocity at high sample rates and also run real-time control loops (for impedance control) from Python over USB.

**Questions:**
- What is the maximum achievable sample rate when polling ODrive v3.6 via the Python API over USB? What are the bottlenecks?
- Does ODrive v3.6 have a built-in data logger (like `start_liveplotter` or native FIFO logging) that's faster than Python polling? How do you use it?
- For impedance control: can you run a torque-command control loop from Python on a PC at a useful rate (>100 Hz)? Or do you need to modify ODrive firmware? What latency should I expect?
- Are there better approaches (e.g., ODrive's built-in trajectory/torque control modes, custom firmware, or running the loop on a microcontroller that talks to ODrive)?
- What Python libraries or tools do people use for real-time ODrive data acquisition? (e.g., `odrive` package, `fibre`, direct USB/serial, etc.)
- Any known issues or gotchas with ODrive v3.6 + Python + D6374 motor specifically?

### 2. QDD Actuator Testing Practices in Research

I want my test results and portfolio presentation to match what real actuator engineers and researchers expect.

**Questions:**
- What metrics do QDD/SEA actuator research papers typically report? (e.g., MIT Cheetah, Stanford Doggo, BEAR actuator, Unitree, ANYmal actuators)
- What standard plots appear in actuator characterization papers? (friction curves, Bode plots, impedance plots, torque-speed curves, efficiency maps?)
- How do researchers typically measure and report:
  - Backlash (methods, instruments, how they present the data)
  - Friction (Coulomb + viscous model — is this standard or do people use more complex models?)
  - Backdrivability (what's the accepted metric — breakaway torque? continuous backdriving torque?)
  - Bandwidth (from Bode plot? from step response? both?)
  - Impedance/transparency (output impedance plot? Z(s) Bode plot?)
- What does a "complete" actuator characterization look like in a paper or technical report? What sections, what order, what data?

### 3. Impedance Control on Low-Ratio Geared Actuators — Practical Implementation

This is the end goal of my test campaign. I need to understand what actually works at the hobby/prototype scale.

**Questions:**
- How do people implement impedance control on ODrive or similar BLDC controllers? Python loop? Custom firmware? What control rates are needed?
- What's the minimum control loop rate for stable impedance control on a 5:1 gearbox with a 150KV motor? (roughly — 100 Hz? 500 Hz? 1 kHz?)
- How does backlash in the gearbox affect impedance control? What are the failure modes (limit cycling, chattering)?
- What $K$ (stiffness) and $B$ (damping) ranges are typical for a QDD actuator of this size (~16 Nm peak)?
- How do people measure/demonstrate impedance control quality? (force-displacement plots? output impedance Bode plots? interaction videos?)
- Are there open-source implementations of impedance control on ODrive that I can reference?
- What safety considerations matter? (e-stop, current limits, software limits on torque command)

### 4. System Identification for BLDC Motor + Gearbox

I'm going to derive the plant transfer function from step response data and validate it with a frequency response (Bode plot).

**Questions:**
- What's the standard approach for system ID on a BLDC motor controlled by a current-loop (FOC) controller? Since the current loop is fast, is the plant effectively just $G(s) = 1/(Js^2 + bs)$?
- How do people do frequency sweeps on motor systems? Chirp signal vs discrete frequency steps vs PRBS? What works best practically?
- What Python tools exist for system identification? (`scipy.signal`, `python-control`, `SIPPY`, others?)
- How do you extract the open-loop plant $G(s)$ from closed-loop step response data when you know the PID gains?
- For a motor + gearbox system: how does the gearbox change the plant model? Just reflected inertia $J_{total} = J_m + N^2 J_g$? Or are there compliance/backlash terms that matter?
- What accuracy should I expect from system ID on a 3D-printed gearbox? (friction is nonlinear, backlash is discontinuous — do linear models still work?)

### 5. Tesla Optimus Actuator Architecture (Public Information)

I want to understand enough about Tesla's actuator design philosophy to speak intelligently about it when networking with their engineers.

**Questions:**
- What is publicly known about Tesla Optimus actuator architecture? (presentations, patents, teardowns, conference talks)
- What type of actuators does Optimus use? (QDD? SEA? harmonic drive? planetary? cycloidal?)
- What motor topology? (outrunner BLDC? custom motors?)
- What control approach? (impedance control? force control? position control with compliance?)
- What testing methodology has Tesla described publicly for their actuators?
- What metrics does Tesla emphasize? (torque density? bandwidth? transparency? efficiency?)
- Are there any Tesla AI Day, Optimus reveal, or conference presentations that discuss actuator testing specifically?

### 6. FDM 3D-Printed Gear Testing & Failure Modes

My gearbox is FDM PLA+ with spur gears (5:1 planetary). I need to know what to watch for.

**Questions:**
- How do FDM-printed gears typically fail? (tooth shear? wear? creep? delamination at layer lines?)
- What's the typical lifespan of FDM PLA+ spur gears under moderate load (<5 Nm at the mesh)?
- How does print orientation affect gear strength? (teeth parallel vs perpendicular to layer lines)
- Are there published test results for 3D-printed gear performance? (academic papers, YouTube teardowns, engineering blogs)
- What wear patterns should I look for during testing? (visual indicators of impending failure)
- How does temperature affect PLA+ gear performance? At what point does thermal softening become a concern under load?

## What I Need From This Research

For each topic, I need:
1. **Concrete answers** to the questions above, with sources
2. **Links to relevant papers, GitHub repos, forum posts, or videos** that I can reference
3. **Practical recommendations** for my specific setup (ODrive v3.6 + D6374 + 5:1 FDM gearbox)
4. **Things I might not have thought to ask** — gaps in my plan based on what experienced people know

Focus on practical, implementation-level information over theory. I have textbooks for theory — I need the stuff that only comes from people who've actually done this.
