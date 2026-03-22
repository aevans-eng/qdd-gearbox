# Herringbone Planetary Gear Pipeline

## Overview

This document describes the working pipeline for generating herringbone planetary gear XYZ profiles for import into 3DExperience CATIA.

**Working script:** `generate_planetary_cad_v16.py`
**Output directory:** `output_herringbone_v16/`
**CATIA macro:** `ImportGearbox_v16.vbs`

### v16 Features
- **Ring compensation:** 0.2° (validated empirically)
- **Profile offset:** -0.05mm (tooth thinning for manufacturing clearance)
- **Pre-positioned planets:** XYZ files include planet positions (no macro math needed)

---

## The Problem

Herringbone (double-helical) planetary gears have three gear types rotating around different centers:
- **Sun**: rotates around global origin
- **Ring**: rotates around global origin
- **Planets**: rotate around their own centers (at carrier_radius from origin)

This mismatch in rotation centers causes the planet-ring mesh to misalign at z≠0 unless compensated.

---

## Working Rules

### 1. Geometry Constraint
```
R = S + 2P
```
Where R = ring teeth, S = sun teeth, P = planet teeth.

### 2. Sun Gear (no compensation)
```python
twist_sun = z × tan(helix_angle) / sun_reference_radius
```

### 3. Planet Gears (no compensation)
```python
mesh_rotation = (1 - R/P) × angular_position
twist_planet = -z × tan(helix_angle) / planet_reference_radius  # opposite hand
position = (carrier_radius × cos(a), carrier_radius × sin(a))
```

### 4. Ring Gear (COMPENSATION REQUIRED)
```python
base_twist = -z × tan(helix_angle) / ring_inner_radius

# THE KEY FORMULA:
compensation = z × tan(helix_angle) × (1/ring_inner_r - 1/mesh_radius)

# where:
mesh_radius = carrier_radius + planet_outer_radius
```

### Why Ring Compensation?

The planet outer point rotates around the planet center, tracing an arc. As seen from the global origin, this point moves by:
```
α_planet = planet_twist × (planet_outer_r / mesh_radius)
```

The ring point rotates around the origin:
```
α_ring = ring_twist
```

The difference must be compensated:
```
Δα = z × tan(helix) × (1/ring_inner_r - 1/mesh_radius)
```

---

## Current Parameters

| Parameter | Value |
|-----------|-------|
| Ring teeth (R) | 30 |
| Planet teeth (P) | 12 |
| Sun teeth (S) | 6 |
| N planets | 3 |
| Helix angle | 20° |
| Ring outer diameter | 70mm |
| Gear thickness | 10mm |
| b-profile | 0.2 |

**Calculated values:**
- Carrier radius: 20.75mm
- Sun outer radius: 8.76mm
- Planet outer radius: 14.25mm
- Ring inner radius: 32.74mm
- Mesh radius: 35mm
- **Ring compensation: 0.2°** (validated empirically)
- **Profile offset: -0.05mm** (tooth thinning for clearance)

---

## Output Files

The script generates XYZ point files for each gear at three z-levels:
```
output_herringbone_v16/
├── sun_6_z0.txt, sun_6_z_pos.txt, sun_6_z_neg.txt
├── planet_12_0_z0.txt, planet_12_0_z_pos.txt, planet_12_0_z_neg.txt
├── planet_12_1_z0.txt, planet_12_1_z_pos.txt, planet_12_1_z_neg.txt
├── planet_12_2_z0.txt, planet_12_2_z_pos.txt, planet_12_2_z_neg.txt
├── ring_30_z0.txt, ring_30_z_pos.txt, ring_30_z_neg.txt
└── *.png validation images
```

**Note:** Planets are pre-positioned in the XYZ files (at 0°, 120°, 240°). No macro offset needed.

---

## CATIA Import Process

**Use the two-phase macro:** `ImportGearbox_v16.vbs`

1. Open new 3D Part in 3DExperience
2. Search "Macro" → open Macros dialog
3. Create new macro in your library, paste code from `ImportGearbox_v16.vbs`
4. Run macro (F5)
5. Phase 1 creates all profiles (15 splines)
6. Phase 2 creates all lofts (5 solids)
7. Fix any loft closing point errors manually (double-click loft → realign points)

**Ring gear:** Currently creates solid internal gear. For ring as hollow cylinder with internal teeth, need Boolean subtract approach (not yet implemented).

**Macro cache location:** `C:\Users\{username}\AppData\Local\Temp\CATAppliRsc_ConstructionDir_1\`

---

## Iteration History & Lessons Learned

See `archive/herringbone_iterations/` for failed attempts.

### v1-v2: Wrong rotation center
**Problem:** Herringbone twist was applied around global origin for all gears.
**Lesson:** Planets must twist around their own centers, not the global origin.

### v3: Missing ring compensation
**Problem:** Sun-planet mesh worked, but planet-ring mesh misaligned at z≠0.
**Lesson:** Different rotation centers (planet center vs global origin) cause angular drift.

### v4-v6: Wrong compensation formulas
**Problem:** Tried various theoretical formulas that didn't match reality.
**Lesson:** Don't trust derived formulas blindly - validate empirically.

### v7-v8: Changed sun/planet instead of just ring
**Problem:** Broke working sun-planet mesh while trying to fix planet-ring.
**Lesson:** When something works, DON'T TOUCH IT. Isolate changes.

### v9: Sweep approach
**Problem:** Needed to find correct ring rotation empirically.
**Solution:** Created tile visualization sweeping ring rotation values.
**Lesson:** When theory fails, use systematic empirical search.

### v10: Calculated formula overshot
**Problem:** Formula gave 0.341°, but actual needed ~0.21°.
**Lesson:** Theoretical formulas are approximations - measure and iterate.

### v11-v12: Iterative refinement
**Solution:** Measured actual offset, adjusted compensation, achieved 0° error.
**Final value:** 0.21068°

### v13-v14: Sun/carrier compensation (FAILED)
**Problem:** Tried adding sun compensation (+3.44°) and carrier compensation to improve sun-planet mesh axis alignment.
**Result:** Broke planet-ring alignment. Moving planets affects both interfaces - compensations are coupled.
**Lesson:** Simple is better. Don't add complexity if simpler solution works.

### v15: Return to simplicity
**Solution:** Copied v9 (ring-only compensation). Ran sweep comparison of ring offsets.
**Finding:** 0.2° ring offset is optimal (0.011° angular error).
**Lesson:** When complex approaches fail, return to validated simple approach.

### v16: Profile offset tolerance (WORKING)
**Solution:** Added -0.05mm profile offset to thin all teeth for manufacturing clearance.
**Result:** ~0.10mm clearance at all mesh interfaces (both mating teeth thinned).
**CATIA:** Two-phase macro creates all profiles first, then all lofts.
**Status:** Successfully imported into 3DExperience - gears look correct!

### Key Lessons Summary

1. **Isolate changes** - Only modify what's broken, preserve what works
2. **Validate empirically** - Theory gives estimates, measurement gives truth
3. **Use visual sweeps** - When stuck, create parameter sweeps to find the answer
4. **Understand the geometry** - The planet-ring compensation exists because planets rotate around offset centers
5. **Iterate to precision** - Measure offset → adjust → repeat until zero
6. **Simple > complex** - v15/v16 ring-only compensation beats v13/v14 multi-compensation
7. **Two-phase macros** - Create all profiles before lofts to prevent cascade failures

---

## Changing Parameters

If you change gear parameters (teeth, helix angle, diameter), you must:

1. Recalculate all radii from the new geometry
2. Apply the ring compensation formula:
   ```
   compensation = z × tan(helix) × (1/ring_inner_r - 1/mesh_radius)
   ```
3. Validate visually with a sweep if unsure
4. Iterate measurement → adjustment until offset = 0°

The formula should get you close (~0.2° accuracy), then iterate for precision.
