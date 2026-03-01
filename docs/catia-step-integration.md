# CATIA Integration — STEP Gear Geometry

How to get pygeartrain STEP gear bodies into the skeleton-driven QDD assembly.

## Core Principles

- **STEP as assembly = bad** — sub-parts get independent DOF and can drift
- **STEP as multi-body part = good** — one coordinate system, bodies are frozen relative to each other
- **Skeleton owns position, part owns form** — skeleton defines where things live, STEP defines what they look like
- **STEP files are read-only reference geometry** — skeleton-driven cuts (bearing bores, bolt holes) are applied to the native part, not the raw STEP
- **Two export types from CadQuery** — `_PRINT` files go to slicer/manufacturer, `_CAD` file goes to CATIA

## Prerequisites

- STEP files generated in `pygeartrain/step_output_aaron/` (run `generate_step_aaron.py`)
- QDD CATIA assembly with working Skeleton A.1

## Step-by-Step

### Stage 1 — CadQuery Export (already done)

`generate_step_aaron.py` exports two types:

| File | Purpose |
|------|---------|
| `sun_PRINT.step/.stl`, `planet_N_PRINT.step/.stl`, `ring_top/bottom_PRINT.step/.stl` | Clean individual parts → slicer or manufacturer |
| `gearbox_CAD.step` | Multi-body part (all gears in one coordinate system) → CATIA |

The `_CAD` file uses a `TopoDS_Compound` — all bodies share one origin, nothing can drift. Primary axis is on part origin Z.

### Stage 2 — Import into CATIA

Import `gearbox_CAD.step` **as a part file, not an assembly.**

In 3DEXPERIENCE CATIA:
1. Open `gearbox_CAD.step` — import as a **Part** (not Product/Assembly)
2. All bodies land in one shared coordinate system — rigid, nothing drifts
3. Reposition the origin once so the primary axis aligns to world Z (should already be correct since CadQuery builds on Z)
4. Save as native **CATPart**

You now have a single part with multiple bodies: sun, 3 planets, ring\_bottom, ring\_top.

### Stage 3 — Skeleton Mating

Insert the native CATPart into your skeleton assembly:

1. Pick the **sun gear's central bore** (cylindrical face at origin) → extract axis
2. Pick a **ring half's flat split face** at $z=0$ → that's the midplane
3. Apply **one coincidence constraint** — part's central axis to skeleton `PUB_z_axis`
4. Apply **one coincidence constraint** — ring split face to skeleton `Gear_midplane`
5. Fix rotation — planet\_0 sits on the +X axis at $(r_{\text{carrier}}, 0, 0)$

| Constraint | From (Gear Part) | To (Skeleton) | Purpose |
|------------|-----------------|---------------|---------|
| Coincidence (axis) | Sun bore axis | `PUB_z_axis` | Concentric with gearbox axis |
| Coincidence (plane) | Ring split face at $z=0$ | `Gear_midplane` | Axial positioning |
| Fix rotation | Part X-axis or planet\_0 direction | Skeleton X-axis | Prevent free spin |

The entire multi-body part locks in place. All internal geometry (planet positions, ring wall, tooth profiles) is already correct because it was built relative to the origin in CadQuery.

### Stage 4 — Boolean Operations (later)

Boolean cut geometry (bearing bores, bolt holes, keyways) should be modeled as **native skeleton-driven geometry**:
- The skeleton parametrically controls the cut dimensions
- Apply the cut to the relevant body inside the multi-body part
- The STEP-origin geometry is the target, the skeleton-driven sketch is the tool

### Stage 5 — Manufacturing Output

- Use **Extract Geometry** (CATIA) to export individual bodies from the multi-body part
- Each body → its own STL/STEP for printing
- If no skeleton-driven cuts were applied to a body, use the clean `_PRINT` files from CadQuery directly

### Verify alignment

After constraining, check:

- [ ] Ring OD sits inside `housing_ring_gear_bore` (95.3mm bore, ring OD = 95mm → 0.15mm radial gap)
- [ ] Planets sit at the correct orbital radius — compare planet center distance against skeleton `planet_mid_path`
- [ ] Gear midplane aligns with skeleton `Gear_midplane` datum
- [ ] No interference between planet tips and ring root / sun root (visual check in section view)

### Update skeleton params if needed

The skeleton was built for the old involute gear set (R30/P11/S8, module=2.5mm). With the new cycloidal set (R48/P18/S12), these skeleton params may need updating:

| Skeleton Param | Old Value | New Value | Source |
|---------------|-----------|-----------|--------|
| `sun_pitch_diam` | 20mm | 19.9mm | Sun outer diameter from script |
| `planet_pitch_diam` | 27.5mm | 29.1mm | Planet outer diameter from script |
| `planet_mid_path` | 23.75mm | 23.0mm | Carrier radius from script |
| `carrier_diam` | 70mm | Recalculate: `ring_pitch_diam - carrier_ring_clearance` | Derived |
| `gear_module` | 2.5mm | N/A | Cycloidal teeth — module doesn't apply |

**Params that stay the same:**
- `ring_pitch_diam` = 75mm (script targets this exactly)
- `gear_height` = 18.6mm
- `ring_wall_thickness` = 10mm
- `number_of_planets` = 3
- `housing_ring_gear_bore` = 95.3mm (ring OD = 95mm, clearance preserved)

### What the skeleton still drives

Even with real gear geometry imported, the skeleton controls:
- Carrier plate dimensions (top/bottom thickness, clearances)
- Housing bore, wall thickness, mounting layout
- Bearing seats (main bearing, planet bearings)
- Fastener patterns (sandwich bolts, planet pins)
- Overall packaging envelope

The gear STEP bodies don't replace the skeleton — they complement it with real tooth geometry.

## Troubleshooting

**STEP import creates an assembly instead of a part:**
- Re-import and explicitly choose "Import as Part" / "As Result"
- The `gearbox_CAD.step` is a compound (multi-body), not an assembly — CATIA should recognize this

**STEP import looks wrong / no solid body:**
- Try importing with "As Result" rather than "As Specification" if available
- If the compound import fails, import individual `_PRINT` files one at a time

**Gears don't align with skeleton:**
- Verify the part's origin matches the skeleton origin
- The STEP files use mm units — confirm CATIA is set to mm

**Planet interference with carrier:**
- The skeleton `carrier_planet_clearance` (1.25mm) was designed for involute teeth
- Cycloidal teeth have different tip profiles — may need clearance adjustment after visual check

**Ring doesn't fit in housing:**
- Ring OD should be 95mm, housing bore 95.3mm
- If ring OD appears different, check that the script ran with `RING_WALL_MM = 10` and `TARGET_RING_DIAMETER_MM = 75`
