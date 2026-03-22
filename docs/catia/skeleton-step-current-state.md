# Skeleton + STEP Integration — Current State of Knowledge

Written 2026-03-01. Purpose: separate confirmed facts from assumptions before planning.

---

## CONFIRMED FACTS

### Skeleton parameters (from assembly_dump.txt)

| Parameter | Current Value |
|-----------|--------------|
| `ring_pitch_diam` | 75mm |
| `ring_wall_thickness` | 10mm |
| `ring_gear_OD` | 101.25mm |
| `housing_ring_gear_bore` | 101.55mm |
| `planet_pitch_diam` | 27.55mm |
| `sun_pitch_diam` | 19.9mm |
| `planet_mid_path` | 23.725mm |
| `gear_module` | 2.5mm |
| `carrier_planet_clearance` | 1.25mm |
| `gearbox_housing_sandwich_fastener_diam` | 5.5mm |
| Sandwich fastener bolt circle radius | 45.625mm |

### Skeleton formulas that use gear_module (confirmed by Aaron)

- **Formula.71:** `ring_pitch_diam + 2*(1.25*gear_module + ring_wall_thickness)` → drives `ring_gear_OD`
- **Carrier cutout formula (external part):** `planet_pitch_diam + 2*gear_module + carrier_planet_clearance`

### STEP file geometry (from generate_step_aaron.py source code)

- Ring outer diameter = `2 × (TARGET_RING_DIAMETER_MM/2 + RING_WALL_MM)` = `2 × (37.5 + 10)` = **95mm** — this is in the code, not estimated
- Ring pitch reference diameter = 75mm
- `RING_WALL_MM = 10mm` in the script is measured **from pitch reference to OD** (not from tooth root to OD)
- Sun outer diameter ≈ 19.9mm — from script print output (previous run)
- Planet outer diameter ≈ 29.1mm — from script print output (previous run)
- Carrier radius ≈ 23.0mm — from script print output (previous run)

### Confirmed discrepancy

- Skeleton `ring_gear_OD` = 101.25mm
- STEP ring OD = 95mm
- **Difference: 6.25mm — the skeleton ring gear is currently 6.25mm larger than the STEP geometry**

### Formula.55 (inferred from math — high confidence)

`ring_gear_OD - ring_wall_thickness` = 101.25 - 10 = 91.25mm = 2 × 45.625mm (sandwich fastener radius from dump). The math matches exactly, so Formula.55 almost certainly drives the sandwich fastener bolt circle.

### Physical setup (from Aaron)

- The bolt through the ring gear circumference **is the sandwich fastener** — same pattern at 45.625mm radius, 5.5mm diameter
- Aaron's concern: without knowing where solid material ends and tooth profile begins, bolt placement could have unequal wall thickness on each side

---

## ASSUMPTIONS / UNKNOWNS

### Ring gear tooth geometry — NOT measured

- **Ring tooth root radius: unknown.** I estimated ~39–40mm (2–3mm beyond the 37.5mm pitch line) based on typical cycloidal proportions. This has NOT been measured from the STEP or calculated from the script.
- **Ring solid wall (root to OD): unknown.** I estimated ~7–8mm. Depends entirely on the tooth root radius above.
- **Ring tooth depth: unknown.** Depends on tooth root radius.

### Formula.17 — confirmed by Aaron

`(sun_pitch_diam + planet_pitch_diam)/2` **directly drives `planet_mid_path`.** It is not a free parameter — it is formula-derived from the pitch diameters using the involute carrier radius rule. Changing sun/planet diameters will silently update planet_mid_path to the wrong value for cycloidal gears.

### Sandwich fastener clearance — partially unknown

- Outer clearance after ring_gear_OD fix: 47.5 - 42.5 - 2.75 = **2.25mm** — this is a real calculation (confirmed geometry)
- Inner clearance (bolt to tooth root): **unknown** — depends on tooth root radius above

### Cycloidal gear parameter values — from previous script run

The sun OD (19.9mm), planet OD (29.1mm), and carrier radius (23.0mm) were printed by a previous script run and recorded in the integration doc. They have not been independently verified since. The values should be correct for the current script parameters but have not been re-confirmed.

---

## ALL CONFIRMED — Script run 002 results (2026-03-01)

| Value | Result | Notes |
|-------|--------|-------|
| Ring tooth root radius | **37.500mm** | Exactly at pitch line — roots don't extend past it |
| Ring tooth depth | **1.531mm** | Shallow — tip to root |
| Ring solid wall | **10.000mm** | Full wall is solid material |
| Ring outer radius | 47.500mm | OD = 95mm ✓ |
| Carrier radius | **22.959mm** | Use this, not 23.0mm |
| Sun outer diameter | 19.898mm | ≈ 19.9mm ✓ |
| Planet outer diameter | 29.082mm | ≈ 29.1mm ✓ |

**Sandwich fastener — Formula.55 needs no changes.**
After ring_gear_OD fix to 95mm: bolt circle = (95-10)/2 = 42.5mm radius, exactly midpoint of ring wall.
Inner clearance (root to bolt edge): 42.5 - 37.5 - 2.75 = **2.25mm**
Outer clearance (OD to bolt edge): 47.5 - 42.5 - 2.75 = **2.25mm** — symmetric, acceptable for printed parts.
