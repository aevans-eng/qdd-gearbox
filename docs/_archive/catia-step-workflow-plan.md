# CATIA STEP Integration Workflow — Planning Doc

**Status:** Skeleton cleanup in progress (prerequisite to STEP import)
**Goal:** A scaleable workflow to apply skeleton-driven operations to STEP gear geometry, with easy STEP swapping as the design evolves.

**Prerequisite — Skeleton cleanup required before STEP import.**
Skeleton was built for involute gears (module=2.5mm). New geometry is cycloidal — several formulas are wrong and must be fixed first.
Script rerun complete (run 002). All values confirmed. Full details: `docs/notes/skeleton-step-current-state.md`

---

## Step 0 — Skeleton Cleanup (do this before STEP import)

**Two parameter value changes. No formula editing.**

Open SKEL_Gearbox in CATIA → parameter list (Tools > Parameters or formula editor).

| Parameter | New value | Why |
|-----------|-----------|-----|
| `sun_pitch_diam` | **16.836mm** | Actual sun pitch diameter. Formula.8 and Formula.17 cascade everything else automatically. |
| `gear_module` | **0mm** | Zeroes out module term in ring_gear_OD and carrier cutout. Safe — no formulas divide by it. |

`ring_pitch_diam` stays at 75mm — already correct.
`planet_pitch_diam` is driven by Formula.8 `(ring_pitch_diam - sun_pitch_diam)/2` — updates automatically.
`planet_mid_path` is driven by Formula.17 `(sun_pitch_diam + planet_pitch_diam)/2` — updates automatically.

**What will cascade (expect these — all correct):**

| Parameter | Before | After | Formula |
|-----------|--------|-------|---------|
| `ring_gear_OD` | 101.25mm | **95mm** | Formula.71 (just changed) |
| `housing_ring_gear_bore` | 101.55mm | **95.3mm** | Formula.60: ring_gear_OD + ring_housing_diam_offset |
| `housing_width` | 115.25mm | **109mm** | Formula.32: ring_gear_OD + 2×Housing_min_wall_thickness |
| `lid_step_OD` | 101mm | **94.75mm** | Formula.66: ring_gear_OD - lid_step_clearance |
| Sandwich fastener bolt circle | 91.25mm dia / 45.625mm radius | **85mm dia / 42.5mm radius** | Formula.55: ring_gear_OD - ring_wall_thickness |

**Check:** ring_gear_OD should read 95mm. housing_ring_gear_bore should read 95.3mm (this now correctly matches the STEP ring OD of 95mm + 0.3mm clearance).

---

### Note — carrier cutout formula (external part)

`planet_pitch_diam + 2*gear_module + carrier_planet_clearance` — gear_module is now 0, so this automatically becomes `planet_pitch_diam + carrier_planet_clearance` = 29.082 + 1.25 = **30.332mm**. No action needed.

---

### Final parameter values after cleanup

| Parameter | Final value | How |
|-----------|------------|-----|
| `sun_pitch_diam` | **16.836mm** | **You set this** |
| `gear_module` | **0mm** | **You set this** |
| `planet_pitch_diam` | 29.082mm | Auto — Formula.8: `(ring_pitch_diam - sun_pitch_diam)/2` |
| `planet_mid_path` | 22.959mm | Auto — Formula.17: `(sun_pitch_diam + planet_pitch_diam)/2` |
| `ring_gear_OD` | 95mm | Auto — Formula.71 |
| `housing_ring_gear_bore` | 95.3mm | Auto — Formula.60 |
| `housing_width` | 109mm | Auto — Formula.32 |
| `lid_step_OD` | 94.75mm | Auto — Formula.66 |

---

## Current State

### What exists
- **SKEL_Gearbox** — master skeleton, publishes all key datums (gear midplane, planet center axes, motor face, shaft plane, bearing positions, fastener patterns)
- **gear_set** (`gear_set A.1`) — placeholder CATPart with:
  - `outline` body — skeleton-driven reference geometry (gear pitch profiles, planet bearing positions from `PUB_planet_bearings`)
  - `sun`, `planets`, `ring_bottom`, `ring_top` bodies — simple parametric geometry with operations applied (Pad, CircPattern, Remove)
  - All operations reference skeleton datums, NOT raw STEP faces
- **gearbox_CAD.step** — real cycloidal herringbone tooth geometry from pygeartrain (R48/P18/S12, 5:1, multi-body part)

### The problem
The gear_set placeholder is parametric and skeleton-driven — it's valuable and should not be replaced. But it has simple/approximate geometry (no real tooth profiles). The STEP file has real tooth geometry but no operations (bearing bores, bolt holes, etc.). Need a way to combine both without sacrificing parametric flexibility or making STEP swapping painful.

### Constraints
- gear_set placeholder must stay — it drives downstream parametric modeling
- STEP swap must be low-friction (new pygeartrain run → update output part without rebuilding everything)
- Operations (bearing bores, bolt holes, removes) must stay skeleton-driven — they should not reference STEP faces directly
- Must work within CATIA 3DEXPERIENCE Part Design

---

## Proposed Workflow

### Core principle
**Two separate parts coexist in the assembly:**

| Part | Role | Geometry source |
|------|------|----------------|
| `gear_set` | Parametric master — drives checks, interference, downstream features | Simple pads, skeleton-driven |
| `gear_output` | Manufacturing geometry — real tooth profiles + skeleton-driven cuts | STEP base + operations |

The skeleton is the single source of truth for both. Neither part references the other.

### Stage 1 — Build `gear_output` part (first time)

1. Create a new CATPart: `gear_output`
2. Pull external references from SKEL_Gearbox (same ones gear_set uses):
   - `PUB_Gear_midplane`
   - `PUB_planet_center_datum_axis`
   - `PUB_planet_bearings`
   - `PUB_REF_Motor_Face`
   - etc.
3. Insert `gearbox_CAD.step` bodies into this part (Insert > Existing Component or equivalent)
   - Bodies land as: sun, planet_0/1/2, ring_bottom, ring_top
4. For each body, apply skeleton-driven operations:
   - Use the **same sketches/profiles** that gear_set uses (referencing skeleton datums, not STEP faces)
   - Bearing bores: sketch on `PUB_Gear_midplane`, pad through body using `PUB_planet_center_datum_axis`
   - Bolt holes: reference `PUB_planet_bearings` sketch
   - These are the same operations as in gear_set — just applied to STEP bodies as the host

> **Key rule:** Every sketch and limit must reference a skeleton datum or the `outline` profiles — never a STEP face. This is what makes STEP swapping possible.

### Stage 2 — STEP swap (future runs)

When a new `gearbox_CAD.step` is generated (new run number from pygeartrain):

1. In `gear_output`, locate the base STEP bodies
2. Replace/re-insert with new STEP file
3. Operations recompute automatically — because they reference skeleton datums, not STEP faces
4. Check for any broken references (should be none if Stage 1 was done correctly)

This should be a ~5 minute operation per new STEP version.

### Stage 3 — Manufacturing export

For each gear body in `gear_output`:
- Extract body → individual STEP/STL for printing or machining
- Or use `_PRINT` files from pygeartrain directly if no skeleton-driven cuts were applied to that body

---

## Open Questions

- **How to insert STEP bodies into an existing CATPart in CATIA 3DEXPERIENCE?** Options: Insert > Body from file, Copy-Paste from another Part, or link via external reference. Need to test which preserves the body as a stable host for operations.
- **Does CATIA allow "Replace" on a STEP-derived body?** If yes, Stage 2 is trivial. If no, the workflow is: delete old bodies, insert new ones, re-run operations (they recompute since they're skeleton-driven).
- **Circular pattern of planets:** gear_set uses `CircPattern.2` to pattern the planet operations. Does this work the same way on STEP bodies? Or does each planet body need operations applied individually?
- **Are the Remove operations in gear_set using the STEP body as host, or a pad as host?** If they're on pads, the strategy is: insert STEP body as base, boolean-remove the STEP body from the pad body, then apply cuts. If on the STEP body directly, much simpler.

---

## What Not To Do

- **Don't apply operations referencing STEP faces** — any face picked directly from the STEP body will break when the STEP is swapped
- **Don't fuse gear_set and gear_output into one part** — keeps things clean and lets gear_set stay as pure parametric reference
- **Don't delete gear_set** — it's the parametric backbone, needed for interference checks and skeleton validation

---

## Files

| File | Location |
|------|----------|
| Skeleton | CATIA assembly — SKEL_Gearbox A.1 |
| Placeholder part | CATIA assembly — gear_set A.1 |
| STEP generator | `pygeartrain/generate_step_aaron.py` |
| Latest STEP output | `pygeartrain/step_output_aaron/001/gearbox_CAD.step` |
| CATIA integration notes | `docs/catia-step-integration.md` |
| Pipeline README | `pygeartrain/step_output_aaron/README.md` |
