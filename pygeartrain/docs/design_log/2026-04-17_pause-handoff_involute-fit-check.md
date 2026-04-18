# 2026-04-17 Pause Handoff - Involute Fit / Assembly Verification

## Current Recommended Script

- Script: [generate_step_aaron_cq_gears.py](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/generate_step_aaron_cq_gears.py)
- Status: this is now the preferred involute path because it uses `cq_gears`' native planetary assembly logic instead of the earlier standalone involute sandbox.

## Why This Path Was Chosen

- The original cycloidal export path in `generate_step_aaron.py` is still intact.
- The earlier custom involute copy drifted out of phase because it generated sun, planet, and ring independently and only reused carrier placement math.
- `cq_gears` provides a native involute planetary assembly path, so the initial mesh phasing is much more trustworthy.

## What Is Already Working

- The `cq_gears` script successfully generates:
  - a STEP assembly
  - a compound STEP
  - individual gear STEP/STL files
  - mesh preview PNGs
  - a general mesh GIF
  - a slow contact diagnostic image/GIF path
- Previously verified complete output:
  - [spur/001](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/step_output_aaron_cq_gears/spur/001)

## What Was Retuned Most Recently

The latest edit to `generate_step_aaron_cq_gears.py` retunes the involute geometry to match the **cycloidal fit envelope**, instead of using a generic involute module choice.

Reference targets taken from the confirmed cycloidal notes:

- carrier radius: `22.959 mm`
- sun OD: `19.898 mm`
- planet OD: `29.082 mm`
- ring inner tip diameter: `71.938 mm`
- ring root diameter: `75.000 mm`
- ring outer diameter: `95.000 mm`

These targets came from:

- [skeleton-step-current-state.md](C:/Users/aaron/Documents/c-projects/qdd-gearbox/docs/catia/skeleton-step-current-state.md)
- original cycloidal exports under [step_output_aaron/spur/000](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/step_output_aaron/spur/000)

## Important Derived Involute Fit Values

These are now computed in the script from the cycloidal reference dimensions:

- module: `2 * carrier_radius / (sun_teeth + planet_teeth)`
- addendum coefficient: averaged from:
  - sun OD target
  - ring inner tip target
- dedendum coefficient: averaged from:
  - planet OD target
  - ring root target
- rim width: derived from ring OD minus ring root diameter

The tooth counts remain:

- ring: `48`
- planet: `18`
- sun: `12`
- planets: `3`

That means the involute copy is still preserving the same tooth-count-based reduction structure as the cycloidal set.

## Measurements Already Collected

### Original cycloidal export dimensions

Measured / confirmed from notes and STEP checks:

- sun OD: about `19.898 mm`
- planet OD: about `29.082 mm`
- ring OD: `95.000 mm`
- ring root diameter: `75.000 mm`
- ring inner tip diameter: about `71.938 mm`

### Earlier cq_gears attempt before fit retune

These were too large:

- sun OD: `21.875 mm`
- planet OD: about `31.25 mm`
- ring OD: about `98.906 mm`

That mismatch is what triggered the fit-envelope retune.

## Current Partial Run State

- A new run folder exists at:
  - [spur/002](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/step_output_aaron_cq_gears/spur/002)
- That run is **partial only** because the long export was interrupted before completion.
- Files confirmed present in `spur/002`:
  - `mesh_preview_full.png`
  - `mesh_preview_zoom.png`
  - `mesh_preview_contact.png`
  - `mesh_animation.gif`
  - `sun_planet_contact_geometry.png`
- Missing / not yet confirmed from that interrupted run:
  - `sun_planet_contact_slowmo.gif`
  - individual STEP exports
  - final assembly STEP export

Do **not** treat `spur/002` as fully verified.

## Open Technical Questions To Resume With

1. Verify the retuned `cq_gears` set actually exports a valid full assembly STEP after the fit-envelope patch.
2. Measure the retuned involute outputs directly against the original cycloidal parts:
   - sun external diameter
   - planet external diameter
   - ring outer diameter
   - ring inner tip diameter
   - ring root diameter
3. Confirm the involute set still fits the existing carrier / clearance envelope closely enough to avoid a reprint.
4. Tune involute clearance based on the cycloidal clearance intent, instead of only using generic involute backlash values.
5. Confirm the reduction remains the same in the final assembly configuration.

## Recommended Next Steps

1. Re-run [generate_step_aaron_cq_gears.py](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/generate_step_aaron_cq_gears.py) with a long enough timeout to finish the full export.
2. Measure the new retuned run against:
   - [step_output_aaron/spur/000](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/step_output_aaron/spur/000)
   - [skeleton-step-current-state.md](C:/Users/aaron/Documents/c-projects/qdd-gearbox/docs/catia/skeleton-step-current-state.md)
3. If the diameters are close enough, document the fit delta explicitly in [2026-04-17_cq-gears-qdd-generator.md](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/docs/design_log/2026-04-17_cq-gears-qdd-generator.md).
4. Then tune involute clearance using the cycloidal reference clearances and re-export the assembly STEP plus diagnostic GIFs.

## Practical Resume Note

If the goal is to avoid reprinting the carrier, the dimensions that matter most are:

- planet OD
- ring OD
- ring inner tooth envelope
- carrier orbit radius

The retune in the script was specifically aimed at those fit-critical dimensions.
