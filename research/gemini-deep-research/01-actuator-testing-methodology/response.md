# QDD Actuator Testing, Characterization, System ID, and Impedance Control for an ODrive v3.6 + D6374-150KV + 5:1 FDM PLA+ Gearbox

## ODrive v3.6 logging and real-time loop execution from Python over USB

ODrive v3.6 (firmware lineage 0.5.x) gives you two fundamentally different “pipes” over USB: a CDC virtual COM port that runs the ASCII protocol (by default), and a vendor-specific interface that runs the Native Protocol (packet-based) used by `odrivetool`/the Python API. These two interfaces cannot (yet) be used simultaneously, which matters because you can’t, for example, stream ASCII telemetry and concurrently use native-protocol RPC for control. citeturn14view0turn15view0

Your “need-to-log” variables are explicitly supported in the v0.5.6 command/monitoring docs: position/velocity via `axis.encoder.pos_estimate` and `axis.encoder.vel_estimate`, quadrature current via `axis.motor.current_control.Iq_setpoint` and `Iq_measured`, and torque-commanding via `axis.controller.input_torque` (in N·m). citeturn26view0

### What sample rate is realistically achievable via Python polling over USB, and what are the bottlenecks?

There is no single official “max polling Hz” promise in ODrive v3.6 documentation, but ODrive’s own Python utilities encode practical expectations:

* The built-in *liveplotter* helper (`start_liveplotter`) is hard-coded to a default `data_rate = 200` Hz. citeturn7view0  
* The “bulk capture” helper (`BulkCapture`) defaults to `data_rate = 500` Hz and includes logic to measure and report the achieved rate, warning you when performance falls below ~90% of requested. citeturn7view0  

Those defaults are a strong signal of what the maintainers considered “reasonable” on real machines with real USB stacks: **~200 Hz is the “it should basically always work” tier; ~500 Hz is the “often works, measure it” tier** (especially as you increase the number of variables read per sample). citeturn7view0

The main bottlenecks are architectural rather than compute-limited:

* **Transaction overhead per variable**: the Python API reads properties by performing endpoint operations over the native protocol; each sample of “(Iq, pos, vel)” is not “one packet,” it’s typically multiple device transactions unless you design a combined endpoint or batch access. The protocol is defined as endpoint operations with request/response payloads, which inherently imposes per-transaction overhead. citeturn15view0  
* **USB full-speed + composite device constraints**: ODrive v3.6’s USB design is full-speed composite CDC + vendor interface; you’re limited by how fast you can push small request/response packets through the OS USB stack with low jitter. citeturn14view0  
* **Non-real-time host timing**: `BulkCapture` and liveplotter intentionally use `time.sleep(...)` pacing; on Windows/macOS/Linux you will see scheduling jitter. Even if average rate is high, jitter is the bigger problem for control-loop stability. citeturn7view0  

A related anchor: ODrive’s internal control loop runs around **8 kHz** (ODrive staff explicitly reference an 8 kHz controls/FOC loop, and ODrive’s API docs in newer generations discuss timing wrap-around “assuming 8 kHz control loop frequency”). citeturn24search5turn24search7  
That means **your Python-over-USB loop will always be an “outer loop”** running at maybe 1–6% of the internal update rate, and you should plan your impedance controller accordingly (lower stiffness, more damping, more filtering, and explicit current/torque limiting).

### Does ODrive v3.6 have a built-in data logger that’s faster than Python polling?

Yes—two levels exist, with different implications:

**Host-side helper loggers (still limited by polling)**  
`start_liveplotter()` and `BulkCapture()` are convenient, but they remain host-paced polling mechanisms. They are *not* “native FIFO logging” on the device. citeturn7view0  

**Firmware “oscilloscope” buffer (device-capture, host-readout)**  
ODrive implemented an embedded “oscilloscope-like buffer” concept specifically to allow logging at the full control-loop rate into a buffer, then transferring to the host afterward. This design intent is documented in ODrive’s own issue history (it was tracked as a feature and later marked completed). citeturn18view0  
In the v0.5.6 API surface, you can see an `odrv.oscilloscope` object with `size` and `get_val(index)` exposed. citeturn21view0  
And in ODrive’s Python utils, there is an `oscilloscope_dump(odrv, num_vals, filename)` helper that simply iterates `get_val(i)` to write `oscilloscope.csv`. citeturn7view0  

**Practical reality check:** the public v0.5.6 API reference is extremely minimal (only `get_val` and `size`), so *how you configure what signal gets captured* may require either (a) digging into firmware defaults, or (b) custom firmware hooks. citeturn21view0turn18view0  
Still, this is your best path if you need **true kHz-to-8kHz internal waveforms** for debugging loop tuning (e.g., current-loop behavior, torque ripple, encoder noise injection), even if it’s not a flexible multi-channel recorder out of the box. citeturn18view0turn24search5

### Can you run a torque-command impedance loop from Python at a useful rate (>100 Hz)? What latency should you expect?

**Yes, >100 Hz is usually feasible**, because you’re “just” updating `axis.controller.input_torque` in N·m while ODrive handles fast inner loops. citeturn26view0turn24search5  
However, **useful impedance control is determined by worst-case jitter, not average Hz**. A 200 Hz loop that occasionally stalls for 30–80 ms will behave like a destabilizing time delay in an impedance controller (often worse than a steady 100 Hz loop with small jitter).

Implementation-level guidance for your specific setup:

* Treat your Python loop as a **low-bandwidth outer impedance loop** and explicitly cap aggressiveness. Your torque command is held between updates (zero-order hold behavior is explicitly discussed in ODrive’s controller documentation for newer generations, and the same discrete-command reality applies here). citeturn10search3  
* If you’re doing **stiff contact** (high K) or interacting with unknown environments, Python-over-USB becomes the limiting factor quickly. The literature on high-bandwidth active impedance control repeatedly emphasizes that achievable “virtual impedance range” (Z-width) depends strongly on closed-loop torque bandwidth, and also highlights how measurement noise and derivative estimation inject audible/physical noise when bandwidth is pushed. citeturn32view2turn31view0  

### Better approaches than “PC Python loop over USB”

If your end goal is impedance control that looks like what legged robotics labs expect, the common pattern is:

1) **Fast inner torque/current loop on the drive** (ODrive already has that internally, ~8 kHz). citeturn24search5turn24search7  
2) **Outer impedance loop on a real-time compute substrate**, *not* a desktop OS USB control loop. The MIT proprioceptive actuator paradigm is explicitly about collocated force/torque control enabling high-bandwidth interaction. citeturn29view0turn30view0  

For your build, the most pragmatic upgrades (in descending practicality):

* **Run the impedance controller on a microcontroller/SBC with tighter timing** (Teensy/STM32/RPi with RT-preempt), and communicate setpoints to ODrive via a robust interface. ODrive’s native protocol is supported on UART as well as USB, and ASCII is available, but the native protocol is recommended when you have a choice. citeturn14view1turn15view0  
* **Use ODrive’s internal position/velocity control loops as an “impedance-like” behavior** by tuning gains and commanding equilibrium position; this won’t replicate full interaction control, but it can produce stable “springy” behavior at the internal loop rate without USB jitter dominating. (You still must handle backlash and friction carefully—see impedance section.) citeturn26view0turn24search5  
* **Custom ODrive firmware**: implement your impedance control law inside the 8 kHz control loop and optionally log with the embedded oscilloscope. This is the closest to “research actuator controller” behavior, but it is the highest-effort path. citeturn18view0turn24search5  

### Python tools people actually use for ODrive data acquisition

For v3.6-era workflows, the core ecosystem is:

* `odrive` Python package + `odrivetool` shell (native protocol) citeturn14view1turn26view0  
* `odrive.utils` helpers like `BulkCapture`, `start_liveplotter`, and `oscilloscope_dump` citeturn7view0  
* Community tooling for v0.5.6 usability gaps (not required for core functionality but useful for configuration). citeturn12search8turn10search13  

### Known gotchas you should plan around before your test campaign

Your setup has two risk multipliers: a high-power servo drive (ODrive) and a compliant-ish transmission (FDM PLA+ planetary). The gotchas that most often blow up tests:

* **Encoder slip or poor coupling → runaway/oscillation**: ODrive explicitly warns that encoder slip can cause “disastrous oscillations or runaway.” This matters *even more* with 3D-printed parts that can deform under load. citeturn13view0  
* **Brake energy handling**: if you decelerate aggressively without a battery or brake resistor, bus voltage rises until overvoltage trips; the getting-started docs emphasize this failure mode and why a brake resistor (or battery) matters. citeturn13view0  
* **Torque estimation limits at high speed**: ODrive notes that `Iq_measured` can become noisy and that commanded vs measured current diverge as you approach voltage-limited speed, which directly affects “current → torque” inference. citeturn26view0  

Key references (papers/repos/docs) for this section:
```text
ODrive v0.5.6 docs (commands, USB, protocol, API reference):
https://docs.odriverobotics.com/v/0.5.6/getting-started.html
https://docs.odriverobotics.com/v/0.5.6/commands.html
https://docs.odriverobotics.com/v/0.5.6/usb.html
https://docs.odriverobotics.com/v/0.5.6/protocol.html
https://docs.odriverobotics.com/v/0.5.6/fibre_types/com_odriverobotics_ODrive.html
```


## What QDD/SEA actuator characterization “should look like” in research-style reporting

If you want your plots and metrics to look like what actuator engineers expect, anchor your campaign around the *same claims* actuator papers make: torque density, transparency/backdrivability, bandwidth (torque and/or impedance), thermal limits, and repeatable measurement methodology.

A strong template baseline comes from the MIT proprioceptive actuator work, which explicitly frames the design objectives as high torque density, efficiency, and impact mitigation/backdrivability (via a new metric, IMF), and then demonstrates force-tracking during dynamic locomotion contact windows (e.g., contact times down to ~85 ms and high peak forces). citeturn29view0turn30view0turn30view1  
Stanford Doggo is another clear QDD reference point: an open-source quadruped explicitly built around quasi-direct-drive design methodology and performance metrics tied to dynamic locomotion. citeturn27search1turn27search26  
ANYmal’s platform paper highlights “compliant joint modules” and explicitly emphasizes torque controllability and robustness to impulsive loads—useful framing for what “good actuators” enable at the robot level. citeturn28search0  

### Metrics that show up repeatedly (and are portfolio-grade)

A research-style characterization typically includes:

**Static and quasi-static performance**
You should report torque constant calibration and torque accuracy in a way that acknowledges QDD reality: with low gear ratio, you *can* use motor current as a proxy for output torque, but you must validate it against an external torque measurement (lever arm + load cell, or torque transducer), because friction and efficiency errors are not negligible—especially in 3D printed gearboxes. The ODrive docs directly support the motor-current readouts you need (`Iq_setpoint`, `Iq_measured`) and the current-to-torque estimate relationship. citeturn26view0turn22search0  

**Backdrivability / transparency**
MIT introduced **Impact Mitigation Factor (IMF)** as a backdrivability-at-impact metric to compare across designs (including SEAs). Even if you don’t compute IMF fully, referencing it and explaining why you chose a simpler proxy (breakaway torque, torque to backdrive at a given speed, “deadband torque” across backlash) will make your report read like it’s written by someone who read the actuator literature. citeturn29view0turn30view0  

**Bandwidth**
Researchers often care about:
* **Torque loop bandwidth** (how fast torque tracks commanded torque) because it governs achievable Z-width and robust interaction. citeturn32view2turn31view0  
* **Output impedance / “transparency”** as a frequency response: how stiff the actuator feels to the environment when you *don’t* want it to be stiff. (More in impedance section.)

### Standard plots that belong in your report

For a QDD actuator portfolio, the most recognizable plot set (that reviewers will instantly understand) is:

1) **Torque–speed envelope** (continuous and peak) and where your controller saturates (current, voltage, temperature). Stanford Doggo and MIT-style actuator work strongly emphasize performance envelopes tied to dynamic tasks, not just “it spins.” citeturn27search1turn29view0  

2) **Friction characterization curves**: torque required vs velocity, separated by direction (CW vs CCW), ideally including a fitted model (Coulomb + viscous is the minimum; add Stribeck if you see low-speed curvature). You can measure the needed currents directly (`Iq_setpoint`/`Iq_measured`) and convert to torque using your calibrated constant. citeturn26view0turn22search0  

3) **Backlash / hysteresis plot**: output angle vs applied torque for a slow torque ramp up/down (shows deadband + hysteresis). This is especially important for your PLA planetary. (You’ll likely see a “flat” region around zero torque due to backlash, then a steeper slope once teeth engage + plastic compliance.)

4) **Frequency response (Bode) of torque tracking and/or impedance**
If you can’t do full impedance FRF, a torque-loop FRF is still highly legible.

5) **Thermal derating curve**: continuous torque vs time (or motor current vs time) until thermal steady state, plus a cool-down profile. Even if you can’t instrument internal motor temps, you can still log inverter temperature and motor current; the point is to show you understand continuous vs peak. citeturn23view0  

A representative example of what “dynamic force tracking evidence” looks like is visible in MIT’s proprioceptive actuator figures: measured vs commanded force trajectories during bounding, with a clearly marked evaluation window. citeturn30view1  

Key references (papers) for this section:
```text
MIT proprioceptive actuator paper (impact mitigation, IMF, force tracking):
https://fab.cba.mit.edu/classes/865.18/motion/papers/mit-cheetah-actuator.pdf

Stanford Doggo (QDD quadruped paper + open-source project):
https://arxiv.org/abs/1905.04254
https://github.com/Nate711/StanfordDoggoProject

ANYmal platform paper (torque controllable compliant joints framing):
https://dbellicoso.github.io/publications/files/hutter2017anymaltoward.pdf
```


## Practical impedance control on a low-ratio geared actuator like yours

You can think of “impedance control on QDD” as having two non-negotiable requirements:

1) **A stable, high-bandwidth inner torque loop**  
2) **An outer impedance loop whose rate/jitter and sensing quality match the stiffness you want**

The proprioceptive-actuator literature explicitly ties achievable virtual impedance range (Z-width) to closed-loop torque bandwidth, while also calling out the very practical problem: high-bandwidth torque + impedance control tends to inject noise (especially from differentiating encoder position into velocity). citeturn32view2turn31view0

### How people implement it on ODrive-class drives in practice

For ODrive v3.6 specifically, the most practical implementation tiers are:

**Tier A: “Impedance-ish” behavior using ODrive’s internal loops (most robust to USB jitter)**  
You tune ODrive’s inner position/velocity control gains to behave like a spring-damper around an equilibrium position, and you command the equilibrium (`input_pos`) from the host at modest rate. This leverages the ~8 kHz internal loop and avoids needing a high-rate host torque loop. citeturn24search5turn26view0  

**Tier B: True impedance law computed on host, torque sent to ODrive (best fidelity, but timing-limited)**  
You read `pos_estimate` and `vel_estimate`, compute `tau = K*(x_des - x) + B*(v_des - v) + tau_ff`, then write `input_torque`. The needed primitives are all directly supported in v0.5.6 (`input_torque`, `pos_estimate`, `vel_estimate`). citeturn26view0turn22search0  

**Tier C: Outer loop on a microcontroller, torque commands to ODrive (best “research-like” outcome without firmware hacking)**  
Same math as Tier B, but moved off the PC. You gain tighter loop timing and deterministic safety interlocks.

### Minimum loop rate: 100 Hz vs 500 Hz vs 1 kHz?

A defensible rule of thumb is: **if you’re only trying to show “compliant interaction” (low-to-moderate stiffness), 100–200 Hz can work; if you want high stiffness and good feel, you want ~500 Hz to 1 kHz outer-loop timing with low jitter**.

The strongest grounded reason is time delay: impedance control is very sensitive to delay and jitter, especially when mechanical backlash and friction cause discontinuities near zero torque. The proprioceptive actuator literature highlights that high bandwidth is critical in fast interactions (impacts/collisions), and that reducing torque bandwidth degrades tracking and impact absorption. citeturn31view0turn32view2  
On the ODrive side, remember your inner loop is ~8 kHz, so the controller can *execute* your command quickly, but your **command freshness** is limited by your outer loop timing. citeturn24search5turn24search7

For your particular build (5:1, ~16 N·m peak), a practical commissioning path is:

* Start outer loop at **100 Hz** with strong damping, low stiffness.  
* Move to **200–500 Hz** only after you add: (a) torque limiting, (b) velocity filtering, and (c) a hard e-stop + watchdog behavior. ODrive supports a watchdog mechanism at the axis level you can incorporate into your safety plan. citeturn13view0turn26view0  

### Backlash: how it breaks impedance control (failure modes you should expect)

Backlash introduces a deadzone where output torque does not produce output motion until gear teeth engage. In impedance control, that often produces:

* **Limit cycles / chatter around zero crossing**: the controller “hunts” across the backlash gap, rapidly changing torque sign.  
* **Apparent “negative damping”** when velocity estimates are noisy and torque updates are delayed. citeturn32view2turn31view0  
* **Impacty re-engagement**: when teeth re-contact, the effective stiffness jumps discontinuously and can excite structural resonances—especially in plastic gear trains.

With an FDM PLA+ planetary, backlash may *grow over time* due to wear and creep, so the impedance behavior you tuned on day 1 may drift.

Two practical mitigations that work well at prototype scale:

* Add a **deadband torque / hysteresis** in your impedance law around zero (effectively “do nothing unless error exceeds X”), to avoid chattering in the backlash region.
* Use a **sign-consistent preload** (small constant torque bias) during certain regimes so the gearbox stays engaged on one flank during contact.

### What K and B ranges are “typical” for your size class?

Published “K and B” are rarely portable because they depend on link length, inertia, and task. A better portfolio-grade way to choose K and B is to tie them to **your torque limits** and **a target deflection**:

* If you want full-scale torque (±16 N·m) at ±0.10 rad (≈5.7°), then **K ≈ 160 N·m/rad**.  
* If you want full-scale torque at ±0.05 rad (≈2.9°), then **K ≈ 320 N·m/rad**.

Then choose **B** for critically damped-ish behavior relative to your reflected inertia estimate (see system ID section). In early testing, it’s common to start with “overdamped” behavior (higher B) because backlash + friction create effective nonlinearity that “looks like time delay.”

The crucial implementation detail: `input_torque` is in N·m on ODrive v0.5.6, so your K/B math can remain in physical units once your encoder is calibrated in turns→radians. citeturn26view0  

### How to demonstrate impedance quality (what to record)

A minimal set that looks “research real”:

* **Force/torque vs displacement** during quasi-static interaction (shows stiffness and hysteresis).  
* **Impulse / tap test** against a known compliance, showing bounded response (no growing oscillations).  
* **Output impedance FRF** (if you can): apply a small chirp torque and measure resulting motion; compute Z(jω)=τ(jω)/ω(jω) or τ(jω)/x(jω).

Even if you don’t compute Z formally, showing measured vs commanded interaction forces during dynamic windows (as MIT does for proprioceptive force control) is a strong precedent for how “interaction control” evidence is presented. citeturn30view1turn29view0  

Key references (impedance + actuator bandwidth context):
```text
High-bandwidth active impedance control discussion (Z-width vs torque bandwidth, noise injection realities):
https://www.mdpi.com/2076-0825/8/4/71
```


## System identification for BLDC + gearbox using ODrive’s current/torque mode

Because ODrive exposes torque-command input (`input_torque`) and current measurement (`Iq_setpoint`, `Iq_measured`), the cleanest “engineering” system ID approach is to treat ODrive as a **torque source** (inner current/FOC loop closed) and identify the *mechanical plant* from torque → motion. citeturn26view0turn24search5

### Is the plant basically \(G(s) = 1/(Js^2 + bs)\) when the current loop is fast?

For a first-pass linear model, yes—especially for low-frequency behavior away from backlash engagement/disengagement—because the torque loop is fast relative to your outer excitation band and the dominant dynamics become inertia + damping. The v3.6 control environment (8 kHz inner loop) supports this separation of time scales for most mechanical ID experiments below a few hundred Hz. citeturn24search5turn24search7

What breaks the simple model for your printed gearbox:

* **Backlash** (discontinuous deadzone)  
* **Coulomb friction + stiction** (nonlinear near zero velocity)  
* **Plastic compliance** (torsional spring behavior, often load-dependent)

So: do your linear ID, but also explicitly quantify where it fails (e.g., “model valid above ±0.2 N·m and |ω|>0.5 rad/s”—numbers depend on your data).

### Frequency sweeps that work well in practice

On hobby-scale rigs, the most reliable is:

* Apply a **torque chirp** (small amplitude, bias away from backlash if needed), log response, compute FRF with FFT methods.
* Repeat with **discrete sine dwell** at key frequencies if you need cleaner magnitude/phase.

Why chirp is practical with ODrive: your command path is straightforward (`input_torque`), and you can log `pos_estimate`/`vel_estimate` and current signals for correlation. citeturn26view0turn22search0

### How does the gearbox change the model?

At minimum, account for reflected inertia:

* Reflect load inertia to motor: \(J_\text{ref} = J_\text{load}/N^2\)  
* Reflect motor inertia to output: \(J_\text{out} \approx N^2 J_\text{motor} + J_\text{gear} + J_\text{load}\)

But with a PLA planetary, you should expect an additional torsional compliance term (spring-damper) and backlash deadzone if you’re trying to ID beyond low frequencies.

### Extracting open-loop plant from closed-loop response

In your situation, you don’t need to do the “closed-loop inversion” if you can run ODrive in torque control and keep higher-level loops off. That gives you the cleanest identification: **torque command → motion** directly, with ODrive doing only the torque production. The commands page makes clear that torque mode is first-class (`input_torque`), and you can log the relevant state estimates. citeturn26view0turn22search0  


## Tesla Optimus actuator architecture from public information

Publicly, Tesla has **not** released a full bill-of-materials actuator teardown with exact gear ratios and motor drawings. What you *can* say confidently (and credibly) is based on three classes of public signals: Tesla recruiting, Tesla-related patent filings, and credible third-party reporting/interviews.

### What types of actuators and transmissions are plausibly in Optimus?

**Tesla recruiting signals (not proofs, but strong hints of design space)**  
A Tesla “Mechanical Engineer, Actuator Integration, Optimus” job description explicitly lists experience domains including planetary, strain wave (harmonic drives), cycloidal, ball screws, belt drives, lead screws, magnetic gear, and “speed reduction systems,” plus torque/force sensing and instrumentation. This tells you Tesla is actively engineering **both rotary and linear reduction systems** and cares about specific torque, efficiency, reliability, and sensing. citeturn33search0  

**Patents: actuator architectures and sensing**  
Tesla-associated patent publications describe actuator systems and methodologies, including the idea of multiple actuator “types” across the robot and sensor integration along a communication backbone. citeturn33search5turn34search18  
Separately, patents for **planetary roller screw linear actuators** exist in the ecosystem of filings being discussed in relation to humanoid actuators; these documents describe integrated roller-screw linear actuator structures and position sensing via magnets/sensing assemblies. citeturn34search2turn34search11  

**Credible reporting: rotary + linear split**  
IEEE Spectrum’s expert commentary very explicitly frames humanoid actuation (including Optimus) in two main classes: **rotary actuators** (described as integrated strain-wave/harmonic-drive style reduction) and **linear actuators** (described as integrated inverted roller screw drive). citeturn34search12  

### What control approach is likely?

Even without Tesla publishing control block diagrams, you can talk intelligently using a conservative, defensible framing:

* Humanoids doing dynamic contact tasks typically need **force/torque awareness** and at least some form of **impedance/force-limited behavior** in joints. This aligns with Tesla emphasizing in-house actuators/sensors in public updates and media coverage of Optimus Gen 2. citeturn34search10turn34search4  
* Tesla’s patent material also emphasizes sensors on actuators and a communication/control backbone, consistent with distributed joint control architectures. citeturn33search5turn34search18  

### What testing methodology and metrics does Tesla emphasize publicly?

Tesla doesn’t publish “Bode plots of joint impedance” publicly (at least not in the sources above). But from recruiting language you can infer the metrics a Tesla actuator engineer will care about: **specific torque/force, efficiency, reliability, thermal performance, and torque/force sensing instrumentation**. citeturn33search0  
If you want to sound credible in conversation, anchor to those and then relate them to the actuator literature vocabulary: torque density, transparency/backdrivability, bandwidth, thermal derating, and safety-limited interaction.

Key references (public, citable):
```text
Tesla Optimus actuator integration hiring signal:
https://www.tesla.com/careers/search/job/mechanical-engineer-actuator-integration-optimus-258780

IEEE Spectrum expert commentary (rotary harmonic-drive vs linear inverted roller screw framing):
https://spectrum.ieee.org/robotics-experts-tesla-bot-optimus

Tesla-related actuator patents:
https://patents.google.com/patent/WO2024072984A1/en
```


## FDM PLA+ planetary gear testing and failure modes for your 5:1 gearbox

Your gearbox is the most “research-uncertain” component: FDM PLA gears are highly sensitive to print parameters, orientation, infill, and temperature—and they can degrade with wear and creep. The right mindset is not “what is the lifespan,” but “how do I detect degradation early and quantify it.”

### How FDM PLA gears typically fail (what to watch for)

Peer-reviewed testing on 3D-printed PLA gears commonly focuses on fatigue life and failure type under controlled torque/speed. For example, experimental work studying PLA gears finds that fatigue life and failure behavior vary strongly with infill percentage under the same torque/speed conditions. citeturn33search6  
Accelerated wear testing across materials (ABS, PLA, annealed PLA) also shows that PLA wear behavior is materially different and that annealing can modestly improve durability in some regimes—useful if you later decide to upgrade filament or post-process. citeturn33search24  

In practice, for a PLA planetary you should expect a mix of:

* **Tooth-root fatigue cracking** (often worsened by layer-line orientation that puts inter-layer adhesion in tension at the tooth root)
* **Tooth face wear / pitting** leading to increased backlash and noise
* **Creep / permanent deformation** (especially if the tooth contact stress is sustained at elevated temperature)

### Print orientation effects are real (and measurable)

Mechanical performance of FDM PLA is strongly dependent on printing orientation; orientation changes can significantly alter strength/stiffness, and dynamic mechanical analysis work explicitly studies how printing orientation influences glass transition region behavior and modulus. citeturn33search7  
That means you should record and report print orientation in your gearbox build spec, the same way researchers report motor KV or encoder CPR—because it changes the mechanical plant.

### Temperature: when does PLA become a concern?

You should assume PLA approaches problematic softening not at “melting,” but near its glass transition and heat deflection regime.

A concrete manufacturer datasheet example (Ultimaker PLA) reports **heat deflection temperature ~58.8 °C** (at the specified test condition) and Tg on the order of ~59 °C. citeturn33search18  
A separate experimental write-up on 3D printed PLA temperature resistance notes “glass transition temperature of PLA is around 60 °C” and discusses annealing as a way to raise temperature resistance/heat deflection behavior. citeturn33search28  

**Implication for your test campaign:** log gearbox temperature (even if it’s just an IR sensor on the housing) during sustained torque tests. If the housing is approaching ~45–55 °C, assume tooth stiffness and backlash may drift measurably during the run.

### Practical gearbox test checkpoints you should add

To make your campaign robust (and to surface 3D-print-specific failure early), add these checkpoints:

* **Backlash growth over time**: measure backlash at baseline, then after every thermal/fatigue test block. Backlash is the “canary in the coal mine” for gear wear and plastic deformation.
* **No-load current vs speed drift**: as wear increases, friction rises; you’ll see increasing `Iq` required for the same speed. ODrive gives you the current signals needed. citeturn26view0turn22search0  
* **Visual inspection map**: photograph tooth flanks and planet carrier features under consistent lighting and magnification. This becomes portfolio-grade evidence of wear patterns.

Key references (gears + PLA temperature):
```text
Experimental failure analysis of PLA 3D-printed gears (fatigue life vs infill, failure types):
https://www.sciencedirect.com/science/article/pii/S245232162300358X

PLA datasheet example (HDT and Tg around ~60°C):
https://um-support-files.ultimaker.com/materials/2.85mm/tds/PLA/Ultimaker-PLA-TDS-v5.00.pdf
```