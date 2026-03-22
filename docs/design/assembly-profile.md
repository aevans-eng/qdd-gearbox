# Assembly Profile — QDD Planetary Gearbox

A living document that builds up a complete picture of the assembly over time. Updated as Aaron shares more info across sessions — small details here and there get consolidated here instead of scattered across discussion files.

**Last updated:** 2026-02-19

---

## Assembly Overview

A 5:1 planetary gearbox (FDM 3D-printed) that sits on top of a BLDC motor. The motor shaft passes through the housing base and connects to the sun gear. Output is through the carrier, which rotates on two main bearings.

**Key design properties:**
- Backdrivable (QDD = quasi-direct-drive)
- Target backlash ≤ 0.5°
- Gear module: 2.5mm (8/11/30 teeth on sun/planet/ring)
- Ratio: 4.75:1 (from pitch diameter ratios: 1 + 75/20)
- No post-processing — everything as-printed
- No seals — silicone grease applied manually
- Budget under $120 CAD
- Printer: Bambu P1S

---

## Parts & How They Fit Together

### Housing Body
- Cup shape — closed bottom, open top
- Motor bolts to the bottom face (gearbox sits on top of motor)
- Motor shaft passes through a clearance hole (`motor_shaft_clearance_hole = 18mm`) in the base
- Contains a cylindrical bore (~⌀95mm) where the ring gears slide in from the top
- Has a bearing pocket/shoulder for the **bottom main bearing** (6805-2RS, ⌀37mm OD)
  - Shoulder supports bearing axially: `main_bearing_shoulder_OD = 34.5mm`, `main_bearing_shoulder_ID = 27.4mm`
  - Bearing sits on a lip, spaced above the housing floor by `main_bearing_base_clearance = 1.5mm`
- M3 fasteners connect housing body to motor housing
- M5 sandwich fasteners (×4) clamp housing body + lid + ring gears together
- `Housing_base_thickness = 5mm`, `Housing_min_wall_thickness = 7mm`

### Lid
- Sits on top of the housing body
- Has a **step** that drops down into the housing bore — this does two things:
  1. Radially locates the lid concentric with the housing (self-centering)
  2. Presses down onto the ring gears, providing axial constraint
- Contains a bearing pocket for the **top main bearing** (6710-2RS, 50×62×6mm)
- Carrier output shaft pokes through the lid: `carrier_output_lid_stickout = 1.5mm`
- `housing_lid_thickness = 15.95mm`, `housing_lid_min_thickness = 7mm`
- Prints face-down (open side up) — bearing bore is built up layer by layer, good for roundness

### Ring Gears (×2 halves)
- Split at mid-height — each half has half the herringbone teeth
- Slide into the housing cylindrical bore from the top
- Lid presses down on them axially — radial fit just needs to locate concentrically, not retain
- Both halves must be identical OD for consistent mesh
- `ring_pitch_diam = 75mm`, `ring_wall_thickness = 10mm`
- `gear_height = 20mm` (both halves combined)

### Carrier (clamshell — 2 halves)
- Bottom half and top half bolted together by shoulder screws
- Shoulder screws do triple duty: planet pins + carrier fastener + carrier alignment
- No separate dowel pins or locating features — shoulder screws handle alignment
- Bottom half has a lip that catches the bottom main bearing OD (bearing OD interfaces with bottom carrier plate)
- Top half interfaces with the top main bearing via the lid
- Output shaft is part of the carrier: `carrier_output_OD = 25mm`, `carrier_output_shaft_length = 17.45mm`
- `carrier_diam = 70mm`, `carrier_plate_bottom_h = 10.95mm`, `carrier_plate_thickness = 4mm`
- `carrier_plate_min_thickness = 2mm` (min material above/below planet pocket)

### Planet Gears (×3)
- Herringbone teeth — self-centering axially, floating
- Each planet has a 685ZZ bearing (⌀14mm OD, ⌀5mm ID, 5mm wide) press-fit into its bore
- The bearing sits well inside the gear (20mm tall gear, 5mm wide bearing — no protrusion)
- Spaced 120° apart: `planet_spacing = 120deg`
- `planet_pitch_diam = 27.5mm`, `planet_mid_path = 23.75mm`
- `carrier_planet_clearance = 2mm` axial clearance — generous for FDM

### Planet Bearings (685ZZ × 3)
- Outer race press-fits into planet gear bore (gear is the rotating part)
- Inner race rides on shoulder screw (pin is stationary)
- `carrier_bearing_OD = 14mm`, `carrier_bearing_ID = 5mm`, `carrier_bearing_h = 5mm`
- Bearing shoulders in carrier: `planet_bearing_shoulder_OD = 12.4mm`, `planet_bearing_shoulder_ID = 6.6mm`

### Shoulder Screws (×3)
- Act as planet pins AND carrier clamshell fasteners
- Shoulder diameter = 5mm (bearing inner race rides on the shoulder)
- Threaded end clamps carrier halves together
- `carrier_planet_fastener_diam = 5mm`

### Sun Gear
- Press fit onto motor D-shaft (circle with flat)
- D-flat prevents rotation, FDM undersizing creates natural press fit
- `sun_pitch_diam = 20mm`
- Motor shaft diameter: TBD (needs measurement with calipers)

### Main Bearings
- **Bottom bearing:** 6805-2RS (ID 25mm, OD 37mm, height 6.95mm) — sits on housing shoulder, OD interfaces with bottom carrier plate
- **Top bearing:** 6710-2RS (50×62×6mm) — sits in lid, carrier top interfaces with it

---

## Assembly Order (Bottom → Top)

1. **Housing body** — base of everything
2. **Bottom main bearing** (6805-2RS) — drops into housing bore, sits on shoulder
3. **Bottom carrier half** — pushes down onto bearing OD, lip catches the outer race
4. **Planet gears** (with 685ZZ bearings pre-pressed in) — sit on carrier
5. **Sun gear** — press-fit onto motor shaft, meshes with planets
6. **Ring gear halves** — slide into housing cylindrical bore from top, mesh with planets
7. **Top carrier half** — placed on top, shoulder screws thread through planet bearings and clamp both carrier halves
8. **Top main bearing** (6805-2RS) — sits on carrier top / in lid pocket
9. **Lid** — step drops down onto ring gears, bearing pocket captures top bearing, sandwich fasteners clamp everything

---

## Axial Constraint Chain

What holds everything in place vertically:

- **Ring gears** rest on housing body (gravity + lid pressure from above)
- **Lid step** presses down on ring gears
- **Bottom main bearing** sits on housing shoulder
- **Carrier** sits on bottom bearing (lip catches ID), constrained from above by top bearing + lid
- **Planets** float axially — herringbone teeth self-center
- **Sandwich fasteners** (M5 × 4) clamp lid to housing body, compressing the whole stack
- **`carrier_lid_clearance = 2mm`** is the buffer in the axial stack — absorbs FDM tolerance accumulation

---

## Radial Constraint Chain

What keeps everything concentric:

- **Housing bore** locates ring gears and lid step concentrically
- **Main bearings** locate carrier concentric to housing (Datum B = bearing bore axis)
- **Carrier** locates planet pins at 120° spacing
- **Planet bearings** locate planets on pins
- **Ring gear bore** and planet mesh keep gear train aligned

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Herringbone planets | Self-centering axially, more tolerant of radial misalignment than spur |
| Clamshell carrier | Allows planet assembly — gears and bearings trapped between two halves |
| Shoulder screws as pins | Simplifies BOM, dual-purpose (pin + fastener + alignment) |
| No post-processing | Prototype simplicity — everything as-printed, adjust offsets parametrically |
| Split ring gear | Enables herringbone teeth (can't insert through solid ring) |
| Skeleton-driven CAD | All dimensions flow from skeleton parameters — change one value, everything updates |
| Separate tolerance offsets | Nominal bearing dims stay pure; FDM offsets applied via formulas on specific features |

---

## CAD Strategy

- **Software:** 3DEXPERIENCE CATIA (student version)
- **Approach:** Skeleton-driven parametric modeling
  - Skeleton A.1 contains all master parameters and reference geometry
  - Individual parts reference skeleton dimensions via formulas/publications
  - Changing a skeleton parameter propagates to all parts
- **Current state:** Skeleton complete, parts modeled, tolerances being added
- **Known challenge:** Parameter organization is hard to navigate in V6 — using naming prefixes to group related params

---

## Manufacturing Notes

- **Printer:** Bambu P1S
- **Material:** TBD (likely PLA or PETG for prototype)
- **General FDM accuracy:** ±0.2mm
- **Bore undersizing:** ~0.1-0.2mm (holes print smaller than modeled)
- **Shaft oversizing:** slight (shafts print larger than modeled)
- **Print orientations:**
  - Housing: open top up
  - Lid: face-down (open side up)
  - Gears: flat
  - Carrier halves: side by side
- **No test prints yet** — calibration coupon planned before full build

---

## Open Items / TBD

- [ ] Measure motor shaft diameter with calipers (needed for sun gear bore)
- [ ] Calibration print to determine printer-specific offsets
- [ ] M3 heat-set insert dimensions for carrier (`carrier_heatsert_diam` and `carrier_heatsert_depth` currently 0)
- [ ] Verify ring gear housing bore dimension in CATIA — Formula.55 currently = `ring_pitch_diam + ring_wall_thickness`, may need correction
- [ ] Design table setup (after prototype validated)

---

*This document grows over time. When Aaron shares new info about the design, it gets consolidated here.*
