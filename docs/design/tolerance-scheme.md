# Tolerance Scheme — QDD Planetary Gearbox

Every mating interface in the gearbox, with fit types, tolerance values, and critical stack-ups. Bridges ISO/ASME fit standards (for learning) with FDM-practical values (for implementation).

**Status:** Post-calibration v1 — applying coupon results to CATIA parameters. Planet gear print queued to validate bearing bore offset with a real part. Small hole offsets are approximate — planet print tests the critical bearing fit, remaining small features validated later.

**Key design facts (from discussion):**
- Lid step presses down onto ring gears (axial constraint)
- Ring gears slide into cylindrical housing bore, split at mid-height
- Shoulder screws = planet pins + carrier fasteners
- Carrier sits on bottom main bearing via lip; lid bearing catches top carrier
- Sun gear: press fit onto D-shaft (circle with flat)
- Herringbone planets: self-centering axially, floating
- No post-processing planned — everything as-printed
- Calibration coupon v1 printed 2026-02-19 — main bearing fit validated, planet bore and small holes need offset corrections
- CATIA parameters being updated with calibration-derived offsets (2026-02-20)

**Related docs:**
- `_archive/08-gdt-notes.md` — Datum reference frame and GD&T callouts
- `_archive/05-parts-list.md` — BOM with bearing/fastener specs
- `tolerancing-discussion.md` — Design Q&A (completed)

---

## Background: How ISO Fits Work

If you've never worked with ISO tolerance designations before, this section explains the system. Everything below in the interface tables will make more sense after reading this.

### The Problem Fits Solve

When two parts mate — a shaft going into a hole — you need to control how tight or loose that joint is. Too loose and things rattle. Too tight and you can't assemble it (or you crack the part). The ISO system gives engineers a standardized language to specify exactly how much clearance or interference a joint should have.

### Anatomy of a Designation: H7/k6

Every fit designation has two parts: **hole / shaft**.

```
    H  7  /  k  6
    │  │     │  │
    │  │     │  └── Tolerance grade (how precise the shaft must be)
    │  │     └───── Fundamental deviation (where the shaft sits relative to nominal)
    │  └────────── Tolerance grade (how precise the hole must be)
    └───────────── Fundamental deviation (where the hole sits relative to nominal)
```

### The Letter: Fundamental Deviation (Position)

The letter tells you **where** the tolerance zone sits relative to the nominal (exact) dimension.

**For holes** (uppercase letters):
```
                     Nominal
                        │
  A  B  C  D  ... G  H │ J  K  ... N  P  R  S  ...  Z
  ◄─── larger ─────────►│◄─── smaller ──────────────►
        (more clearance) │      (more interference)
```

**For shafts** (lowercase letters):
```
                     Nominal
                        │
  a  b  c  d  ... g  h │ j  k  ... n  p  r  s  ...  z
  ◄─── smaller ────────►│◄─── larger ──────────────►
        (more clearance) │      (more interference)
```

**Key letters to know:**

| Letter | Meaning |
|--------|---------|
| **H** (hole) | Starts exactly at nominal, goes up. The most common hole designation — "hole basis" system |
| **h** (shaft) | Starts exactly at nominal, goes down. Shaft at or below nominal |
| **g** (shaft) | Below nominal — guaranteed clearance in an H hole |
| **k** (shaft) | Straddles nominal — might be slightly above or below. Transition zone |
| **p** (shaft) | Above nominal — guaranteed interference in an H hole |

### The Number: IT Grade (Precision)

The number (called the **IT grade**) controls **how wide** the tolerance band is — i.e., how precisely the part must be made.

| IT Grade | Typical Tolerance at ⌀25mm | Used For |
|----------|---------------------------|----------|
| IT5 | ±0.004mm | Precision ground shafts |
| IT6 | ±0.006mm | Ground/precision turned shafts |
| IT7 | ±0.010mm | Reamed holes, good machining |
| IT8 | ±0.013mm | Standard machining |
| IT11 | ±0.065mm | Rough machining |
| IT14+ | ±0.26mm+ | Sheet metal, casting, **FDM printing** |

**Lower number = tighter tolerance = more expensive to make.**

For our QDD project, standard machining fits (IT6/IT7) describe what we *want* the joint to behave like. The FDM offsets in this doc are how we *approximate* those fits with 3D printing.

### The Three Fit Categories

When you combine a hole and shaft designation, you get one of three fit types:

```
  ┌──────────────┬──────────────┬──────────────┐
  │  CLEARANCE   │  TRANSITION  │ INTERFERENCE  │
  │              │              │               │
  │  Shaft       │  Shaft       │   ████████    │
  │  ┌──────┐    │  ┌───╫──┐   │  ┌██████──┐   │
  │  │      │    │  │   ║  │   │  │████████ │   │
  │  │ gap  │    │  │   ║  │   │  │████████ │   │
  │  │      │    │  │   ║  │   │  │████████ │   │
  │  └──────┘    │  └───╫──┘   │  └██████──┘   │
  │   Hole       │   Hole       │   Hole        │
  │              │  may be      │   shaft is    │
  │  always a    │  clearance   │   larger      │
  │  gap         │  or press    │   than hole   │
  └──────────────┴──────────────┴──────────────┘
```

| Category | Example | Shaft vs Hole | Typical Use |
|----------|---------|--------------|-------------|
| **Clearance** | H7/g6 | Shaft always smaller | Sliding/rotating parts, easy assembly |
| **Transition** | H7/k6 | Could go either way | Locating bearings in stationary housings |
| **Interference (Press)** | H7/p6 | Shaft always larger | Locking parts together, bearing on rotating shaft |

### Fits Used in This Gearbox

Here's every fit in this doc mapped to why it was chosen:

| Interface | Fit | Category | Reasoning |
|-----------|-----|----------|-----------|
| Bottom bearing ID → Housing shaft | k6 | Transition | Housing is stationary — inner race sits snug on shaft |
| Bottom bearing OD → Carrier bore | H7/k6 | Transition | Finger press — FDM texture prevents creep, maximizes backdrivability |
| Top bearing OD → Lid bore | H7/k6 | Transition | Lid is stationary — bearing should sit snug but be hand-assemblable |
| Carrier output shaft → Top bearing ID | k6 | Transition | Finger press — matches gold standard feel |
| Planet bearing → Planet gear bore | H7/k6 | Transition | Finger press — same feel as main bearing, validates with planet print |
| Shoulder screw → Planet bearing ID | g6 | Clearance | Pin is stationary — bearing spins freely on it |
| Ring gear → Housing bore | H7/h6 | Clearance | Ring drops in for assembly, lid holds it axially |
| Sun gear → Motor shaft | H7/p6 | Press fit | Must transmit full motor torque without slipping |
| Lid step → Housing bore | H7/h6 | Clearance | Self-centering fit, must be assemblable |

### "Hole Basis" System

You'll notice every hole above is **H** (or the bore is the reference). This is the **hole basis** system — you make the hole to a standard size and adjust the shaft to get the fit you want. This is the most common approach because:

1. Holes are harder to adjust after manufacturing (especially bored/reamed holes)
2. Shafts are easier to turn down or grind
3. For bearings, the bore/OD is fixed by the manufacturer — you adjust the housing bore and shaft to match

### How This Connects to FDM

ISO fits assume machined metal parts with micron-level control. FDM printing operates at ±0.1-0.3mm — orders of magnitude looser. So we can't achieve a true H7/k6, but we can use the *intent* of each fit:

| ISO Intent | What We Do in FDM |
|-----------|-------------------|
| Transition fit (snug, assemblable) | Oversize bore by 0.10mm — printing shrinks it to approximately snug |
| Press fit (locked together) | Model at nominal or slight interference — printing creates natural press |
| Clearance fit (slides freely) | Oversize bore by 0.2-0.3mm — ensures parts slide together despite FDM variation |

The ISO designations in this doc serve two purposes:
1. **Learning** — you know what fit an engineer would specify for each interface
2. **Intent** — the FDM offsets are calibrated to approximate that behavior

---

## How to Read This Document

| Field | Meaning |
|-------|---------|
| **Function** | What this fit needs to accomplish |
| **ISO Designation** | Standard fit code (e.g., H7/g6) — for learning/documentation |
| **Nominal** | The bearing/component dimension (fixed by manufacturer) |
| **CATIA Today** | What the skeleton currently models this as |
| **FDM Target** | What we should model to get a good as-printed fit |
| **New Parameter** | Parameter to add to skeleton for the clearance/offset |
| **Priority** | Critical / Important / Standard |

**FDM offset convention:** Bores print smaller than modeled. Shafts print larger than modeled. So:
- Bores: model **oversized** (add clearance to nominal)
- Shafts: model **undersized** (subtract clearance from nominal)

---

## FDM Bearing Fit Philosophy

**Decision (2026-02-20):** All bearing interfaces target a **finger-press transition fit** — the same feel as the main bearing in calibration coupon v1 (⌀37.10mm bore, 6805-2RS pushed in by hand with firm finger pressure).

### Why we departed from convention

The textbook rule is: *the rotating ring gets an interference/press fit* to prevent bearing creep (race slowly spinning in its housing). For machined metal parts with micron-level control, this is correct and important.

**For our 3D-printed QDD, the priorities are different:**

| Factor | Convention says | Our situation |
|--------|----------------|---------------|
| Fit precision | Achievable to ±0.01mm | FDM gives ±0.1-0.3mm — can't achieve true press fits reliably |
| Top priority | Bearing life, load capacity | **Backdrivability** — friction kills the whole QDD concept |
| Axial loads | Depend on gear geometry | Herringbone gears self-center → minimal axial thrust on bearings |
| Load level | Often high, continuous | Low torque, prototype loads |
| Surface texture | Smooth metal needs interference for grip | FDM layer lines provide natural grip even in transition fits |
| If creep occurs | Catastrophic in production | Fixable — loctite retaining compound or reprint with offset tweak |

### The rule for this gearbox

**Every bearing interface targets the coupon v1 main bearing feel:** firm finger press, clicks into place, doesn't fall out. This applies to both stationary and rotating rings.

The ISO designations in this doc still show what a conventional engineer would specify — for learning. The FDM offsets implement the transition-fit-everywhere strategy.

---

## 1. Radial Fits (Bore/Shaft Interfaces)

### 1.1 Bottom Main Bearing ID → Housing Body Shaft

> 6805-2RS inner race (⌀25mm) sits on a shaft/boss on the housing body

| Field | Value |
|-------|-------|
| **Function** | Housing body shaft locates the bottom bearing radially. The bearing ID sits on this shaft. Housing is stationary, so the inner race is stationary — it just needs to sit snugly without spinning on the shaft |
| **ISO Designation** | k6 (transition fit for stationary inner race on shaft) |
| **Nominal** | Bearing ID = 25.000mm |
| **CATIA Today** | `Main_bearing_ID = 25mm` — shaft modeled at exact nominal |
| **FDM Target** | Model shaft at **25.10mm** (+0.10mm). FDM shrinks shafts, so printed shaft ≈ 24.9-25.0mm → snug fit in bearing ID |
| **New Parameter** | `main_bearing_shaft_offset = 0.10mm` → shaft = `Main_bearing_ID + main_bearing_shaft_offset` |
| **Post-Processing** | If too tight: sand shaft lightly. If too loose: not recoverable without reprinting |
| **Priority** | **Critical** |

**Shoulder context:** Your skeleton has `main_bearing_shoulder_OD = 34.5mm` and `main_bearing_shoulder_ID = 27.4mm`. The shoulder supports the bearing face axially. The shaft locates it radially.

---

### 1.2 Bottom Main Bearing OD → Carrier Plate Bore

> 6805-2RS outer race (⌀37mm) sits in the bottom carrier plate bore

| Field | Value |
|-------|-------|
| **Function** | The bottom carrier plate has a bore/shoulder that captures the bottom bearing OD. The carrier rotates, so the outer race rotates with it |
| **ISO Designation** | H7/k6 (transition fit) — conventionally would be P7 press fit for rotating outer race, but we're targeting transition fit for backdrivability (see "FDM Bearing Fit Philosophy") |
| **Nominal** | Bearing OD = 37.000mm |
| **CATIA Today** | Uses `Main_bearing_OD = 37mm` |
| **FDM Target** | Model bore at **37.10mm** (+0.10mm). Same offset as lid bore — targeting the gold standard finger-press feel from coupon v1 |
| **New Parameter** | `carrier_bearing_bore_offset = 0.10mm` → bore = `Main_bearing_OD + carrier_bearing_bore_offset` |
| **Priority** | **Critical** |

**Why transition fit instead of press?** Conventional rule says rotating outer race needs press fit. But FDM surface texture provides enough grip at prototype loads, and backdrivability is the top priority for QDD.

**Creep risk is low:** The lid step constrains the ring gear and carrier axially — the bearing OD can't walk out. Retaining compound is also not a reliable fallback on low-surface-energy filaments (PLA/PETG). If creep does occur, reprint with a reduced bore offset.

---

### 1.3 Top Main Bearing OD → Lid Bore

> 6805-2RS outer race (⌀37mm) seats into lid bore

| Field | Value |
|-------|-------|
| **Function** | Locate top bearing in the lid. Lid is stationary, so the outer race is stationary — needs a transition fit (snug but assemblable) |
| **ISO Designation** | H7/k6 (transition fit) |
| **Nominal** | Bearing OD = 37.000mm (may change if top bearing size changes in future) |
| **CATIA Today** | Uses `Main_bearing_OD = 37mm` |
| **FDM Target** | Model bore at **37.10mm** (+0.10mm). FDM shrinks holes, so printed bore ≈ 36.9-37.0mm → snug fit |
| **New Parameter** | `lid_bearing_bore_offset = 0.10mm` → bore = `lid_bearing_OD + lid_bearing_bore_offset` |
| **Priority** | **Critical** |

**Note:** The lid prints face-down (open side up per A15), so the bearing bore is built up layer by layer — good for roundness. Uses separate `Lid_bearing_OD` parameter in case the top bearing changes size in the future.

---

### 1.4 Top Main Bearing ID → Carrier Output Shaft

> Carrier output shaft (⌀25mm) fits into top 6805-2RS inner race

| Field | Value |
|-------|-------|
| **Function** | Carrier rotates — the inner race sits snug on the output shaft |
| **ISO Designation** | k6 (transition fit) — conventionally would be k5 interference for rotating inner race, but targeting transition fit for backdrivability (see "FDM Bearing Fit Philosophy") |
| **Nominal** | Bearing ID = 25.000mm |
| **CATIA Today** | `Main_bearing_ID = 25mm` and `carrier_output_OD = 25.1mm` — offset already baked into param value |
| **FDM Target** | Model shaft at **25.10mm** (+0.10mm). FDM shrinks shafts, so printed shaft ≈ 24.9-25.0mm → snug fit in bearing ID |
| **New Parameter** | `carrier_shaft_offset = 0.10mm` → shaft OD = `Main_bearing_ID + carrier_shaft_offset` |
| **Post-Processing** | If too tight: sand shaft lightly. If too loose: not recoverable without reprinting |
| **Priority** | **Critical** |

**Why transition fit?** Conventionally the rotating inner race needs interference (k5). But FDM surface texture provides grip, and backdrivability is priority. The +0.10mm offset matches the gold standard from coupon v1. If the bearing slips on the shaft, apply loctite or reprint with a slightly larger offset.

---

### 1.5 Planet Bearing OD → Planet Gear Bore

> 685ZZ outer race (⌀14mm) press-fits into planet gear bore

| Field | Value |
|-------|-------|
| **Function** | Bearing and gear rotate together around the planet pin. Bearing must not spin inside the gear — that would mean the gear isn't transmitting torque through the bearing |
| **ISO Designation** | H7/k6 (transition fit) — conventionally would be P7 press fit for rotating outer race, but targeting transition fit for backdrivability (see "FDM Bearing Fit Philosophy") |
| **Nominal** | Bearing OD = 14.000mm (`carrier_bearing_OD = 14mm`) |
| **CATIA Today** | `planet_bearing_OD = 14mm` — modeled at nominal |
| **FDM Target** | Model bore at **14.15mm** (+0.15mm). Calibration: ⌀14.00 printed 13.75mm (−0.25mm). Expect ~13.90mm printed — ~0.10mm smaller than bearing OD (press fit). Adjust after planet print. |
| **New Parameter** | `planet_bearing_offset = 0.15mm` → bore = `planet_bearing_OD + planet_bearing_offset` = **14.15mm**. Value from Aaron's judgment. Validate with planet print. |
| **Post-Processing** | If bearing won't press in: carefully open bore with round needle file |
| **Priority** | **Critical** — 3 of these (one per planet), all must be consistent |

**Why this is tricky:** The planet gear is the *rotating* part here, while the inner race is clamped to the stationary pin (shoulder screw). So the *outer* race rotates with the gear. Conventionally this means interference fit, but we're targeting transition fit for backdrivability. FDM texture + low loads should prevent creep. The planet gear print will validate this — if the 685ZZ drops in too easily, reduce offset.

**Bearing shoulder context:** `planet_bearing_shoulder_OD = 12.4mm`, `planet_bearing_shoulder_ID = 6.6mm`. These shoulders in the carrier support the bearing faces axially.

**Inner race clearance relief:** The 685ZZ inner race OD must not contact the shoulder step face. If it does, the shoulder screw clamps the inner race against the step, binding the bearing (inner race can't rotate relative to outer race). A relief counterbore is needed on each end of the planet bore, sized to clear the inner race OD.

- **Measured:** 685ZZ inner race OD = **7mm**
- Relief diameter: `planet_inner_race_OD + 0.5mm` = **7.5mm**
- Depth: enough that inner race face doesn't bottom out when bearing is fully seated
- On both ends (one per bearing)
- **Doubles as bearing removal path:** rod inserted through shoulder screw hole from opposite end catches inner race face, drives bearing out
- **Geometry check:** shoulder step OD (12.4mm) > inner race OD (7mm) ✓ — step contacts outer race face and clears inner race

---

### 1.6 Planet Bearing ID → Shoulder Screw (Planet Pin)

> Shoulder screw ⌀5mm through 685ZZ inner race (⌀5mm ID)

| Field | Value |
|-------|-------|
| **Function** | Inner race is clamped stationary by shoulder screw. Planet + outer race spin around it. Pin must be smooth fit in bearing — standard bearing-on-shaft fit |
| **ISO Designation** | g6 (sliding fit) — bearing ID on shoulder screw shoulder (hardware-to-hardware) |
| **Nominal** | Bearing ID = 5.000mm (`carrier_bearing_ID = 5mm`) |
| **CATIA Today** | `carrier_planet_fastener_diam = 5mm` |
| **FDM Target (bearing interface)** | N/A — shoulder screw is a **purchased machined part**. Bearing ID rides on the screw shoulder. No printed surface involved. |
| **FDM Target (carrier bore)** | The carrier plate has a **printed bore** the shoulder screw passes through to locate the planet axis. This bore IS subject to FDM shrinkage. At ⌀5mm, expect ~0.35mm shrink → bore prints ~4.65mm, shoulder won't pass through. Model at **5.35mm** — screw passes through snugly, minimal axis wobble. |
| **Parameter update** | `carrier_planet_fastener_diam`: 5mm → **5.35mm**. Offset baked in (no separate param — shoulder screw diameter is fixed). |
| **Priority** | **Critical** — slop here = planet axis wobble = gear mesh error |

**Key insight:** The shoulder screw does double duty — it's the planet pin AND the carrier clamshell fastener. The shoulder diameter is what the bearing rides on (hardware-to-hardware, no FDM offset). The **carrier bore** is the printed feature that needs attention.

---

### 1.7 Ring Gear OD → Housing Bore

> Ring gear outer diameter slides into housing cylindrical bore

| Field | Value |
|-------|-------|
| **Function** | Concentrically locate ring gear. Must be close enough for good concentricity but loose enough to drop in during assembly. Lid presses down on ring gears axially (A2), so radial fit just needs to locate, not retain |
| **ISO Designation** | H7/h6 (locational clearance fit) |
| **Nominal** | Ring gear OD = `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness)` = 75 + 2*(3.125 + 10) = **101.25mm** (`ring_wall_thickness` redefined as minimum solid wall from tooth root — see §5) |
| **CATIA Today** | Housing bore uses `ring_pitch_diam - carrier_ring_clearance` for carrier, but the ring gear housing interface is driven by `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness)`. Need to verify the actual housing bore dimension in CATIA |
| **FDM Target** | **0.3mm diametral clearance** (0.15mm per side). Model housing bore = ring gear OD + 0.3mm. Large diameter = more absolute error, so more clearance needed |
| **New Parameter** | `ring_housing_diam_offset = 0.30mm` |
| **Post-Processing** | Sand ring gear OD if too tight |
| **Priority** | **Critical** — ring gear concentricity directly affects mesh quality |

**Note:** Ring gears are split at mid-height (A4). Both halves must be the same OD and both must fit the same bore. Inconsistency between halves = step in the ring gear teeth.

**Sandwich bolt radial position check:** The sandwich fastener holes pass through the ring gear body at mid-height. After the ring gear OD increases to 101.25mm, verify in CATIA that the bolt circle still falls within the ring gear wall — between the ring root circle radius (~40.6mm) and the ring gear OD radius (~50.6mm). If the bolt circle exits the ring wall, it will break out into air.

---

### 1.8 Sun Gear Bore → Motor Shaft (D-Shaft)

> Sun gear bore fits onto motor D-shaft via press fit

| Field | Value |
|-------|-------|
| **Function** | Transmit full motor torque to sun gear. D-shaft flat prevents rotation, press fit prevents axial slip |
| **ISO Designation** | H7/p6 (press fit) — but modified for D-shaft geometry |
| **Nominal** | Motor shaft OD = TBD (need to measure). Skeleton has `motor_shaft_clearance_hole = 18mm` for the housing pass-through, but actual shaft is smaller |
| **CATIA Today** | Sun gear bore likely driven by `sun_pitch_diam` (20mm) for the gear geometry, but the bore for the motor shaft is separate. `Gears\Radius.2 = 10mm` (⌀20mm) appears to be the sun pitch circle, and `Gears\Radius.11 = 2.5mm` (⌀5mm) may be the sun gear bore |
| **FDM Target** | Model bore at **nominal shaft diameter** (no offset). D-shaft flat provides anti-rotation. FDM undersizing creates natural press fit |
| **New Parameter** | `motor_shaft_diam = TBD` (measure actual motor shaft with calipers) |
| **Priority** | Important |

**Action needed:** Measure motor shaft diameter with calipers. The D-flat dimension also matters — model the bore to match the shaft profile.

---

### 1.9 Lid Step → Ring Gear / Housing Interface

> Lid has a step that drops down and sits on top of ring gears (A2)

| Field | Value |
|-------|-------|
| **Function** | The lid step serves two purposes: (1) radially locates lid concentric with housing, (2) presses down on ring gears to hold them axially. This is the primary lid registration feature |
| **ISO Designation** | H7/h6 (locational clearance) for the radial fit between lid step OD and housing bore |
| **Nominal** | Lid step OD ≈ housing bore ID (which is the ring gear bore, ~101.25mm after ring wall redefine — see §1.7, §5) |
| **CATIA Today** | Lid dimensions driven by `housing_lid_thickness = 18.7mm` and related formulas |
| **FDM Target** | **0.2-0.3mm diametral clearance** between lid step and housing bore. Must be loose enough to assemble but tight enough to locate |
| **New Parameter** | `lid_step_clearance = 0.25mm` |
| **Priority** | Important — this is how the lid self-centers |

---

## 2. Axial Fits (Height/Shoulder Interfaces)

### 2.1 Split Ring Gear Height → Housing Cavity

> Combined height of both ring gear halves must fit within housing cavity depth

| Field | Value |
|-------|-------|
| **Function** | Ring gears sit in housing, lid presses down on them. Need slight clearance so lid seats on housing body (not on ring gears alone — ring gears compress, housing doesn't) |
| **Nominal** | Ring gear total height = `gear_height = 18.6mm` (both halves combined). Housing cavity depth = housing_body_total_height minus base thickness minus bearing pocket minus lid interface |
| **CATIA Today** | `gear_height = 18.6mm`. The cavity depth is implicit from the stack formula |
| **Target** | Ring gear stack should be **0.2-0.5mm shorter** than cavity depth. Lid step applies light axial pressure |
| **New Parameter** | Already partially handled by `carrier_lid_clearance = 4.75mm`, but verify that ring gear height has its own clearance in the stack |
| **Priority** | Important |

**From the height formula (actual CATIA values):**
```
housing_body_total_height = Housing_base_thickness + main_bearing_base_clearance
                          + Main_bearing_height + carrier_plate_bottom_h
                          + gear_height + carrier_plate_thickness
                          + carrier_lid_clearance + housing_lid_thickness
= 5 + 2 + 6.95 + 10.2 + 18.6 + 3.25 + 4.75 + 18.7 = 69.45mm
```
The `carrier_lid_clearance = 4.75mm` provides space between the top of the carrier and the lid. The ring gears occupy the `gear_height = 18.6mm` zone. The lid step drops down onto them — so the lid step depth must be slightly more than the ring gear protrusion above the carrier.

---

### 2.2 Carrier–Planet Axial Stack (Most Critical)

> Shoulder-to-shoulder distance in carrier vs planet + bearing stack

| Field | Value |
|-------|-------|
| **Function** | Planets must spin freely. Herringbone teeth self-center axially (A9), but the pocket must provide enough room for the planet + bearings without binding |
| **Concern** | Too tight → planets bind, friction kills backdrivability. Too loose → axial rattle (less critical with herringbone since they self-center) |
| **Priority** | **Critical** — directly affects backdrivability |

**Stack analysis (actual CATIA values):**

```
Known dimensions:
  carrier_plate_bottom_h  = 10.2mm   (bottom carrier plate total height)
  carrier_plate_thickness = 3.25mm   (top carrier plate thickness)
  carrier_plate_min_thickness = 2mm  (min solid wall above/below planet pocket)
  carrier_planet_clearance = 1.25mm  (designed gap each side of planet)
  gear_height = 18.6mm               (planet gear height)
  carrier_bearing_h = 5mm            (685ZZ bearing height)

Pocket height = gear_height + 2 × carrier_planet_clearance
             = 18.6 + 2×1.25 = 21.1mm

Planet assembly:
  685ZZ bearings recessed inside through-bore — no protrusion beyond gear faces
  Planet assembly height = 18.6mm (gear only)

Clearance: 21.1 − 18.6 = 2.5mm total (1.25mm each side)
```

**Verdict:** 1.25mm clearance per side is adequate with herringbone self-centering. FDM tolerance ±0.2mm leaves minimum ~1.05mm clearance in worst case. No binding risk.

---

### 2.3 Main Bearing Seating Depth

> Bearing height (6.95mm per skeleton) vs pocket depth

| Field | Value |
|-------|-------|
| **Function** | Bearing must be fully seated in pocket, supported axially by the shoulder |
| **Nominal** | `Main_bearing_height = 6.95mm` (from skeleton — slightly under the 7mm catalog spec, likely accounting for tolerance) |
| **CATIA Today** | Pocket depth driven by carrier and housing geometry. `main_bearing_base_clearance = 2mm` spaces the bottom bearing above the housing floor |
| **Concern** | The bearing pocket depth is implicit — not a standalone parameter. It's the distance from the bearing shoulder to the housing wall/lid wall |
| **Target** | Pocket depth ≥ `Main_bearing_height` (6.95mm). Bearing should sit flush or slightly proud |
| **New Parameter** | Consider adding `main_bearing_pocket_depth = 7.0mm` as an explicit parameter |
| **Priority** | Important |

---

## 3. Clearance Holes

### 3.1 M3 Fastener Clearance Holes

> Gearbox housing → motor housing. **Measured: M3, 8mm long with stock socket cap.**

| Field | Value |
|-------|-------|
| **Standard** (ISO 273) | Close fit: ⌀3.4mm / Normal fit: ⌀3.6mm |
| **CATIA Today** | `gearbox_housing_motor_housing_fastener_diam = 3.4mm` — modeled at ISO close-fit clearance, not FDM-corrected |
| **FDM Target** | Model at **~⌀3.8mm**. Calibration coupon: ⌀3.4 printed ~3.0mm (−0.4mm). Need ~3.8mm modeled to get ~3.4mm printed. |
| **Action** | Change `gearbox_housing_motor_housing_fastener_diam` from 3mm to ~3.8mm |
| **Priority** | Standard |

> **⚠ Measurement note:** Small hole measurements (~⌀3–5mm) are approximate — calipers are imprecise on small bores. Revalidate on coupon v2.

### 3.2 M4 Fastener Clearance Holes

> Gearbox housing → motor (ODrive). **Measured: ⌀3.92mm (≈M4), ~6.1mm long.** These are the motor mounting bolts from the ODrive motor.

| Field | Value |
|-------|-------|
| **Standard** (ISO 273) | Close fit: ⌀4.5mm / Normal fit: ⌀4.8mm |
| **CATIA Today** | `gearbox_housing_motor_fastener_diam = 4.5mm` — modeled at ISO close-fit clearance, not FDM-corrected |
| **FDM Target** | Model at **~⌀4.9mm**. Extrapolated from M3 calibration (~0.35–0.4mm shrink on small holes). |
| **Action** | Change from 4mm to ~4.9mm |
| **Priority** | Standard |

> **⚠ Estimated — not yet validated.** Extrapolated from M3 hole shrinkage. Revalidate on coupon v2.

### 3.3 M5 Sandwich Fastener Clearance Holes

> Housing-lid-ring gear sandwich assembly (4 fasteners)

| Field | Value |
|-------|-------|
| **Standard** (ISO 273) | Close fit: ⌀5.5mm / Normal fit: ⌀5.8mm |
| **CATIA Today** | `gearbox_housing_sandwich_fastener_diam = 5.5mm` — not yet updated to confirmed value |
| **FDM Target** | Model at **⌀5.35mm**. Tight clearance fit — analogous to shoulder screw bore logic. Aaron confirmed value. |
| **Action** | Change from 5mm to 5.35mm |
| **Priority** | Standard |

> **⚠ Not yet validated.** Revalidate on coupon v2.

### 3.4 Heat-Set Insert Pilot Holes

#### M3 Inserts (carrier, housing)

> M3 heat-set inserts — measured 2026-02-20

| Field | Value |
|---|---|
| **Insert measurements** | OD w/ ribs: 6.03mm, OD smooth body: **4.91mm** |
| **CATIA parameter** | `m3_heatsert_diam` → **5.2mm** |
| **CATIA parameter** | `m3_heatsert_depth` → **6.0mm** |
| **Rationale** | Pilot targets smooth body OD (4.91mm). With ~0.3mm shrink on small holes, model 5.2mm → expect ~4.9mm printed. Ribs melt into plastic during iron insertion. |
| **Priority** | Important |

#### M5 Inserts (output shaft)

> M5 heat-set inserts for output shaft attachment. **Previously documented as M4 — corrected to M5 based on actual hardware.**

| Field | Value |
|---|---|
| **Insert measurements** | OD w/ ribs: 6.97mm, OD smooth body: **5.96mm** |
| **CATIA parameter** | output shaft heatsert diam → **6.3mm** |
| **CATIA parameter** | output shaft heatsert depth → **~6.5mm** |
| **Rationale** | Pilot targets smooth body OD (5.96mm). With estimated shrink, model 6.3mm → expect ~6.0mm printed. |
| **Priority** | Important |

> **⚠ Correction:** Previous versions of this doc listed M4 inserts for the output shaft. Actual hardware is M5. `m5_heatsert_diam = 6.3mm` and `m5_heatsert_depth = 6.5mm` are the active params. `m4_heatsert_diam` and `m4_heatsert_depth` still exist in the skeleton (at 5mm / 6mm) but are **dead params — delete from skeleton**. No M4 inserts exist in this design.

> **⚠ Measurement note:** Insert and small hole measurements are approximate (calipers imprecise on small features). Heatsert fits will be validated when carrier or housing is printed.

**Note on carrier alignment:** The two carrier halves are aligned by the 3 shoulder screws (which double as planet pins). No separate dowel pins or locating features are needed — the shoulder screws passing through the planet bearings constrain angular position of both halves.

---

## 4. Critical Stack-Up Analyses

### 4.1 Full Axial Stack (Housing Assembly)

This is the tolerance chain Aaron flagged as most concerning (A17). The lid, ring gears, carrier, and bearings all stack axially.

```
                    ┌─────────────────────────┐
                    │      Lid (top)           │
                    │  ┌───────────────────┐   │  Main_bearing_height = 6.95mm
                    │  │ Top main bearing   │   │
                    │  │ (6805-2RS)         │   │
                    │  └───────────────────┘   │
                    │     carrier_lid_clearance │  = 4.75mm
                    ├─────────────────────────┤
  carrier_plate_    │  Top carrier plate       │  = 3.25mm
  thickness         ├─────────────────────────┤
                    │                          │
  gear_height       │  Gears + Planets         │  = 18.6mm
                    │  (ring gears fill this)  │
                    │                          │
                    ├─────────────────────────┤
  carrier_plate_    │  Bottom carrier plate     │  = 10.2mm
  bottom_h          │  (includes bearing seat) │
                    ├─────────────────────────┤
                    │  ┌───────────────────┐   │
  Main_bearing_     │  │ Bottom main bearing│   │  = 6.95mm
  height            │  │ (6805-2RS)         │   │
                    │  └───────────────────┘   │
  main_bearing_     │  (clearance to base)     │  = 2mm
  base_clearance    ├─────────────────────────┤
  Housing_base_     │  Housing base            │  = 5mm
  thickness         └─────────────────────────┘

  Total = 5 + 2 + 6.95 + 10.2 + 18.6 + 3.25 + 4.75 + 18.7 = 69.45mm ✓
```

**Where tolerance accumulates:**

| Component | Nominal | FDM Tolerance | Worst Case |
|-----------|---------|---------------|------------|
| Housing base thickness | 5.00mm | ±0.20mm | 4.80–5.20mm |
| Main bearing clearance | 2.00mm | ±0.20mm | 1.80–2.20mm |
| Bottom bearing (purchased) | 6.95mm | ±0.05mm | 6.90–7.00mm |
| Bottom carrier plate | 10.20mm | ±0.20mm | 10.00–10.40mm |
| Gear zone | 18.60mm | ±0.20mm | 18.40–18.80mm |
| Top carrier plate | 3.25mm | ±0.20mm | 3.05–3.45mm |
| Carrier-lid clearance | 4.75mm | — (result) | — |
| Top bearing (purchased) | 6.95mm | ±0.05mm | 6.90–7.00mm |
| Lid (printed) | 18.70mm | ±0.20mm | 18.50–18.90mm |

**Worst-case total range:** 67.45mm to 71.45mm (vs nominal 69.45mm)

**The `carrier_lid_clearance = 4.75mm` is the buffer.** In worst case, printed parts could eat into this clearance by up to ~1.0mm (all tolerances stacking against you), leaving ~3.75mm. Comfortable margin — the lid will seat.

**Verdict:** The 4.75mm `carrier_lid_clearance` provides generous margin. This is the first thing to check if the lid doesn't seat flat, but it's unlikely to be a problem.

---

### 4.2 Radial Concentricity Chain

All gear meshes depend on these features being concentric to Datum B (central axis):

```
Concentricity error budget:

  Housing bore (ring gear location)    ±0.15mm  (FDM bore roundness)
+ Carrier bearing play                 ±0.05mm  (bearing internal clearance)
+ Carrier pin position                 ±0.10mm  (FDM hole position)
+ Ring gear OD to ID concentricity     ±0.10mm  (FDM print accuracy)
─────────────────────────────────────────────
= Worst case total mesh error          ±0.40mm
```

**This is larger than the 0.08mm runout target in 08-gdt-notes.md.** But that target assumed post-processing (reaming). Since Aaron wants as-printed (A14), the realistic target is ±0.2-0.3mm mesh alignment error.

**Is ±0.3mm acceptable?** For a 3D-printed prototype with `module ~2.5` gears (tooth height ~5.6mm), ±0.3mm radial error is ~5% of tooth height. This will cause some non-uniform loading but shouldn't prevent the gears from meshing. Expect slightly noisier operation and faster wear on the high-contact sides.

**Mitigation:** The herringbone teeth help — they self-center axially and are more tolerant of slight radial misalignment than spur gears.

---

### 4.3 Carrier–Planet Pocket Stack

```
Pocket height available = f(carrier geometry)

Planet assembly inside pocket:
  Bearing (685ZZ):     5mm
  Planet gear:        18.6mm  (gear_height)
  Bearing (685ZZ):     5mm
  ─────────────────
  Total:              28.6mm  (if bearings sit outside the gear bore)

  OR if bearings sit inside the gear bore (18.6mm deep bore, 5mm bearing):
  Total:              18.6mm  (bearings recessed inside gear)
```

**This depends on whether the 685ZZ bearings protrude beyond the planet gear faces.** The gear is 18.6mm tall, and the bearing is 5mm wide. If the bore goes all the way through, the bearings sit 6.8mm inside each end — well within the gear body. No protrusion.

**With `carrier_planet_clearance = 1.25mm` on each side:** The pocket is 18.6mm (gear) + 2×1.25mm (clearance) = 21.1mm. The planet assembly is 18.6mm. That's 2.5mm total clearance — adequate with herringbone self-centering.

**Verdict:** No risk of binding. The herringbone self-centering means the planets will find their axial position naturally.

---

## 5. Gear Module & Clearance Fix

**Problem discovered:** Carrier pocket clearances and the ring gear wall thickness are based on pitch diameters, but actual gear teeth extend beyond the pitch circle. This means carrier pockets may be too small and the ring gear wall is thinner than expected.

### The Missing Parameter

```
gear_module = 2.5mm
```

Calculated from: `module = pitch_diam / number_of_teeth`
- Sun: 20mm / 8 teeth = 2.5mm
- Planet: 27.5mm / 11 teeth = 2.5mm
- Ring: 75mm / 30 teeth = 2.5mm

### How Teeth Extend Beyond Pitch Diameter

| Dimension | Formula | Meaning |
|---|---|---|
| **Addendum** (tip above pitch) | `1.0 × gear_module` = 2.5mm | How far tooth tips extend outward |
| **Dedendum** (root below pitch) | `1.25 × gear_module` = 3.125mm | How deep tooth roots cut inward |
| **Tip diameter** (external gear) | `pitch_diam + 2 × gear_module` | Outer edge of tooth tips |
| **Root diameter** (external gear) | `pitch_diam - 2.5 × gear_module` | Bottom of tooth roots |

### Actual Gear Tip Diameters

| Gear | Pitch Diam | Tip Diam | Root Diam |
|---|---|---|---|
| Sun | 20mm | **25mm** | 13.75mm |
| Planet | 27.5mm | **32.5mm** | 21.25mm |
| Ring (internal — teeth point inward) | 75mm | **70mm** (tips inward) | **81.25mm** (roots at OD side) |

### What to Fix in CATIA

**1. Add parameter:** DONE
- `gear_module = 2.5mm`

**2. Fix planet pocket clearance cut: ** DONE
 - **Current:** based on `planet_pitch_diam + clearance` (pocket only 27.5 + clearance)
- **Problem:** actual planet OD is 32.5mm — teeth crash into carrier wall
- **Fix:** change to `planet_pitch_diam + 2 * gear_module + clearance`
- This makes the pocket clear the tooth tips, not just the pitch circle

**3. Fix sun gear passthrough clearance cut:** DONE
- **Current:** based on `sun_pitch_diam + clearance`
- **Problem:** actual sun tip diameter is 25mm, not 20mm
- **Fix:** change to `sun_pitch_diam + 2 * gear_module + clearance`

_**4. Ring gear wall thickness — redefined (2026-02-20): done**_
- `ring_wall_thickness = 10mm` is now defined as the **minimum solid wall from tooth root to ring gear OD**
- The tooth root (dedendum) sits `1.25 × gear_module` = 3.125mm inside the pitch circle, so:
  - Ring gear OD = `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness)` = 75 + 2*(3.125 + 10) = **101.25mm**
- **Correction (was "7.5mm", error):** Previous version said solid wall = `ring_wall_thickness − gear_module` = 7.5mm. That was wrong — it subtracted the addendum (1×module) instead of the dedendum (1.25×module). Actual solid wall under the old definition (pitch to OD) = 10 − 3.125 = **6.875mm**, not 7.5mm.
- Under the new definition, `ring_wall_thickness` IS the solid wall. Parameter value stays 10mm — the meaning changed, and the OD formula updated to match.

### Why This Matters Parametrically

If you ever change `gear_module` (different tooth size), the clearance cuts and wall thickness automatically adjust. Without this parameter, changing tooth size would silently break the carrier pockets.

---

## 6. CATIA Parameter Summary

### New Parameters — Status

| CATIA Param Name                                                         | Value in CATIA | Status                      | Notes                                                                   |
| ------------------------------------------------------------------------ | -------------- | --------------------------- | ----------------------------------------------------------------------- |
| `gear_module`                                                            | 2.5mm          | ✅ Done                      |                                                                         |
| `main_bearing_shaft_offset`                                              | 0.10mm         | ✅ Done                      | Doc previously called this `housing_bearing_shaft_offset`               |
| `planet_bearing_offset`                                                  | 0.20mm         | ⚠ Needs update → **0.15mm** | Doc calls this `planet_bore_offset`; `planet_bearing_bore` auto-updates |
| `carrier_bearing_bore_offset`                                            | 0.10mm         | ✅ Done                      |                                                                         |
| `lid_bearing_bore_offset`                                                | 0.10mm         | ✅ Done                      |                                                                         |
| `lid_bearing_OD`                                                         | 37mm           | ✅ Done                      | Doc had capital `Lid_bearing_OD`                                        |
| `carrier_shaft_offset`                                                   | 0.10mm         | ✅ Done                      |                                                                         |
| `ring_housing_diam_offset`                                               | 0.30mm         | ✅ Done                      |                                                                         |
| `lid_step_clearance`                                                     | 0.25mm         | ✅ Done                      |                                                                         |
| `planet_inner_race_OD`                                                   | —              | ❌ Not yet added             | Value: 7mm (measured). Used for inner race relief counterbore (⌀7.5mm)  |
| NOTE: ISNT THE INNER RACE OD ALREADY A THING? PLANET_BEARING_SHOULDER_ID |                |                             |                                                                         |

### Existing Parameters to Modify

| Parameter | CATIA Value | Target | Status | Notes |
|-----------|-------------|--------|--------|-------|
| `carrier_planet_fastener_diam` | 5.35mm | 5.35mm | ✅ Done | Shoulder screw carrier bore. Offset baked in. ⚠ Validate with carrier print. |
| `gearbox_housing_motor_housing_fastener_diam` | 3.4mm | **3.8mm** | ❌ Pending | M3 clearance hole. Calibration: 3.4mm printed ~3.0mm. |
| `gearbox_housing_motor_fastener_diam` | 4.5mm | **4.9mm** | ❌ Pending | M4 clearance hole. Extrapolated ~0.35–0.4mm shrink. ⚠ Not yet validated. |
| `gearbox_housing_sandwich_fastener_diam` | 5.5mm | **5.35mm** | ❌ Pending | Aaron confirmed value. ⚠ Not yet validated. |
| `m3_heatsert_diam` | 5.2mm | 5.2mm | ✅ Done | M3 insert pilot. Measured body OD = 4.91mm. |
| `m3_heatsert_depth` | 6mm | 6mm | ✅ Done | |
| `m5_heatsert_diam` | 6.3mm | 6.3mm | ✅ Done | Output shaft (M5, not M4). Measured body OD = 5.96mm. |
| `m5_heatsert_depth` | 6.5mm | 6.5mm | ✅ Done | |
| `m4_heatsert_diam` | 5mm | **DELETE** | ⚠ Dead param | No M4 inserts in design. Delete from skeleton. |
| `m4_heatsert_depth` | 6mm | **DELETE** | ⚠ Dead param | No M4 inserts in design. Delete from skeleton. |

> **⚠ Correction (2026-02-20):** Output shaft inserts are **M5, not M4** as previously documented. Old `m4_heatsert_*` parameters are superseded.
>
> **⚠ Note:** Small hole offsets (clearance holes and heatsert pilots) are extrapolated from approximate caliper measurements on coupon v1. Will be validated when carrier/housing parts are printed with these features.

### Formulas to Add

All nominal bearing parameters (`Main_bearing_OD`, `Main_bearing_ID`, etc.) stay untouched — they represent the real bearing spec and are referenced by multiple features. The offset gets applied on the **specific sketch dimension** that controls each mating feature.

**Leave these alone** (they're nominal references, don't add offsets to them):
- `Main_bearing_OD = 37mm`
- `Main_bearing_ID = 25mm`
- `ring_pitch_diam = 75mm`, `ring_wall_thickness = 10mm`

**Note:** `carrier_output_OD = 25.1mm` in CATIA — the offset is baked into the param value directly rather than via formula. Either approach works.

**Formula status:**

| # | Feature | CATIA Formula (Formula.x) | Target Formula | Result | Status |
| - | ------- | ------------------------- | -------------- | ------ | ------ |
| 1 | Housing body bearing shaft | `Formula.61`: `Main_bearing_ID + main_bearing_shaft_offset` | — | 25.10mm | ✅ Done |
| 2 | Carrier plate bearing bore | `Formula.67`: `Main_bearing_OD + carrier_bearing_bore_offset` | — | 37.10mm | ✅ Done |
| 3 | Lid bearing bore | `Formula.62`: `lid_bearing_OD + lid_bearing_bore_offset` | — | 37.10mm | ✅ Done |
| 4 | Carrier output shaft OD | `Formula.59/69`: `Main_bearing_ID + carrier_shaft_offset` | — | 25.10mm | ✅ Done |
| 5 | Ring gear housing bore | `Formula.60`: `ring_pitch_diam + 2*ring_wall_thickness + ring_housing_diam_offset` = **95.3mm** | `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness) + ring_housing_diam_offset` | **101.55mm** | ❌ Pending |
| 6 | Lid step OD | `Formula.66`: `ring_pitch_diam + 2*ring_wall_thickness - lid_step_clearance` = **94.75mm** | `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness) - lid_step_clearance` | **101.00mm** | ❌ Pending |
| 7 | Housing width | `Formula.32`: `ring_pitch_diam + 2*ring_wall_thickness + 2*Housing_min_wall_thickness` = **109mm** | `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness) + 2*Housing_min_wall_thickness` | **115.25mm** | ❌ Pending |

**Note on naming:** Each bearing interface has its own offset parameter (`main_bearing_shaft_offset`, `carrier_bearing_bore_offset`, `lid_bearing_bore_offset`, `carrier_shaft_offset`) rather than one global value. The lid bore references `lid_bearing_OD` instead of `Main_bearing_OD` — if the top bearing changes size in the future, update only `lid_bearing_OD` and the lid bore adjusts independently.

---

## 6. Calibration Print Strategy

All offsets in this document are theoretical — derived from ISO fit intent and general FDM rules, not from our printer. Before printing real gearbox parts, print a calibration coupon to validate the fits with real hardware.

### Test Coupon Design

A rectangular block (~60×50×25mm) with test features modeled at the **actual FDM target dimensions** from this document. Print it, then test-fit real bearings, bolts, and inserts into it. If a fit feels wrong, measure with calipers to quantify how much to adjust.

#### Coupon Layout

```
  TOP VIEW (~60 x 50mm, 25mm tall)
  ┌─────────────────────────────────────────┐
  │                                         │
  │    ┌─────────┐                          │
  │    │ ⌀37.10  │           ○ ~⌀5.3mm     │
  │    │  bore   │                          │
  │    │ w/shoulder           ○ ~⌀3.8mm     │
  │    └─────────┘                          │
  │                                         │
  │        ○ ⌀14mm            ⊙ ⌀25.10     │
  │        bore w/shoulder    post          │
  │                         (on top)        │
  └─────────────────────────────────────────┘
```

- **⌀25.10mm post** — boss extruded ~15mm upward from the top face
- **⌀37.10mm and ⌀14mm bores** — counterbores with shoulder steps to test bearing seating (see cross-section)
- Keep **≥5mm** solid material between features and between features and block edges

**Bearing bore cross-sections:**

```
  ⌀37.10 bore (main bearing seat)       ⌀14 bore (planet bearing seat)

  ┌───┐         ┌───┐                   ┌──┐       ┌──┐
  │   │         │   │                   │  │       │  │
  │   │ ⌀37.10 │   │                   │  │  ⌀14  │  │
  │   │         │   │                   │  │       │  │
  │   │         │   │                   │  │       │  │
  │   ├─────────┤   │ ← shoulder        │  ├───────┤  │ ← shoulder
  │   │ ⌀34.5  │   │   depth ~7mm     │  │ ⌀12.4 │  │   depth ~5mm
  └───┘         └───┘   (bearing ht)    └──┘       └──┘   (bearing ht)

  Shoulder OD sits between bore         Shoulder OD sits between bore
  wall and bearing ID.                  wall and screw.
  Bearing face rests on this ledge.     Bearing face rests on this ledge.
```

#### Feature Table

All dimensions are the **FDM target values** from this tolerance scheme — what we actually plan to model in the gearbox.

| Feature               | Model Dim    | Source                         | Type                      | Depth/Height | Test-Fit With                         |
| --------------------- | ------------ | ------------------------------ | ------------------------- | ------------ | ------------------------------------- |
| Main bearing bore     | **⌀37.10mm** | §1.3 lid bore (+0.10 offset)   | Counterbore               | 18mm deep    | 6805-2RS bearing (push OD in)         |
| ↳ shoulder step       | **⌀34.5mm**  | §1.1 shoulder OD               | Inner bore below shoulder | Thru         | Bearing should seat flush on ledge    |
| Bearing shaft post    | **⌀25.10mm** | §1.1/§1.4 (+0.10 offset)       | Boss (upward)             | 15mm tall    | 6805-2RS bearing (slide ID onto post) |
| Planet bearing bore   | **⌀14.00mm** | §1.4 (nominal, FDM undersizes) | Counterbore               | 20mm deep    | 685ZZ bearing (press OD in)           |
| ↳ shoulder step       | **⌀12.4mm**  | §1.4 shoulder OD               | Inner bore below shoulder | Thru         | Bearing should seat flush on ledge    |
| Heat-set insert pilot | **~⌀5.3mm** | §3.4 (post-calibration)        | Through hole              | Thru         | M3 heat-set insert (body OD 4.96mm)   |
| M3 clearance hole     | **~⌀3.8mm** | §3.1 (post-calibration)        | Through hole              | Thru         | M3 bolt (should pass through freely)  |

**Why ⌀37.10?** The coupon tests the transition fit. Both the lid bore (§1.3) and carrier bore (§1.2) are now 37.10mm — all bearing interfaces target the same transition fit. The coupon validates both at once.

Shoulder step depths match bearing heights: ~7mm for 6805-2RS, ~5mm for 685ZZ.

#### CATIA Modeling Steps

1. **Pad** a 60×50×25mm block (sketch rectangle on xy-plane → Pad 25mm)
2. **Pocket** the ⌀37.10mm counterbore — sketch ⌀37.10 circle on top face, Pocket 18mm (not thru)
3. **Pocket** the ⌀34.5mm shoulder bore — sketch ⌀34.5 circle concentric in the ⌀37.10 pocket floor, Pocket → Through All
4. **Pocket** the ⌀14.00mm counterbore — sketch ⌀14.00 circle on top face, Pocket 20mm
5. **Pocket** the ⌀12.4mm shoulder bore — sketch ⌀12.4 circle concentric in the ⌀14 pocket floor, Pocket → Through All
6. **Pocket** the ⌀5.00mm and ⌀3.40mm holes — Through All
7. **Pad** the ⌀25.10mm post — sketch ⌀25.10 circle on top face, Pad 15mm upward

#### Print Settings

**Use the exact same settings planned for real gearbox parts:**
- Same printer, same filament (material, brand, color)
- Same layer height, infill %, infill pattern
- Same nozzle and bed temperature
- **Print orientation:** flat 50×50 face on build plate — bores are vertical (best roundness), post grows upward (good cylindricity). This matches how most gearbox bores will print.

If any settings change for the real build, the calibration data may not transfer — reprint the coupon.

### Fit-Test Procedure

Test each feature with the actual hardware. This is the primary validation — does the fit feel right?

| Feature | Model Dim | Test With | Pass Criteria | Result |
|---------|-----------|-----------|---------------|--------|
| ⌀37.10 bore | 37.10mm | 6805-2RS bearing OD | Snug push fit — seats with firm hand pressure, doesn't fall out | **PASS** — finger press fit, clicks into place |
| ↳ shoulder | ⌀34.5mm | (same bearing) | Bearing sits flush on ledge, no rocking | Measured ~34.45mm |
| ⌀25.10 post | 25.10mm | 6805-2RS bearing ID | Snug slide-on — slight resistance, no slop | Measured 25.01mm — **not fit-tested** (bearing not slid onto post) |
| ↳ shoulder | ⌀27.4mm | (post shoulder ring) | — | Measured 27.3mm |
| ⌀14.00 bore | 14.00mm | 685ZZ bearing OD | Press fit — needs firm push or light tap, stays put | **FAIL** — bearing won't go in (bore too tight) |
| ↳ shoulder | ⌀12.4mm | (same bearing) | Bearing seats flush on ledge | Measured 12.07mm |
| ⌀5.00 hole | 5.00mm | Heat-set insert | Insert threads in with soldering iron, no excessive melt | Printed 4.65mm — too small |
| ⌀3.40 hole | 3.40mm | M3 bolt | Bolt passes through freely, minimal slop | Printed ~3.0mm — too tight |

### Calibration Results (2026-02-19)

#### Measurement Data

| Feature | Modeled | Measured | Deviation | Notes |
|---------|---------|----------|-----------|-------|
| ⌀37.1 bore | 37.10mm | ~37.0mm | **−0.10mm** | Hard to measure, fit feels great |
| ⌀34.5 shoulder | 34.50mm | ~34.45mm | −0.05mm | Hard to measure |
| ⌀25.1 post | 25.10mm | 25.01mm | −0.09mm | Shaft shrinks as expected |
| ⌀27.4 shoulder | 27.40mm | 27.3mm | −0.10mm | |
| ⌀14.0 bore | 14.00mm | 13.75mm | **−0.25mm** | Bearing OD = 14.00mm exact, won't fit |
| ⌀12.4 shoulder | 12.40mm | 12.07mm | **−0.33mm** | |
| ⌀5.0 hole | 5.00mm | 4.65mm | **−0.35mm** | |
| ⌀3.4 hole | 3.40mm | ~3.0mm | **−0.40mm** | M3 clearance hole |

**Trend: smaller features shrink proportionally more.** The ⌀37mm bore lost ~0.3% while the ⌀3.4mm hole lost ~12%.

**Possible contributor: Z-seam alignment.** Printed with random seam, but on small-diameter holes the seam bump takes up a proportionally larger fraction of the circumference. A seam bump that's negligible on a ⌀37mm bore may noticeably tighten a ⌀3.4mm hole. Consider testing "aligned" seam (away from bore interiors) on coupon v2 to isolate this effect.

#### Heat-Set Insert Measurements (corrected 2026-02-20)

Inserts re-measured more carefully:

| Insert | OD w/ ribs | OD smooth body | Pilot hole to model | Depth |
|--------|-----------|---------------|-------------------|-------|
| **M3** | 6.03mm | **4.91mm** | **5.2mm** | 6.0mm |
| **M5** (output shaft) | 6.97mm | **5.96mm** | **6.3mm** | ~6.5mm |

> **Correction:** Output shaft inserts are M5, not M4 as previously documented.

Pilot hole should be sized for the body OD (without ribs). The ribs melt into surrounding plastic during installation.

#### What to Update

**⚠ Measurement Uncertainty:** Small feature measurements (⌀3–5mm holes) are approximate — calipers are imprecise on small bores. Recommended offsets for small holes should be revalidated on coupon v2. The bearing fits (⌀37, ⌀25, ⌀14) are more reliable since hardware fit-testing gives direct pass/fail.

**Working fits (keep current offsets):**
- `lid_bearing_bore_offset = 0.10mm` — ⌀37.10 bore → finger press fit. Perfect for transition fit. **Validated.**
- `main_bearing_shaft_offset = 0.10mm` — ⌀25.10 post → printed 25.01mm. Dimension looks right, but **bearing not test-fitted onto post** — needs fit-test on next build.
- `carrier_shaft_offset = 0.10mm` — same post diameter, same situation. **Needs fit-test.**
- `carrier_bearing_bore_offset = 0.10mm` — changed from 0.00mm (press fit) to 0.10mm (transition fit) per bearing fit philosophy decision. Matches lid bore offset. **Not yet validated — will test when carrier prints.**

**Corrections applied (all done — see §6 for current CATIA status):**

| Parameter | Coupon finding | Applied value |
| --------- | -------------- | ------------- |
| `planet_bearing_offset` | ⌀14 bore printed 13.75mm (−0.25mm) | **0.15mm** (Aaron's judgment) |
| `m3_heatsert_diam` | Insert body OD = 4.91mm (re-measured) | **5.2mm** |
| M3 clearance hole (`gearbox_housing_motor_housing_fastener_diam`) | Printed ~3.0mm, need ~3.4mm | **3.8mm** target |
| M4 clearance hole (`gearbox_housing_motor_fastener_diam`) | Extrapolated from M3 shrink | **4.9mm** target |
| M5 clearance hole (`gearbox_housing_sandwich_fastener_diam`) | — | **5.35mm** (Aaron confirmed) |
| Output shaft heatsert | Was M4 — corrected to M5, body OD = 5.96mm | **6.3mm** (`m5_heatsert_diam`) |

**Planet bearing shoulder (⌀12.4 → 12.07 printed):** Lost 0.33mm. May need a shoulder offset bump. Retest after planet print.

#### Next Steps (2026-02-20)

1. ~~Update CATIA parameters with new offsets~~ → In progress, see [2026-02-20 log](2026-02-20.md)
2. **Print planet gear** — validates bearing bore offset (+0.20mm, slightly conservative) with a real part
3. Test 685ZZ press fit — goal: match main bearing feel from coupon v1
4. Heatsert fits validated later when carrier/housing is printed (planet has no inserts)

### Python Calibration Calculator (Future)

A simple Python script that takes measured vs modeled dimensions, calculates per-feature offsets, and outputs corrected CATIA parameter values. Good candidate for a learning exercise in `learning/skill-building/`.

---

## Revision History

| Date | Change |
|------|--------|
| 2026-02-18 | Initial skeleton created |
| 2026-02-18 | Populated with real CATIA dimensions, FDM values, stack-up analyses from discussion answers |
| 2026-02-19 | Expanded calibration section: detailed coupon layout, CATIA steps, fit-test procedure |
| 2026-02-19 | First calibration print results: main bearing fit good, planet bore needs +0.25mm, small holes need significant offset increase, M3 heatsert larger than assumed |
| 2026-02-20 | Corrected heatsert measurements (M3: 4.91mm body, M5 replaces M4: 5.96mm body). Updated all pilot hole and clearance hole values. Planet gear print queued as next validation step. |
| 2026-02-20 | Bearing fit philosophy change: all interfaces target transition fit (finger press) for backdrivability. `carrier_bearing_bore_offset` 0.00→0.10mm. Departed from conventional rotating-ring = press fit rule — justified by FDM reality and QDD priorities. |
| 2026-02-20 | Ring wall thickness redefined: `ring_wall_thickness` now means minimum solid wall from tooth root to OD (not pitch to OD). Fixed §5 error (7.5mm → 6.875mm under old definition). Ring gear OD updated from 95mm → 101.25mm with new formula `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness)`. Housing bore and lid step formulas updated. |
| 2026-02-20 | Planet bore offset revised 0.20mm → 0.15mm (Aaron's judgment). Inner race clearance relief added to §1.4 — prevents bearing bind, doubles as removal path. Sandwich fastener diam updated 5.8mm → 5.35mm (Aaron confirmed). |
| 2026-02-20 | Synced doc to actual CATIA parameter dump. Updated §4.1 stack (all values), §4.3 pocket analysis, §2.1 gear height. Fixed CATIA param names (`main_bearing_shaft_offset`, `planet_bearing_offset`, `lid_bearing_OD`). Formula table restructured with done/pending status. Dead `m4_heatsert_*` params flagged for deletion. |
