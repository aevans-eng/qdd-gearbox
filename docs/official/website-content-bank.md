# QDD Gearbox — Website Content Bank
> Consolidated reference for portfolio page write-ups.
> Source files referenced inline. Last updated: 2026-03-13.

---

## Project Overview
*Sources: goals-and-scope.md, design-requirements.md, assembly-profile.md*

A quasi-direct-drive (QDD) actuator built around an FDM 3D-printed 5:1 planetary gearbox, interfacing with a BLDC motor, magnetic encoder, and ODrive controller. The defining property of a QDD is **transparency** — the gearbox must be backdrivable with low friction and minimal backlash, so the motor can feel and respond to external forces.

**Key specs:**
- Gear ratio: 5:1 (R48/P18/S12, 3 planets, cycloidal tooth profile)
- Backlash target: ≤ 0.5 deg
- Friction torque: < 1 Nm (motor disconnected) — benchmarked against CubeMars AK70-10 (~0.97 Nm)
- Peak torque: 16 Nm | Continuous: 12 Nm
- Efficiency target: > 90%
- Budget: < $120 CAD
- Weight target: < 2 kg
- Manufacturing: FDM only (Bambu P1S), all off-the-shelf + printed parts, no special tools
- Printer: Bambu P1S, PLA/PETG

**Why it matters:** QDD actuators are the standard in legged robots and collaborative arms (e.g., Tesla Optimus). Designing one from scratch — including trade studies, parametric CAD, DFM for FDM, calibration, and structured testing — demonstrates actuator design competence end to end.

---

## Design Decisions
*Sources: trade-studies.md, design-process.md*

### Methodology
The design followed a structured sprint process: (1) establish quantifiable requirements, (2) research and brainstorm concepts, (3) rank via weighted trade studies (Pugh matrices), (4) define interfaces between domains, (5) detailed CAD with DFM built in. Key insight from the process: **the #1 failure mode in student robotics is not the gearbox itself, but how it attaches to the motor or how the magnet attaches to the shaft.** Interface definition was prioritized accordingly.

### Gear Type Selection

| Metric (Weight) | Planetary | Cycloidal | Drive Belt | Capstan | Strain Wave | Sequential |
|---|---|---|---|---|---|---|
| Cheapness (0.20) | 5 | 3 | 3.5 | 4 | 3.5 | 4.5 |
| Transparency (0.15) | 4 | 3.5 | 5 | 4 | 3 | 4 |
| Torque Density (0.10) | 4 | 4 | 3 | 3 | 5 | 2 |
| Precision (0.15) | 4 | 5 | 3.5 | 3 | 5 | 4 |
| DFM/DFA (0.15) | 4 | 3 | 4 | 3 | 3 | 4 |
| Efficiency (0.10) | 4.5 | 4 | 5 | 4.5 | 3.5 | 4 |
| Durability (0.15) | 5 | 4 | 4 | 4 | 3 | 5 |
| **Weighted Total** | **4.40** | 3.73 | 3.98 | 3.65 | 3.65 | 4.05 |

**Winner: Planetary.** Best balance of cost, efficiency, durability, and printability.

### Ratio Selection

| Metric (Weight) | 4:1 | **5:1** | 6:1 | 7:1 |
|---|---|---|---|---|
| Transparency (0.15) | 5 | 4.5 | 4 | 3.5 |
| Torque Density (0.20) | 4 | 4.5 | 4.5 | 5 |
| Durability (0.20) | 5 | 5 | 4.5 | 4 |
| **Weighted Total** | 4.80 | **4.83** | 4.60 | 4.53 |

**Winner: 5:1.** Best compromise between transparency and torque multiplication.

### Bearing Selection

| Metric (Weight) | **Ball** | Roller | Needle | Taper | Bushing | Crossed Roller |
|---|---|---|---|---|---|---|
| Cheapness (0.60) | 5 | 3 | 4 | 2 | 5 | 1 |
| Radial Loading (0.20) | 4 | 5 | 5 | 4 | 2 | 5 |
| **Weighted Total** | **4.05** | 3.00 | 3.60 | 2.70 | 3.65 | 2.60 |

**Winner: Ball bearings.** Cost-dominant weighting reflects the prototype budget constraint.

---

## CAD Architecture (CATIA V6)
*Sources: modeling-guide.md, skeleton-workflow.md, assembly-profile.md*

### Parametric Philosophy
The entire assembly is skeleton-driven: a master skeleton part (`SKL_Skeleton A.1`) contains all parameters, reference planes, and axes. Individual parts read from the skeleton via formulas and publications — they never reference each other directly. Changing a skeleton parameter propagates to every downstream part automatically.

### Core Principles
- **Single source of truth:** All positioning data lives in the skeleton. Parts don't define their own locations.
- **Parts constrain to skeleton, never to each other.** If Part A and Part B need to align, both reference the same skeleton geometry.
- **No B-Rep references.** Never reference edges or faces of solid bodies — sketch on planes, reference wireframe geometry. B-Rep refs break when features reorder.
- **Body-level patterning** over feature-level — more stable when upstream geometry changes.
- **Placeholder gears as geometric contracts** — define interface (pitch diameter, position) without tooth complexity. Real geometry swaps in and inherits the same constraints.

### Assembly Structure
```
QDD Master Assem
├── Gearbox_Master_Assem
│   ├── SKL_Skeleton (master reference, FIXED)
│   ├── gear_set (sun, planets, ring — placeholder + STEP import)
│   ├── carrier_assem (bottom/top halves, cutting_bodies, skeleton_refs)
│   ├── housing_assem (body, lid, cutting_bodies, bearings)
│   └── Bearings (6805-2RS x2)
├── MotorHousing (D6374 motor, enclosure cap/housing)
└── Engineering Connections
```

### Skeleton-Driven Workflow
- Sub-assemblies import skeleton geometry into a dedicated reference part (`skel_ref`), which is fixed. All other parts in the sub-assembly constrain to it.
- Cutting bodies (boolean tools for bearing pockets, bolt holes) reference only skeleton datums — survive STEP swaps and revision changes.
- "Chain of Zeros" positioning: Skeleton at (0,0,0) → sub-assembly constrained to skeleton midplane → parts constrained to sub-assembly origin. Ensures geometry pastes without offsets.

---

## Tolerancing & DFM
*Sources: tolerance-scheme.md, manufacturing-tips.md, assembly-profile.md*

### FDM Tolerancing Approach
Standard ISO fit designations (H7/k6, etc.) describe the *intent* — what the joint should behave like. FDM-specific offsets approximate those fits with 3D printing. Every bearing interface uses a separate named offset parameter in the skeleton (e.g., `main_bearing_shaft_offset = 0.10mm`), keeping nominal bearing dimensions pure.

**General FDM rules:**
- Accuracy: +/- 0.2mm
- Bores print undersized (~0.1-0.2mm) — model oversized to compensate
- Shafts print slightly oversized — model undersized to compensate
- Large diameters have more absolute error

### Bearing Fit Philosophy
All bearing interfaces target a **finger-press transition fit** — firm finger pressure seats the bearing, it clicks in and doesn't fall out. This departed from conventional practice (rotating ring = press fit) because FDM surface texture provides grip and backdrivability is the priority.

### Calibration Coupon Method
Before the full build, a test coupon was printed with representative features (bearing bore at 37.10mm, bearing shaft post at 25.10mm, planet bore at 14mm, clearance holes, heat-set insert pilots). Each feature was measured with calipers and compared to nominal. Results:

- **Main bearing bore (37.10mm):** Perfect finger-press fit. Validated.
- **Bearing shaft post (25.10mm):** Printed 25.01mm. Dimensionally correct, needs fit-test.
- **Planet bore (14.00mm):** Printed 13.75mm (-0.25mm). Offset increased to +0.15mm.
- **Small holes (3-5mm):** Significant undersizing (-0.4mm on M3). Offsets extrapolated, need v2 coupon validation.

### Key Offsets Applied to CATIA

| Interface | Offset Parameter | Value | Status |
|---|---|---|---|
| Housing bearing shaft | `main_bearing_shaft_offset` | +0.10mm | Validated |
| Carrier bearing bore | `carrier_bearing_bore_offset` | +0.10mm | Applied |
| Lid bearing bore | `lid_bearing_bore_offset` | +0.10mm | Validated |
| Carrier output shaft | `carrier_shaft_offset` | +0.10mm | Applied |
| Planet bearing bore | `planet_bearing_offset` | +0.15mm | Pending validation |
| Ring-to-housing bore | `ring_housing_diam_offset` | +0.30mm | Applied |

### DFM Lessons Learned
- **Heat-set inserts:** Model pilot hole at insert OD (not generic tables — those assume injection molding). Depth = 1.5x insert length. Use non-tapered soldering iron tip. Plate-press technique for flush seating.
- **Self-tapping holes validated:** M3: 2.6mm, M4: 3.6mm, M5: 4.6mm pilot holes — simpler than heat inserts for prototyping.
- **Print orientation trade-offs:** Critical bores vertical for roundness. Gear teeth printed flat. Carrier orientation creates a conflict — output shaft up gives good top bearing surface but bad planet bearing shoulders.
- **Shoulder bolts as dual-purpose parts:** D5mm shoulder screws serve as planet pins AND carrier clamshell fasteners, reducing BOM.

---

## Prototyping
*Sources: prototypes/rev00a/notes.md*

### Rev 00A Build Observations

**Fits (initial print):**
- Housing main bearing: slightly too loose (tight clearance, should be loose transition)
- Lid-to-bearing: good loose-medium transition fit
- Planet bearings: mostly loose-medium transition, one was clearance (tolerance inconsistency)
- M3 motor clearance holes: 0.13mm too tight
- Sun gear: very tight, needed pressing onto shaft. Bore enlarged from 10.05mm to 10.075mm.

**Reprints (Rev 00A iteration):**
- Bottom carrier shell and housing body reprinted with adjusted offsets
- Heat inserts abandoned in favor of self-tapping threads (validated with coupon)
- Skeleton offsets updated: `carrier_shaft_offset` 0.10 → 0.12, `carrier_bearing_bore_offset` 0.10 → 0.12, `main_bearing_shaft_offset` 0.10 → 0.12, `lid_step_clearance` 0.25 → 0.18

**Issues identified during assembly:**
- Lid adds drag when tightened — something is over-constrained (confirmed in T-002)
- Carrier planet bearing shoulders deform under bolt torque (confirmed in T-003/T-005)
- Gear meshing feels notchy — suspected herringbone alignment error (confirmed in T-001)
- Need text features on gears for assembly orientation
- Need better parameter naming in skeleton (unclear if higher value = tighter or looser)

---

## Testing & Iteration
*Sources: test-tracker.md, prototypes/rev00b/changes.md*

### Test Methodology
Testing follows a structured framework with full traceability:
- **Unknowns Register:** Each unknown (U-01 through U-10) is categorized by risk x uncertainty, mapped to requirements, and tracked through resolution.
- **Dependency Map:** Component → Interface → Subsystem → System. Tests resolve bottom-up.
- **Test entries** define the question, measured quantity, and acceptance criteria *before* testing. Results link back to unknowns and requirements.

### Test Results Summary

| Test | Question | Finding | Decision |
|---|---|---|---|
| **T-001:** Gear mesh root cause | Why does the gearbox feel notchy? | At least one planet has incorrect herringbone alignment. Carrier + planets in ring (no sun) = smooth. Sun inserted = clicky. Backlash present, suggesting tolerances may be OK — problem is mesh misalignment, not interference. | **Switch to spur gears** for Rev 00B. Herringbone helix too slight to benefit at this scale, over-constrains mesh, creates undetectable assembly error. |
| **T-002:** Lid drag | Is the lid over-constraining the carrier? | Yes. Lid double-constrains: (1) clamps ring gear to housing and (2) constrains carrier top via bearing recess. Tolerance stackup through carrier assembly pushes carrier higher than nominal → lid presses on carrier → drag. | **Decouple constraints** — added extra axial clearance on carrier top shaft for Rev 00B. |
| **T-003:** Carrier shoulder deformation | Does the printed shoulder deform under bolt torque? | Bottom carrier shoulders: OK. Top carrier shoulders: print quality issues — output-shaft-up orientation gives good top bearing surface but bad planet bearing shoulders (overhang artifacts). | **Print strategy change** — top carrier loses walls, bottom carrier gets all walls. Eliminates overhang on shoulder surfaces. |
| **T-004:** Carrier half indexing | Can carrier halves clock under load? | ~0.5mm play exists by hand. But load path analysis shows no operational force drives clocking — planets push both halves in the same direction via shared pins. | **Not a concern.** No design change needed. |
| **T-005:** Bolt torque vs planet resistance | Does tightening carrier bolts bind the planets? | Narrow window between "carrier has play" and "planets bind." At 1.1 Nm: noticeable drag. Backed off 1 turn: all spin freely. Re-torqued incrementally: 1/3 free, 2/3 slight drag. | **Marginal fail.** Confirms shoulder design is sensitive. Rev 00B shoulder redesign required. |

### Rev 00B Scoped Changes (Must-Have)

| Change | Source | Part |
|---|---|---|
| Switch herringbone → spur gears (0 deg helix) | T-001 | All gears |
| Enlarge output shaft + larger top bearing | T-001, U-07 | Carrier top |
| Fix planet bearing shoulder print quality | T-003, T-005 | Carrier top/bottom |
| Decouple lid constraint (ring gear vs carrier) | T-002 | Lid |
| Thread into plastic (no heat inserts) | T-001 | Carrier |

---

## Project Timeline
*Sources: work logs, test-tracker.md revision history*

| Date | Milestone |
|---|---|
| 2026-01-04 | Design sprint — requirements, trade studies, concept selection, initial CAD |
| 2026-02-14 | Interior-out dimensioning decision, carrier-planet interface design |
| 2026-02-19 | Calibration coupon v1 printed and measured |
| 2026-02-20 | Bearing fit philosophy established (transition fit everywhere), CATIA offsets updated |
| 2026-03-01 | Cycloidal gear parameter migration, STEP integration into skeleton assembly, real tooth geometry in master assembly |
| 2026-03-08 | Test tracker created, unknowns populated from prototype observations |
| 2026-03-11 | R-04 backdrivability spec rewritten (friction torque < 1 Nm), unknowns consolidated |
| 2026-03-13 | Rev 00A testing session — T-001 through T-005 completed/analyzed, Rev 00B changes scoped |

---

## Future Work (Placeholders)
- GD&T / formal engineering drawings
- Tolerance stack-up analysis (quantitative)
- Controls & motor integration (ODrive)
- Rev 00B printing & testing
- Durability testing under sustained use
- Backlash and backdrivability quantitative measurement
- Torque capacity verification (motor torque x 5:1)

---

## Available Visuals

### docs/images/
| File | Description |
|---|---|
| `full-assembly-cross-section.png` | Complete assembly stack, cross-sectioned — shows gear mesh, bearings, carrier, housing |
| `master-assembly-tree.png` | CATIA top-level assembly tree with housing and motor |
| `carrier-assembly-tree.png` | Carrier sub-assembly tree showing cutting_bodies and external refs |
| `housing-lid-detail.png` | Lid part showing external references from skeleton |
| `2026-02-14-carrier-planet-interface-sketch.png` | Hand sketch of carrier-planet cross-section and axial stack-up |
| `2026-03-01-20-43-gears-product-structure.png` | CATIA product tree with STEP import and gear_set structure |
| `2026-03-01-21-19-master-assembly-with-gears.png` | Master assembly cross-section with real cycloidal tooth geometry |

### prototypes/rev00a/photos/
| File | Description |
|---|---|
| `fun comparison pic to the first non skeleton model i made, when i was still learning the software.png` | Before/after comparison — early model vs current |
| `3DEXPERIENCE_*.png` (multiple) | CATIA screenshots of Rev 00A assembly |
| `comet_*.png` | Photo(s) of printed prototype |
| Various `.png` files | Additional prototype and CAD screenshots (review for portfolio-worthy shots) |
