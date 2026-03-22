# CATIA STEP Integration

How to get pygeartrain STEP gear bodies into the skeleton-driven QDD assembly.

## Overview

The gear integration lives in a dedicated **product** (`gears`) with four sibling parts:

| Part | Role |
|------|------|
| `skel_ref` | Fixed reference — holds pasted skeleton planes, sketches, axes. All other parts mate to this. |
| `gear_set` | Parametric placeholder gears (simple pads). Drives downstream parts (carrier, etc.). |
| `gear_part_output_rev01` | Imported STEP from pygeartrain — real herringbone cycloidal tooth geometry. |
| `cutting/adding bodies` | Separate part for boolean operations (bearing bores, bolt holes). References skeleton only. |

**Architecture rules:**
- The master skeleton (`SKEL_Gearbox`) is the single source of truth
- Each part independently pulls skeleton publications via Paste Link — no cross-referencing between parts (unreliable in practice)
- Cutting bodies reference skeleton datums only, never a specific gear part — this makes them survive STEP swaps
- `skel_ref` is the fixed anchor; all parts constrain to it, not to each other

![Gears product structure](images/2026-03-01-20-43-gears-product-structure.png)

**Key files:**
- STEP generator: `pygeartrain/generate_step_aaron.py`
- Latest STEP output: `pygeartrain/step_output_aaron/` (run 002)
- Confirmed geometry values: `docs/catia/skeleton-step-current-state.md`
- Pipeline README: `pygeartrain/step_output_aaron/README.md`

---

## Step 0 — Skeleton Cleanup (prerequisite)

Skeleton was built for involute gears (module=2.5mm). New geometry is cycloidal — two parameter changes fix everything.

**Open SKEL_Gearbox in CATIA → parameter list (Tools > Parameters or formula editor).**

| Parameter | New value | Why |
|-----------|-----------|-----|
| `sun_pitch_diam` | **16.836mm** | Actual sun pitch diameter. Formula.8 and Formula.17 cascade everything else. |
| `gear_module` | **0mm** | Zeroes out module term in ring_gear_OD and carrier cutout. Safe — no formulas divide by it. |

`ring_pitch_diam` stays at 75mm — already correct.
`planet_pitch_diam` is driven by Formula.8 `(ring_pitch_diam - sun_pitch_diam)/2` — updates automatically.
`planet_mid_path` is driven by Formula.17 `(sun_pitch_diam + planet_pitch_diam)/2` — updates automatically.

### What will cascade (expect these — all correct)

| Parameter | Before | After | Formula |
|-----------|--------|-------|---------|
| `planet_pitch_diam` | 27.5mm | **29.082mm** | Formula.8 |
| `planet_mid_path` | 23.75mm | **22.959mm** | Formula.17 |
| `ring_gear_OD` | 101.25mm | **95mm** | Formula.71 |
| `housing_ring_gear_bore` | 101.55mm | **95.3mm** | Formula.60 |
| `housing_width` | 115.25mm | **109mm** | Formula.32 |
| `lid_step_OD` | 101mm | **94.75mm** | Formula.66 |
| Sandwich fastener bolt circle | 91.25mm dia | **85mm dia** | Formula.55 |

**Check:** `ring_gear_OD` should read 95mm. `housing_ring_gear_bore` should read 95.3mm (matches STEP ring OD of 95mm + 0.3mm clearance).

### Carrier cutout formula (external part)

`planet_pitch_diam + 2*gear_module + carrier_planet_clearance` — gear_module is now 0, so this becomes `planet_pitch_diam + carrier_planet_clearance` = 29.082 + 1.25 = **30.332mm**. No action needed.

### Final parameter values after cleanup

| Parameter | Final value | How |
|-----------|------------|-----|
| `sun_pitch_diam` | **16.836mm** | **You set this** |
| `gear_module` | **0mm** | **You set this** |
| `planet_pitch_diam` | 29.082mm | Auto — Formula.8 |
| `planet_mid_path` | 22.959mm | Auto — Formula.17 |
| `ring_gear_OD` | 95mm | Auto — Formula.71 |
| `housing_ring_gear_bore` | 95.3mm | Auto — Formula.60 |
| `housing_width` | 109mm | Auto — Formula.32 |
| `lid_step_OD` | 94.75mm | Auto — Formula.66 |

---

## Step 1 — Import STEP → gear_part_output

1. Open `gearbox_CAD.step` (run 002) — import as a **Part** (not Product/Assembly)
2. All bodies land in one shared coordinate system — rigid, nothing drifts
3. Save as native CATPart (`gear_part_output_rev01`)
4. Insert into the `gears` product as a sibling to `skel_ref` and `gear_set`
5. Bodies: MANIFOLD_SOLID_BREP entries (sun, planets, ring halves)

The `_CAD` file uses a `TopoDS_Compound` — all bodies share one origin, primary axis on Z.

**If STEP import creates an assembly:** Re-import and explicitly choose "Import as Part" / "As Result". The file is a compound (multi-body), not an assembly.

---

## Step 2 — Constrain to Skeleton

Each part in the `gears` product independently pulls skeleton publications via Paste Link into its own external references. Don't cross-reference between sibling parts — go directly to the master skeleton.

`gear_part_output` needs at minimum:
- `PUB_Gear_midplane`
- `PUB_z_axis`
- `PUB_planet_center_datum_axis`

Constrain `gear_part_output` to `skel_ref`:

| Constraint | From (gear_part_output) | To (skel_ref) | Purpose |
|------------|------------------------|---------------|---------|
| Coincidence (axis) | Sun bore axis | `PUB_z_axis` | Concentric with gearbox axis |
| Coincidence (plane) | Ring split face at $z=0$ | `PUB_Gear_midplane` | Axial positioning |
| Fix rotation | Part X-axis or planet_0 direction | Skeleton X-axis | Prevent free spin |

The entire multi-body part locks in place. All internal geometry (planet positions, ring wall, tooth profiles) is already correct because it was built relative to the origin in CadQuery.

---

## Step 3 — Verify Fit

After constraining, check:

- [ ] Ring OD sits inside `housing_ring_gear_bore` (95.3mm bore, ring OD = 95mm → 0.15mm radial gap)
- [ ] Planets sit at the correct orbital radius — compare planet center distance against skeleton `planet_mid_path` (22.959mm)
- [ ] Gear midplane aligns with skeleton `Gear_midplane` datum
- [ ] No interference between planet tips and ring root / sun root (visual check in section view)
- [ ] Planet interference with carrier — `carrier_planet_clearance` (1.25mm) was designed for involute teeth; cycloidal have different tip profiles, may need adjustment

---

## Step 4 — Skeleton-Driven Cuts (later)

Operations live in the `cutting/adding bodies` part — a separate sibling in the `gears` product. This part is **not dependent on any specific gear part** — it references skeleton datums only.

- Use the **same sketches/profiles** that `gear_set` uses (referencing skeleton datums, not STEP faces)
- Bearing bores: sketch on `PUB_Gear_midplane`, pad through body using `PUB_planet_center_datum_axis`
- Bolt holes: reference `PUB_planet_bearings` sketch
- Boolean Remove the cutting bodies against STEP bodies in `gear_part_output`

**Key rule:** Every sketch and limit must reference a skeleton datum or the `outline` profiles — never a STEP face. This is what makes STEP swapping possible and cutting bodies reusable across revisions.

---

## Step 5 — STEP Swap (future runs)

When a new `gearbox_CAD.step` is generated (new run from pygeartrain):

1. In `gear_part_output`, locate the base STEP bodies
2. Replace/re-insert with new STEP file (save as new rev, e.g. `gear_part_output_rev02`)
3. Cutting bodies recompute automatically — they reference skeleton datums, not STEP faces
4. Check for broken references (should be none if Step 4 was done correctly)

Should be a ~5 minute operation per new STEP version.

---

## Step 6 — Manufacturing Export

For each gear body in `gear_output`:
- Extract body → individual STEP/STL for printing or machining
- Or use `_PRINT` files from pygeartrain directly if no skeleton-driven cuts were applied to that body

CadQuery export types:

| File | Purpose |
|------|---------|
| `sun_PRINT.step/.stl`, `planet_N_PRINT.step/.stl`, `ring_top/bottom_PRINT.step/.stl` | Clean individual parts → slicer or manufacturer |
| `gearbox_CAD.step` | Multi-body part (all gears in one coordinate system) → CATIA |

---

## Open Questions (to test in CATIA)

- **Does CATIA allow "Replace" on a STEP-derived body?** If yes, Step 5 is trivial. If no: delete old bodies, insert new ones, cutting bodies recompute.
- **Circular pattern of planets:** `gear_set` uses `CircPattern.2` to pattern planet operations. Does this work when applied to STEP bodies via cutting bodies? Or does each planet need operations individually?
- **Boolean workflow:** How does the cutting/adding bodies part apply its operations to `gear_part_output`? Product-level boolean, or assembly-level cut? Need to test.

---

## What Not To Do

- **Don't reference STEP faces in operations** — any face picked directly from the STEP body will break when the STEP is swapped
- **Don't fuse gear_set and gear_part_output into one part** — keeps things clean and lets gear_set stay as pure parametric reference
- **Don't delete gear_set** — it's the parametric backbone, needed for interference checks and skeleton validation
- **Don't cross-reference external params between sibling parts** — each part pulls directly from the master skeleton. Cross-part references were unreliable in practice.

---

## What the Skeleton Still Drives

Even with real gear geometry imported, the skeleton controls:
- Carrier plate dimensions (top/bottom thickness, clearances)
- Housing bore, wall thickness, mounting layout
- Bearing seats (main bearing, planet bearings)
- Fastener patterns (sandwich bolts, planet pins)
- Overall packaging envelope

The gear STEP bodies don't replace the skeleton — they complement it with real tooth geometry.

---

## Troubleshooting

**STEP import looks wrong / no solid body:**
- Try importing with "As Result" rather than "As Specification" if available
- If compound import fails, import individual `_PRINT` files one at a time

**Gears don't align with skeleton:**
- Verify the part's origin matches the skeleton origin
- STEP files use mm units — confirm CATIA is set to mm

**Ring doesn't fit in housing:**
- Ring OD should be 95mm, housing bore 95.3mm
- If ring OD appears different, check that the script ran with `RING_WALL_MM = 10` and `TARGET_RING_DIAMETER_MM = 75`
