# 2026-04-17 — QDD Involute Generator Using `cq_gears`

## Decision

For a working involute planetary export path, use:

- `pygeartrain/generate_step_aaron_cq_gears.py`

This is now the recommended involute path over the custom one-off involute script.

## Why this path won

The custom involute copy was building:

- sun profile independently
- planet profile independently
- ring profile independently

That made phase/indexing fragile.

`cq_gears` already provides:

- involute spur / helical / herringbone gears
- ring gears
- planetary gearsets
- a native `PlanetaryGearset.assemble()` method with explicit initial tooth phasing

Sources:

- local cloned repo: `_dump/cq_gears`
- upstream README: [meadiode/cq_gears](https://github.com/meadiode/cq_gears)

The README explicitly says it supports:

- spur gear
- helical gear
- herringbone gear
- ring gear
- planetary gearsets

## Current QDD setup

The script currently targets the QDD envelope with:

- tooth counts: `R72 / P27 / S18`
- carrier/orbit radius target: `22.959 mm`
- cycloidal fit targets:
  - sun OD: `19.898 mm`
  - planet OD: `29.082 mm`
  - ring inner tip diameter: `71.938 mm`
  - ring root diameter: `75.000 mm`
  - ring OD: `95.000 mm`
- teeth: `R48 / P18 / S12`
- face width: `18.6 mm`
- pressure angle: `20 deg`
- backlash: `0.08 mm`
- addendum coefficient: derived from the cycloidal fit targets
- dedendum coefficient: derived from the cycloidal fit targets

The involute ratio remains the same as the cycloidal set. The current baseline uses a higher same-ratio tooth-count family than the original `12/18/48` involute attempt because the original family was too shallow and failed the simple external contact-ratio screen.

## Outputs

Each run writes to:

- `pygeartrain/step_output_aaron_cq_gears/<gear_type>/<run>/`

Current outputs include:

- `sun_PRINT.step/.stl`
- `planet_0_PRINT.step/.stl` through `planet_2_PRINT.step/.stl`
- `ring_PRINT.step/.stl`
- `gearbox_CAD.step` — assembly STEP
- `gearbox_CAD_compound.step` — compound STEP
- `mesh_preview_full.png`
- `mesh_preview_zoom.png`
- `mesh_preview_contact.png`
- `mesh_animation.gif`
- `sun_planet_contact_geometry.png`
- `sun_planet_contact_slowmo.gif`

## Contact diagnostics

The script now also writes a focused sun-planet diagnostic view:

- `sun_planet_contact_geometry.png`
- `sun_planet_contact_slowmo.gif`

These emphasize one mesh pair and overlay classic involute references:

- pitch circles — dashed
- base circles — dotted
- line of centers — grey
- line of action — purple
- pitch point — black dot
- estimated instantaneous contact point — magenta dot

The magenta contact point is an estimate based on nearest sampled points on the
two tooth outlines. It is a good visual diagnostic, but it is not yet a full
analytical contact solver.

## Verification

Verified working run:

- `pygeartrain/step_output_aaron_cq_gears/spur/000`
- `pygeartrain/step_output_aaron_cq_gears/spur/001`
- `pygeartrain/step_output_aaron_cq_gears/spur/005`
- `pygeartrain/step_output_aaron_cq_gears/spur/006`
- `pygeartrain/step_output_aaron_cq_gears/spur/008`

Observed result:

- assembly export completed in one pass
- `spur/005` is the first fit-matched involute export
- STEP measurements from `spur/005` match the cycloidal envelope:
  - sun STEP OD: `19.898 mm`
  - planet STEP OD: `29.082 mm`
  - ring STEP OD: `95.000 mm`
  - assembly STEP OD: `95.000 mm`
- gear ratio is preserved because tooth counts stayed `R48 / P18 / S12`

`spur/006` is the fast assembly-only export with the involute mesh tuned from the
cycloidal print clearance intent.

- cycloidal reference used: `0.13 mm` total mesh clearance
- mapped involute radial root clearance: `0.065 mm`
- mapped involute backlash factor at `m = 1.5306`, `25 deg`: `0.0911`
- assembly STEP bounding box: `95.0 x 95.0 x 18.6 mm`
- no individual gear STEP/STL files exported by default

`spur/008` is the current printable involute baseline:

- family: `R72 / P27 / S18`
- pressure angle: `20 deg`
- same fit envelope as the cycloidal set
- external sun-planet contact ratio estimate: `1.236`
- materially better visible tooth proportions than the old `12/18/48` involute
- exported assembly file: `step_output_aaron_cq_gears/spur/008/gearbox_CAD.step`

See [2026-04-17_involute-print-verification.md](C:/Users/aaron/Documents/c-projects/qdd-gearbox/pygeartrain/docs/design_log/2026-04-17_involute-print-verification.md) for the more explicit verification summary.

## Important fix

The local `_dump/cq_gears` clone needed a small fix before fit retuning would work:

- `SpurGear` already accepted `addendum_coeff` / `dedendum_coeff`
- `RingGear` did not
- `PlanetaryGearset` was not forwarding those coefficients into the sun / planet / ring constructors

That forwarding path is now patched locally, which is why `spur/005` finally matches the cycloidal fit envelope.

## Notes

- The script currently imports `cq_gears` from the local clone in `_dump/cq_gears`
- This is intentional for speed; it avoids spending more time reimplementing involute meshing logic manually
- If this becomes the permanent path, the next cleanup step is to vendor or install `cq_gears` in a more formal location
