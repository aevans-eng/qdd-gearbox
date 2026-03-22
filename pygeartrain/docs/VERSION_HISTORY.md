# HackathonActuator Version History

Complete history of all gear generation versions, variations, and lessons learned.

---

## Quick Reference

| Version | Script | Output | Planets | Clearance | Key Feature |
|---------|--------|--------|---------|-----------|-------------|
| v1-v14 | `generate_planetary_cad_v*.py` | XYZ curves | 3 | N/A | Iterating on herringbone compensation |
| v15 | `generate_planetary_cad_v15.py` | XYZ curves | 3 | N/A | Return to ring-only compensation |
| v16 | `generate_planetary_cad_v16.py` | XYZ curves | 3 | -0.05mm | **Working** - CATIA macro workflow |
| v17 (STEP) | `generate_step_v17.py` | STEP/STL | 3 | -0.05mm | First CadQuery direct export (48/18/12) |
| v18 | `generate_step_v18.py` | STEP/STL | 3 | -0.20mm | Print-in-place (too loose) |
| v19 | `generate_step_v19.py` | STEP/STL | 3 | -0.10mm | Optimized clearance |
| v20 | `generate_step_v20.py` | STEP/STL | **4** | -0.10mm | Added 4th planet for torque |
| v20B | `generate_step_v20B.py` | STEP/STL | 4 | -0.10mm | **Split ring** with M3 bolts |
| v20c | `create_v20c_clearance.py` | STL only | 4 | Variable | Post-process gap creation |
| v21 | `generate_step_v21.py` | STEP/STL | 4 | **+0.05mm** | **30° helix**, interference fit |

---

## Two Parallel Pipelines

### 1. XYZ Curve Pipeline (v1-v16)
**For: 3DExperience CATIA import**

Generates XYZ text files with gear profiles at three Z-levels (z_neg, z0, z_pos) for lofting in CAD.

- **Scripts:** `generate_planetary_cad_v*.py`
- **Output:** `output_herringbone_v*/` - XYZ text files
- **Macro:** `ImportGearbox_v16.vbs` - Creates profiles and lofts in CATIA
- **Gear params:** R30/P12/S6, 3 planets, 70mm ring OD, 10mm thick

### 2. CadQuery STEP Pipeline (v17-v20B)
**For: Direct STEP/STL export**

Uses CadQuery to generate solid geometry directly - no CAD import needed.

- **Scripts:** `generate_step_v*.py`
- **Output:** `step_output_v*/` - STEP and STL files
- **Gear params:** R48/P18/S12, 3-4 planets, 80mm ring OD, 22mm thick

---

## Version Details

### XYZ Curve Versions (for CATIA)

#### v1-v2: Wrong rotation center
**Problem:** Applied herringbone twist around global origin for all gears.
**Lesson:** Planets must twist around their own centers, not the global origin.

#### v3: Basic herringbone with mesh rotation
**Problem:** Sun-planet mesh worked, but planet-ring mesh misaligned at z≠0.
**Lesson:** Different rotation centers (planet vs global) cause angular drift that must be compensated.

#### v4-v6: Wrong compensation formulas
**Problem:** Tried various theoretical formulas that didn't match reality.
**Lesson:** Don't trust derived formulas blindly - validate empirically.

#### v7-v8: Multi-gear compensation (FAILED)
**Problem:** Changed sun/planet instead of just ring - broke working sun-planet mesh.
**Lesson:** When something works, DON'T TOUCH IT. Isolate changes to what's broken.

#### v9: Empirical sweep approach
**Solution:** Created tile visualization sweeping ring rotation values.
**Finding:** Found correct neighborhood (~0.34°).
**Lesson:** When theory fails, use systematic empirical search.

#### v10-v12: Iterative refinement
- v10: Formula gave 0.341°, but overshot (0.131° remaining error)
- v11: Measured 0.21°, very close (0.0007° remaining)
- v12: Iterated to 0.21068° - **perfect** 0° offset

#### v13-v14: Multi-compensation attempt (FAILED)
**Problem:** Tried adding sun compensation (+3.44°) and carrier compensation.
**Result:** Broke planet-ring alignment. Compensations are coupled.
**Lesson:** Simple is better. Don't add complexity if simpler solution works.

#### v15: Return to simplicity
**Solution:** Copied v9 approach (ring-only compensation). Ran sweep comparison.
**Finding:** 0.2° ring offset is optimal (0.011° error).

#### v16: Manufacturing tolerance (WORKING)
**Solution:** Added -0.05mm profile offset to thin teeth for clearance.
**Result:** ~0.10mm clearance at mesh interfaces.
**Status:** Successfully imported into 3DExperience CATIA.

**Files:**
- `generate_planetary_cad_v16.py` - Generates XYZ curves
- `ImportGearbox_v16.vbs` - CATIA macro
- `output_herringbone_v16/` - Output files

---

### CadQuery STEP Versions

#### v17: First CadQuery port
**Purpose:** Generate STEP/STL directly without CAD software.
**New gear params:** R48/P18/S12 (larger teeth), 80mm ring OD, 22mm thick
**Clearance:** -0.05mm per gear (0.10mm total)
**Planets:** 3

**Files:**
- `generate_step_v17.py`
- `step_output_v17/` - sun.step/stl, planet_0-2.step/stl, ring.step/stl, assembly

#### v18: Print-in-place (loose)
**Purpose:** Increase clearance for FDM print-in-place.
**Clearance:** -0.20mm per gear (0.40mm total)
**Result:** Too loose - gears have excessive backlash.

#### v19: Optimized clearance
**Purpose:** Balance between printability and backlash.
**Clearance:** -0.10mm per gear (0.20mm total)
**Result:** Good balance - tight but printable on tuned printers.

#### v20: Four planets
**Purpose:** Increase torque capacity by adding 4th planet.
**Planets:** 4 (at 0°, 90°, 180°, 270°)
**Clearance:** -0.10mm per gear

**Files:**
- `generate_step_v20.py`
- `step_output_v20/` - sun, planet_0-3, ring, assembly

#### v20B: Split ring with M3 bolts (CURRENT)
**Purpose:** Assemble-able version (not print-in-place).
**Key changes:**
- Ring split at z=0 into top and bottom halves
- 6x M3 screw holes for bolting halves together
- Counterbored clearance holes in one half, tap holes in other
- 5mm ring wall thickness

**Files:**
- `generate_step_v20B.py`
- `step_output_v20B/`:
  - `sun.step/stl`
  - `planet_0.step/stl` through `planet_3.step/stl`
  - `ring_top.step/stl`
  - `ring_bottom.step/stl`
  - `gearbox_assembly.step/stl`

**Print Test Results (2026-01-31):**

✅ **What worked:**
- Two-part ring assembly works well for assembly
- Everything printed decently
- Low friction

❌ **Issues:**
- Clearances too generous - gears shift/sink noticeably when picked up
- Some gears have slop

💡 **Ideas for v21:**
- Fewer teeth to take advantage of the tooth profile style
- Reduce tolerance to 0mm or introduce interference fit
- Rely on plastic squish during assembly to compensate for interference

#### v21: Tight Fit + Steeper Helix (2026-01-31)
**Purpose:** Zero backlash gearbox with better axial resistance.
**Key changes from v20B:**
- Helix angle: 30° (was 20°) - more axial resistance to prevent sinking
- Interference fit: +0.05mm (was -0.10mm clearance) - relies on plastic squish
- Same teeth: R48/P18/S12, 4 planets, 5:1 ratio

**Files:**
- `generate_step_v21.py`
- `step_output_v21/`:
  - `sun.step/stl`
  - `planet_0.step/stl` through `planet_3.step/stl`
  - `ring_top.step/stl`
  - `ring_bottom.step/stl`
  - `gearbox_assembly.step/stl`

**Validation added:** Script now checks all planetary gear rules before generating:
1. Mesh constraint: R = S + 2P
2. Assembly constraint: (R + S) % N == 0
3. Planet non-interference: (S + P) × sin(π/N) > P + 2
4. Minimum teeth: S ≥ 6, P ≥ 6
5. Planet count: 2 ≤ N ≤ 8

---

#### v20c: Post-process gap creation
**Purpose:** Add gaps at contact points without changing overall profiles.
**Method:** Finds vertices too close to neighbors, pushes them apart.
**Params:** MIN_GAP=0.08mm, THRESHOLD=0.15mm
**Output:** STL only (mesh-based operation)

---

## Key Parameters

### Original CATIA workflow (v16)
```
Ring teeth:     30
Planet teeth:   12
Sun teeth:      6
N planets:      3
Helix angle:    20°
Ring OD:        70mm
Thickness:      10mm
b-profile:      0.2
Ring offset:    0.2° (compensation)
Profile offset: -0.05mm
```

### CadQuery workflow (v17-v20B)
```
Ring teeth:     48
Planet teeth:   18
Sun teeth:      12
N planets:      3 (v17-v19) or 4 (v20+)
Helix angle:    20°
Ring OD:        80mm
Thickness:      22mm
b-profile:      0.5
Ring offset:    0.2° (compensation)
Profile offset: -0.10mm (v19+)
Ring wall:      5mm (v20B)
```

### v21 Parameters
```
Ring teeth:     48
Planet teeth:   18
Sun teeth:      12
N planets:      4
Helix angle:    30° (was 20°)
Ring OD:        80mm
Thickness:      22mm
b-profile:      0.5
Ring offset:    0.2° (compensation)
Profile offset: +0.05mm (INTERFERENCE - was -0.10mm)
Ring wall:      8mm
```

### Geometry constraint
```
R = S + 2P
```
Ring teeth = Sun teeth + 2 × Planet teeth

### Gear ratio
```
Ratio = (R + S) / S
```
- v16: (30 + 6) / 6 = 6:1
- v17+: (48 + 12) / 12 = 5:1

---

## The Ring Compensation Formula

The key insight for herringbone planetary gears:

```python
# Planets rotate around their own centers
# Ring rotates around global origin
# This causes mesh drift at z ≠ 0

ring_compensation = z × tan(helix_angle) × (1/ring_inner_r - 1/mesh_radius)

where:
  mesh_radius = carrier_radius + planet_outer_radius
```

This formula gets within ~0.2° of perfect. One iteration of empirical measurement achieves 0°.

---

## Lessons Learned Summary

1. **Isolate changes** - Only modify what's broken, preserve what works
2. **Validate empirically** - Theory gives estimates, measurement gives truth
3. **Use visual sweeps** - When stuck, create parameter sweeps
4. **Understand geometry** - Ring compensation exists because planets orbit at offset
5. **Iterate to precision** - Formula → Measure → Adjust → Repeat
6. **Simple > complex** - Ring-only compensation beats multi-compensation
7. **Two-phase macros** - Create all profiles before lofts to prevent cascade failures

---

## Output File Locations

### XYZ Curves (for CATIA import)
```
output_herringbone/           # Initial test
output_herringbone_v12-v17/   # Various iterations
output_herringbone_final/     # Clean working set
```

### STEP/STL (ready to print/import)
```
step_output_v17/              # 3 planets, 0.10mm clearance
step_output_v18/              # 3 planets, 0.40mm clearance (too loose)
step_output_v19/              # 3 planets, 0.20mm clearance (optimized)
step_output_v20/              # 4 planets, 0.20mm clearance
step_output_v20B/             # 4 planets, split ring with M3 bolts
step_output_v20c/             # 4 planets, post-processed gaps (STL only)
step_output_v21/              # 4 planets, 30° helix, +0.05mm interference ← CURRENT
```

---

## Next Steps / Ideas

### v21 Implemented
- [x] **Tighter tolerances** - +0.05mm interference fit (v21)
- [x] **Steeper helix** - 30° for better axial resistance (v21)
- [x] **Gear validation** - Script checks all rules before generating

### v22+ Ideas (pending v21 print test)
- [ ] Add carrier geometry to STEP output
- [ ] Parametric script for different gear ratios
- [ ] Blender render workflow for portfolio images
- [ ] Motor mount integration
- [ ] Bearing seats for planets
