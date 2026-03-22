# QDD Actuator — Test Tracker

| Field | Value |
|-------|-------|
| Assembly | QDD Planetary Gearbox (5:1), Rev 00B |
| Document Owner | Aaron Evans |
| Created | 2026-03-08 |
| Last Updated | 2026-03-13 |

---

## 1. Requirements Reference

Source: `docs/design-sprint-jan4/design-requirements.md`

| ID   | Requirement       | Target                                | Type | Verification Method |
| ---- | ----------------- | ------------------------------------- | ---- | ------------------- |
| R-01 | Backlash          | ≤ 0.5°                                | Hard | Measurement         |
| R-02 | Cost              | < $120 CAD                            | Hard | Inspection (BOM)    |
| R-03 | DFM/DFA           | Off-the-shelf + FDM, no special tools | Hard | Inspection          |
| R-04 | Backdrivability   | Friction torque < 1 Nm (motor disconnected) | Hard | Measurement   |
| R-05 | Durability        | No self-destruction in < 1 min        | Hard | Test                |
| R-06 | Peak torque       | ≥ 16 Nm                               | Hard | Measurement         |
| R-07 | Continuous torque | ≥ 12 Nm                               | Hard | Measurement         |
| R-08 | Thermal           | No melting in < 5 min                 | Hard | Measurement         |
| R-09 | Efficiency        | > 90%                                 | Soft | Measurement         |
| R-10 | Weight            | < 2 kg                                | Soft | Measurement         |
| R-11 | Speed             | ≥ 600 RPM continuous                  | Soft | Measurement         |

### Requirements Traceability — Coverage Gaps

> Last reviewed: 2026-03-17

| Req | Validated By (Phases 0–4) | Gap? |
|-----|--------------------------|------|
| R-01 Backlash | **T-012** | — |
| R-02 Cost | BOM inspection | — |
| R-03 DFM/DFA | Inspection | — |
| R-04 Backdrivability | **T-013, T-008, T-006** | — |
| R-05 Durability | — | **Phase 5 only** |
| R-06 Peak torque | — | **Phase 5 only** |
| R-07 Continuous torque | — | **Phase 5 only** |
| R-08 Thermal | Health monitoring (informal) | **Phase 5 only — no formal pass/fail test** |
| R-09 Efficiency | T-006 (friction, related) | **Phase 5 only — T-006 does not measure output power** |
| R-10 Weight | — | **Trivial — weigh the assembly** |
| R-11 Speed | T-016 (bandwidth, related) | **No direct 600 RPM sustained test** |

**Notes:**
- R-05 through R-09 are deferred to Phase 5 by design — Phases 0–4 focus on characterization and controls capability. These requirements cannot be claimed as validated until Phase 5 is executed.
- R-10 requires only a kitchen scale measurement — add as a 1-minute check at the start of Phase 1.
- R-11: T-016 measures frequency-domain bandwidth, not max continuous RPM. A direct validation would require sustained operation at 600 RPM output (3000 RPM motor shaft) and confirming no faults or thermal issues.
- T-007, T-016, T-017, T-018 are characterization/demo tests — they build understanding and portfolio content but do not directly pass/fail against specific requirements.

---

## 2. Prioritization Reference

**Risk × Uncertainty Matrix**

|  | High Risk | Low Risk |
|--|-----------|----------|
| **High Uncertainty** | Test first | Test when convenient |
| **Low Uncertainty** | Verify early | Monitor / skip |

**Test Levels (resolve bottom-up)**

| Level | Scope | Prerequisite |
|-------|-------|--------------|
| Component | Individual parts meet spec | — |
| Interface | Parts work together correctly | Component pass |
| Subsystem | Assembly functions as intended | Interface pass |
| System | Full actuator meets requirements | Subsystem pass |

---

## 3. Dependency Map

```
Component: part dimensions, print quality, bearing fits
  └─► Interface: gear mesh quality, carrier-bearing assembly, lid fit
        └─► Subsystem: free rotation, correct ratio, no binding
              └─► System: backlash, torque capacity, backdrivability, efficiency, durability
```

**Gearbox-specific dependencies:**

```
Planet bore dimensions OK ──┐
Sun gear fit on shaft OK ───┤
Ring gear print quality OK ─┴──► Gear mesh quality OK ──► Free rotation ──┬─► Backlash (R-01)
                                                                          ├─► Efficiency (R-09)
                                                                          ├─► Backdrivability (R-04)
Carrier shoulder integrity OK ─► Carrier holds under load ───────────────┬┴─► Torque capacity (R-06, R-07)
                                                                         └──► Durability (R-05)
Lid fit / constraint OK ──────► No parasitic drag ──► Backdrivability (R-04)
```

---

## 4. Unknowns Register

> **Convention:** IDs are permanent. Merged or retired entries keep their ID and are marked accordingly — never renumber, as IDs may be referenced in notes, conversations, and test entries.

| ID   | Unknown                                                          | Category     | Test Level | Depends On       | Traces To        | Priority           | Status      |
| ---- | ---------------------------------------------------------------- | ------------ | ---------- | ---------------- | ---------------- | ------------------ | ----------- |
| U-01 | Planet positioning & mesh clearance — geometry vs. assembly?     | Assembly/fit | Interface  | Component dims   | R-01, R-04, R-09 | Test first         | Postponed → Rev 00B |
| U-02 | ~~Merged into U-01~~ | — | — | — | — | — | — |
| U-03 | Lid causing drag — over-constraint on carrier?                   | Assembly/fit | Interface  | —                | R-04, R-09       | Test first         | Root cause identified |
| U-04 | Carrier bearing shoulder deformation under bolt torque           | Structural   | Component  | —                | R-05, R-06       | Test first         | Confirmed — shoulders sensitive to torque (T-005) |
| U-05 | Carrier halves need indexing?                                    | Assembly/fit | Interface  | U-04             | R-01             | Monitor / skip     | Resolved — no operational clocking load |
| U-06 | Gearbox structural capacity (handles motor torque × 5:1?)        | Structural   | System     | U-04, U-01       | R-06, R-07       | After fundamentals | Not started |
| U-07 | Output shaft strength — self-tap holding, diameter adequate      | Structural   | Component  | —                | R-06             | Verify early       | Known undersized → Rev 00B |
| U-08 | Backlash — quantified                                            | Performance  | System     | U-01, U-03       | R-01             | After fundamentals | T-012 defined |
| U-09 | Backdrivability — quantified                                     | Performance  | System     | U-01, U-03       | R-04             | After fundamentals | T-013, T-006, T-008 defined |
| U-10 | Durability under sustained use                                   | Degradation  | System     | U-04, U-06       | R-05             | After fundamentals | Not started |

---

## 5. Test Log

<details>
<summary>Template — copy for each new test</summary>

### T-XXX: [Test Name]
**Date:** YYYY-MM-DD | **Unknown(s):** U-XX | **Requirement(s):** R-XX | **Test Level:** Component / Interface / Subsystem / System | **Prerequisites:** [What must pass first]

**Question:** What specifically are you trying to answer?

**Measured Quantity:** What physical measurement resolves it?

**Acceptance Criteria:** What constitutes pass/fail? (defined before testing)

**Setup & Equipment:**
- Tools:
- Parts to print:
- Fixtures:

**Procedure:**
1. ...
2. ...
3. ...

**Results:**


**Decision:** Pass / Fail / Inconclusive
- Root cause (if fail):
- Action:
- Design change required: Y/N
- Re-test needed: Y/N

</details>

### T-001: Root cause analysis of tight gear meshing
**Date:** — | **Unknown(s):** U-01 | **Requirement(s):** R-01, R-04 | **Test Level:** Interface | **Prerequisites:** Part dimensions (ring, planet, sun, carrier)
**Status: POSTPONED → Rev 00B**

**Reason for postponement:** Output shaft on Rev 00A is clearly too small and needs to be enlarged, requiring a larger top bearing. Not worth installing heat inserts into the current part — easier to reprint. Rev 00B will thread directly into plastic instead of using heat inserts, for simplicity.

**Scope (reduced for Rev 00A):** Skip backdrivability and backlash testing this revision. Limit to dimensional measurements only:
- Measure outer diameters of all gears
- Measure hole-to-hole spacing on the top carrier portion (planet center path diameter)
- Measure ring gear ID

**Question:** Why does the gearbox feel notchy when spinning?
- Are the gear meshing tolerances too tight?
- Is the carrier placing the planets slightly too far outwards?
- Are the tolerance stackups off due to 3D printer dimensional bias?
- Were any herringbone gears installed with wrong alignment?

**Measured Quantity:** Gear ODs, carrier planet center path diameter, ring gear ID — compare to nominal specs.

**Acceptance Criteria:** Dimensions within expected printer tolerance of nominal values.

**Setup & Equipment:**
- Tools: calipers, hex keys for disassembly
- Parts to print: —
- Fixtures: —

**Procedure:**
1. Measure outer diameters of sun, planet, and ring gears. Compare to nominal.
2. Measure carrier planet center path diameter (hole-to-hole spacing on top carrier).
3. Measure ring gear ID.
4. Visually inspect herringbone alignment on each planet — check if any are flipped.
5. Document all measurements and compare to CAD nominal values.

**Observations (2026-03-13 — hands-on inspection before formal measurements):**

**Carrier + planets in ring gear (no sun):** Rides smooth. Ring-planet interface is working well.

**Sun gear inserted into carrier + planets:** Very clicky. Sun-planet meshing is not right. On closer inspection, at least one planet appears to have incorrect herringbone alignment — the subtle helix angle makes it easy to install wrong.

**Backlash observation:** With sun gear in, noticeable backlash is present. This suggests the dimensional tolerances may actually be fine — the clickiness is from mesh misalignment, not interference.

**3D printer bias hypothesis (noted, not primary cause):**
If the printer biases dimensions larger, sun-planet clearance gets squeezed (both ODs grow into the same gap) while ring-planet clearance is roughly self-compensating (ring ID and planet OD both grow outward). Worth keeping in mind for future tolerance analysis, but the herringbone misalignment is the dominant issue right now.

**Decision: switch to spur gears for Rev 00B.**
The herringbone helix angle is very slight and likely not providing meaningful benefit at this scale. It over-constrains the mesh and creates an assembly error mode (incorrect alignment) that's hard to detect visually. Spur gears eliminate this problem entirely.

**Results:** Dimensional measurements still pending.

**Decision:** Partially resolved
- Primary root cause: herringbone alignment error on at least one planet, possibly compounded by the helix over-constraining the mesh
- Action: reprint gears as spur (0° helix) for Rev 00B
- Secondary: 3D printer dimensional bias may affect sun-planet clearance — measure to confirm, but not the main issue
- Design change required: Y — spur gears
- Re-test needed: Y (after spur gear reprint)

### T-002: Lid drag — over-constraint on carrier
**Date:** — | **Unknown(s):** U-03 | **Requirement(s):** R-04, R-09 | **Test Level:** Interface | **Prerequisites:** None
**Status: ROOT CAUSE IDENTIFIED — design change needed, testing may not be required**

**Question:** Is the lid adding parasitic drag by over-constraining the carrier axially?

**Root cause analysis (2026-03-13):**
The lid is doing double duty — constraining two separate things with one piece:
1. **Ring gear to housing** — bolts go through lid → ring gear, so clamping force sits directly on top of the ring gear
2. **Carrier top** — the lid bearing recess constrains the top of the carrier assembly

This creates a tolerance stackup problem. The carrier top position depends on:
- Bottom carrier main bearing seat on the body shaft (tolerance)
- Three planet gears sitting on bottom carrier shoulders (height tolerance)
- Bearing press-fit depth into planet bores (height tolerance)
- Top carrier shoulder contact with planet bearings (height tolerance)

Minor imperfections at any of these interfaces cause the carrier assembly to sit slightly higher than nominal. When the lid is clamped down, it presses on the top carrier shaft → parasitic drag.

**Design solutions to explore:**
1. **Add axial clearance** — increase gap between lid bearing recess and carrier top shaft (quickest fix)
2. **Deepen lid bearing recess** — more space for the top bearing, reducing interference with carrier
3. **Space the lid out further** — shims or taller standoffs between lid and ring gear

Note: slight axial play on the carrier is likely acceptable. Risk: bottom carrier bearing surfaces could slide slightly outward, causing bearing wobble on the shoulder surfaces. But immediate priority is eliminating the drag.

**Original test procedure (retained for reference):**
1. With gearbox fully assembled, spin motor by hand and note resistance.
2. Remove lid. Spin output again under same conditions.
3. Compare — if noticeably freer without lid, the lid is over-constraining.

**Decision:** Design change for Rev 00B
- Root cause: tolerance stackup across carrier assembly causes lid to press on carrier top
- Action: brainstorm lid constraint redesign — decouple ring gear clamping from carrier constraint
- Design change required: Y
- Re-test needed: verify fix in Rev 00B

### T-003: Carrier bearing shoulder deformation under bolt torque
**Date:** 2026-03-13 (visual inspection) | **Unknown(s):** U-04 | **Requirement(s):** R-05, R-06 | **Test Level:** Component | **Prerequisites:** None

**Question:** Does the 3D-printed carrier bearing shoulder deform or creep when the carrier bolts are tightened? Could this affect bearing preload or carrier alignment?

**Measured Quantity:** Shoulder dimensions before and after bolt torque is applied.

**Acceptance Criteria:**
- Shoulder dimension change < 0.1 mm after tightening to assembly torque
- No visible cracking, whitening, or permanent deformation

**Setup & Equipment:**
- Tools: calipers (or dial indicator), torque wrench / hex key, marker for reference points
- Parts to print: —
- Fixtures: —

**Procedure:**
1. Measure carrier bearing shoulder height/diameter with calipers before assembly.
2. Assemble carrier halves, tighten bolts to normal assembly torque.
3. Re-measure shoulder dimensions.
4. Visually inspect for cracks, whitening, or deformation at the shoulder.
5. Leave assembled for 30+ min, re-measure to check for creep.

**Results (2026-03-13 — visual inspection post-run):**
- **Bottom carrier shoulders: GOOD.** No visible deformation, shoulders intact.
- **Top carrier shoulders: PRINT QUALITY ISSUE.** The top carrier is printed with output shaft facing up (to get clean shoulder surface for the top lid bearing). This sacrifices the planet bearing shoulders on the top carrier — they have significant print artifacts and imperfections from being on the overhang/support side.

**Print orientation trade-off:** Output shaft up → good top bearing surface, bad planet bearing shoulders. This is a fundamental conflict in the current design.

**Design solutions to explore for Rev 00B:**
1. **Better support strategy** — improve support type/settings to get cleaner planet bearing shoulders
2. **Eliminate printed shoulders entirely** — use metal spacers on the inner bearing race instead of 3D printed shoulders. Top carrier becomes a flat plate (trivial to print). Bottom carrier walls extend further up to capture the planets. Still allows indexing if needed. Trade-off: more purchased parts.
3. **Change print orientation / geometry** — make bearing shoulders the same height as the gear cutouts, so when printed flat (output shaft up), the planet bearing shoulder faces are in direct contact with the build plate → much better surface quality. The clearance pockets between shoulders would still print fine.

**Decision:** Inconclusive (no dimensional measurement yet, but print quality issue identified)
- Root cause: print orientation trade-off — can't get good surfaces on both top bearing shoulder AND planet bearing shoulders simultaneously with current geometry
- Action: explore design alternatives (options 1–3 above) for Rev 00B
- Design change required: likely Y
- Re-test needed: Y (after Rev 00B redesign)

### T-004: Carrier half indexing — clocking under load
**Date:** YYYY-MM-DD | **Unknown(s):** U-05 | **Requirement(s):** R-01 | **Test Level:** Interface | **Prerequisites:** T-003 (carrier shoulder must not be deforming)

**Question:** Can the two carrier halves rotate relative to each other (clock) when loaded? If so, this would shift planet positions and affect backlash.

**Measured Quantity:** Relative rotation between carrier halves under applied torque.

**Acceptance Criteria:**
- No visible or measurable relative motion between halves under hand-applied torsion
- No gap opening at the parting line

**Setup & Equipment:**
- Tools: marker (draw witness lines across parting line), calipers, hex keys
- Parts to print: —
- Fixtures: method to grip each half independently (e.g., clamp housing, twist output)

**Procedure:**
1. Assemble carrier with planets installed and bolts tightened to normal torque.
2. Draw witness marks across the carrier parting line with a fine marker.
3. Grip one half (via housing constraint) and apply torsion to the other half by hand — try to twist them in opposite directions.
4. Check witness marks for any shift. Check parting line for gap opening.
5. If possible, measure with dial indicator on one half while loading the other.

**Results (2026-03-13):**

**Quick physical check:** By hand, able to twist the two carrier halves relative to each other. Measured roughly ~0.5 mm deflection at the outer edge of the carrier (would need to be extrapolated to angular deflection for a proper number).

**Load path analysis — clocking is not a realistic failure mode in operation:**
The planets orbit inside the ring gear, and the planet bearing pins span between both carrier halves. The tangential force from each orbiting planet acts on the pin, pushing both carrier halves in the same rotational direction simultaneously. Neither half is driven independently — they're both carried by the same pins. The bolts hold the sandwich together axially, but they aren't transferring torque between the halves.

For clocking to occur in operation, there would need to be a torsional load path through one half but not the other. That doesn't exist in this geometry — the output shaft is rigidly part of the same assembly being driven as a unit.

**Conclusion:** The ~0.5 mm of play exists (bolts + clearances allow it), but there's no operational load that would drive it. Clocking is not a concern for Rev 00A or likely Rev 00B. If indexing is added in a future revision, it would be for assembly repeatability, not for resisting in-service loads.

**Decision:** Not a concern
- Root cause: N/A — failure mode doesn't have a driving force in the actual load path
- Action: no design change needed for clocking. Indexing may still be added later for assembly convenience.
- Design change required: N
- Re-test needed: N

### T-005: Carrier bolt torque vs planet rotation resistance
**Date:** 2026-03-13 | **Unknown(s):** U-04 | **Requirement(s):** R-04, R-05 | **Test Level:** Component/Interface | **Prerequisites:** None

**Question:** How does carrier bolt torque affect planet rotation resistance? Does tightening the bolts deform the bearing shoulders enough to bind the planets?

**Measured Quantity:** Qualitative/quantitative planet rotation resistance at various carrier bolt torques.

**Acceptance Criteria:**
- Planet rotation should remain free across the usable bolt torque range
- If resistance increases significantly with torque, shoulder deformation is confirmed as a problem

**Setup & Equipment:**
- Tools: hex key, torque reference (or controlled incremental tightening)
- Parts to print: —
- Fixtures: —

**Procedure:**
1. Assemble carrier with planets and bearings installed.
2. Set carrier bolts to a light torque. Spin each planet by hand — note resistance.
3. Incrementally increase bolt torque. After each step, re-check planet resistance.
4. Note the torque level at which resistance noticeably increases (if it does).
5. Document via video.

**Results (2026-03-13):**

| Step | Bolt State | Planet Resistance | Notes |
|------|-----------|-------------------|-------|
| 1 | 1.1 Nm (minimum of torque wrench range) | Noticeable resistance on all 3 planets. Not hard to spin, but definitely not free. | None spin freely |
| 2 | Backed off 1 full turn from 1.1 Nm | All 3 spin very freely, smooth. | Some audible rubbing — likely shoulder surfaces or print artifacts. Carrier is not tight (play present). |
| 3 | Re-torqued incrementally (star pattern, 1/8 turn steps) until no play in carrier but still flex | 1 of 3 planets spins freely, 2 have slight drag | Carrier still has flex. Difficult to find a torque that eliminates carrier play without binding at least some planets. |

**Observations:**
- There's a narrow window between "carrier has play" and "planets bind" — the shoulders are sensitive to clamping force
- Planet bearings have metal shields, so slight drag is less concerning for contamination
- The slight drag probably isn't performance-critical for this prototype, but confirms the shoulder design is marginal
- Consistent with T-003 findings — print quality on top carrier shoulders is contributing to the sensitivity

**Decision:** Fail (marginal)
- Root cause: 3D printed bearing shoulders deform under bolt torque, narrowing the bearing bore and adding drag. Print quality issues on top carrier shoulders (T-003) compound the problem.
- Action: Rev 00B shoulder redesign — see `prototypes/rev00b/changes.md` item 4
- Design change required: Y
- Re-test needed: Y (after Rev 00B)

### T-006: Friction characterization — Coulomb + viscous model
**Date:** YYYY-MM-DD | **Unknown(s):** U-09 | **Requirement(s):** R-04, R-09 | **Test Level:** System | **Prerequisites:** Motor + encoder + ODrive running, gearbox assembled

**Question:** What is the gearbox's friction torque as a function of speed? What are the Coulomb (static) and viscous (speed-dependent) friction components?

**Measured Quantity:** Motor torque current ($I_q$) at constant output velocities. Friction torque $\tau_f = K_t \cdot I_q$ at each speed, where $K_t$ is the motor torque constant.

**Acceptance Criteria:**
- Reflected friction torque < 1 Nm across speed range (R-04 backdrivability requirement)
- Friction model should be approximately linear ($\tau_f = \tau_c + b\omega$) — significant nonlinearity indicates binding or interference

**Setup & Equipment:**
- Tools: ODrive + motor + encoder, computer with odrivetool / Python API
- Parts to print: —
- Fixtures: gearbox output shaft free (no load attached)

**Procedure:**
1. Configure ODrive in velocity control mode.
2. Command constant output velocities: 0.5, 1, 2, 5, 10 rev/s (adjust range based on motor limits and gear ratio).
3. At each speed, let velocity settle for 2–3 seconds, then log `Iq_measured` for 5 seconds.
4. Repeat in both directions (CW and CCW) to check for asymmetry.
5. Compute friction torque at each speed: $\tau_f = K_t \cdot \overline{I_q}$.
6. Plot $\tau_f$ vs $\omega$. Fit a line: intercept = Coulomb friction $\tau_c$, slope = viscous coefficient $b$.

**Results:**


**Decision:** Pass / Fail / Inconclusive
- Root cause (if fail):
- Action:
- Design change required: Y/N
- Re-test needed: Y/N

### T-007: Step response — system dynamics
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (characterization) | **Test Level:** System | **Prerequisites:** Motor + encoder + ODrive running, gearbox assembled

**Question:** What are the dynamic characteristics of the actuator (rise time, overshoot, settling time, steady-state error)? How does the gearbox affect the plant model compared to the motor alone?

**Measured Quantity:** Output position, velocity, and $I_q$ vs time in response to a position step command.

**Acceptance Criteria:**
- System reaches commanded position and settles (no sustained oscillation)
- Overshoot < 10% (adjustable via gains, but baseline matters)
- Steady-state error < 0.5° at output (R-01 backlash feeds into this)

**Setup & Equipment:**
- Tools: ODrive + motor + encoder, computer with odrivetool / Python API
- Parts to print: —
- Fixtures: gearbox output shaft free (no load attached)

**Procedure:**
1. Configure ODrive in position control mode with default PID gains.
2. Command a 1-revolution step at the output shaft (= 5 rev at motor).
3. Log position, velocity, and $I_q$ at max sample rate throughout the transient.
4. Repeat 3–5 times for consistency.
5. Plot position vs time. Extract: rise time ($t_r$, 10–90%), overshoot (%), settling time ($t_s$, ±2%), steady-state error.
6. Plot velocity and $I_q$ vs time on the same timeline for a complete picture.
7. Optional: repeat with different step sizes (0.25, 0.5, 2 rev) to check linearity.

**Results:**


**Decision:** Pass / Fail / Inconclusive
- Root cause (if fail):
- Action:
- Design change required: Y/N
- Re-test needed: Y/N

### T-008: Backdriving torque — passive resistance
**Date:** YYYY-MM-DD | **Unknown(s):** U-09 | **Requirement(s):** R-04 | **Test Level:** System | **Prerequisites:** Motor + encoder + ODrive running, gearbox assembled

**Question:** How much torque does it take to backdrive the gearbox through the output shaft when the motor is not actively controlled? This is the true backdrivability metric for a QDD.

**Measured Quantity:** $I_q$ induced by back-EMF when the output shaft is turned by hand, plus the corresponding output velocity. Backdriving torque $\tau_{bd} = K_t \cdot I_q \cdot N$ (reflected to output through gear ratio $N = 5$).

**Acceptance Criteria:**
- Backdriving torque < 1 Nm at output (R-04)
- Should feel light and smooth by hand — no cogging, no sticky spots

**Setup & Equipment:**
- Tools: ODrive + motor + encoder, computer with odrivetool / Python API
- Parts to print: —
- Fixtures: gearbox mounted so output shaft is accessible for hand turning

**Procedure:**
1. Set ODrive to idle state (no active control) or current control mode commanding 0A.
2. Slowly rotate the output shaft by hand at roughly constant speed (~0.5–1 rev/s).
3. Log `Iq_measured` and encoder velocity continuously.
4. Repeat in both directions.
5. Compute reflected backdriving torque: $\tau_{bd} = K_t \cdot |I_q| \cdot N$.
6. Plot $\tau_{bd}$ vs output position — look for periodic variation (indicates cogging or gear mesh effects).
7. Note qualitative feel: smooth, notchy, sticky spots, etc.

**Results:**


**Decision:** Pass / Fail / Inconclusive
- Root cause (if fail):
- Action:
- Design change required: Y/N
- Re-test needed: Y/N

### T-009: Motor Kt verification (baseline)
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (baseline) | **Test Level:** Component | **Prerequisites:** ODrive + motor + encoder configured

**Question:** Does the motor behave as expected at no-load? Is the effective $K_t$ consistent with the 150KV rating ($K_t = 0.0551$ Nm/A)?

**Measured Quantity:** $I_q$ at constant low velocity, no load.

**Acceptance Criteria:** No-load $I_q$ < 1A at low speed (2 rev/s). No erratic behavior.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 0.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-010: Motor cogging & friction profile (baseline)
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (baseline) | **Test Level:** Component | **Prerequisites:** T-009 pass

**Question:** What is the motor's cogging torque signature and friction profile? (Needed to isolate gearbox effects later.)

**Measured Quantity:** $I_q$ vs rotor position at slow constant velocity (~0.5 rev/s).

**Acceptance Criteria:** Periodic cogging pattern visible, roughly symmetric CW/CCW.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 0.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-011: Motor friction vs speed — no load (baseline)
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (baseline) | **Test Level:** Component | **Prerequisites:** T-009 pass

**Question:** What is the motor's friction torque as a function of speed? ($\tau_f = \tau_c + b\omega$)

**Measured Quantity:** Average $I_q$ at 5–6 constant speeds (1–20 rev/s), both directions.

**Acceptance Criteria:** Roughly linear friction vs speed. No erratic jumps.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 0.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-012: Output shaft backlash measurement
**Date:** YYYY-MM-DD | **Unknown(s):** U-08 | **Requirement(s):** R-01 | **Test Level:** System | **Prerequisites:** Gearbox assembled, motor shaft locked

**Question:** What is the angular backlash at the output shaft?

**Measured Quantity:** Angular play (degrees) at output with input locked. Measured at 4+ positions around one revolution.

**Acceptance Criteria:** Backlash ≤ 0.5° (R-01 hard requirement).

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 1.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-013: Hand backdriving — qualitative + rough torque
**Date:** YYYY-MM-DD | **Unknown(s):** U-09 | **Requirement(s):** R-04 | **Test Level:** System | **Prerequisites:** Gearbox assembled

**Question:** How much torque to backdrive the output shaft by hand? Smooth or notchy?

**Measured Quantity:** Force on kitchen scale via lever arm → torque. Qualitative feel notes.

**Acceptance Criteria:** Backdriving torque < 1 Nm (R-04). Smooth feel preferred.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 1.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-014: Motor step response (baseline)
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (baseline) | **Test Level:** Component | **Prerequisites:** T-009 pass

**Question:** What is the motor's step response without the gearbox? (Baseline for T-007 comparison.)

**Measured Quantity:** Position, velocity, $I_q$ vs time after a 1-rev position step command. Extract: rise time, overshoot, settling time, steady-state error.

**Acceptance Criteria:** Clean second-order response, consistent across 3–5 repetitions.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 0.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-015: Plant identification from step response data
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — | **Test Level:** System | **Prerequisites:** T-014, T-007 complete

**Question:** What is the plant transfer function $G(s)$ for the motor alone and motor+gearbox? What are $J$ (inertia) and $b$ (viscous friction)?

**Measured Quantity:** Fitted transfer function parameters from step response data using scipy.

**Acceptance Criteria:** Model prediction matches measured step response within 10% on rise time and overshoot.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 3.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-016: Frequency response — Bode plot
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (characterization; related to R-11 but does not directly validate 600 RPM) | **Test Level:** System | **Prerequisites:** T-015 (for validation)

**Question:** What is the actuator's bandwidth? Does the measured Bode plot match the identified $G(s)$?

**Measured Quantity:** Gain and phase vs frequency (0.5–50 Hz) for motor alone and motor+gearbox.

**Acceptance Criteria:** Measured Bode plot matches predicted Bode plot from T-015 model. Bandwidth identified.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 3.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-017: Impedance control — virtual spring
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (QDD capability demo; R-04 validated by T-008/T-013) | **Test Level:** System | **Prerequisites:** T-015 (plant model for tuning)

**Question:** Can the actuator behave as a virtual spring with tunable stiffness $K$?

**Measured Quantity:** Force vs displacement at output (should be linear, slope = $K$). Qualitative feel.

**Acceptance Criteria:** Linear force-displacement relationship. Smooth feel. Returns to setpoint. No oscillation at chosen $K$.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 4.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-018: Impedance control — virtual spring-damper
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — (QDD capability demo) | **Test Level:** System | **Prerequisites:** T-017

**Question:** Can damping be added to stabilize higher stiffness values? Does the spring-damper interaction feel natural?

**Measured Quantity:** Position vs time (damped oscillation after displacement). Torque vs velocity (damping curve).

**Acceptance Criteria:** Damped return to setpoint. Higher $K$ achievable with $B$ than without. Smooth feel.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 4.

**Results:**

**Decision:** Pass / Fail / Inconclusive

### T-019: Variable impedance demo (stretch goal)
**Date:** YYYY-MM-DD | **Unknown(s):** — | **Requirement(s):** — | **Test Level:** System | **Prerequisites:** T-018

**Question:** Can stiffness and damping be adjusted in real time via GUI sliders while interacting with the output?

**Measured Quantity:** Demo video + logged $K$, $B$, position, torque time series.

**Acceptance Criteria:** Smooth real-time parameter adjustment. Visually demonstrable change in feel. No instability during transitions.

**Procedure:** See `testing/test-campaign-rev00b.md` Phase 4.

**Results:**

**Decision:** Pass / Fail / Inconclusive

---

## 6. Revision History

| Date | Rev | Description |
|------|-----|-------------|
| 2026-03-16 | G | Expanded campaign to 5 phases. Added T-014 (motor step response baseline), T-015 (plant identification), T-016 (Bode plot), T-017/T-018/T-019 (impedance control). Full campaign in `test-campaign-rev00b.md`. |
| 2026-03-16 | F | Added T-009 through T-013 for Rev 00B quantitative testing campaign. T-009/010/011 = motor baseline (Phase 0). T-012 = backlash. T-013 = hand backdriving. Created `test-campaign-rev00b.md` with phased test plan. |
| 2026-03-13 | E | T-001 postponed → Rev 00B. T-002 root cause identified (lid over-constraint). T-003 visual inspection (print quality issue on top carrier). T-004 resolved — load path analysis shows clocking not a real failure mode, U-05 deprioritized. T-005 added + completed (bolt torque vs planet resistance, marginal fail). U-07 known undersized. Rev 00B changes consolidated in `prototypes/rev00b/changes.md`. |
| 2026-03-11 | C | Merged U-02 into U-01 (same root cause). Added T-004 (carrier indexing). Added ID permanence convention. Updated R-04 spec. |
| 2026-03-08 | A | Initial tracker created. Unknowns populated from prototype notes. |
