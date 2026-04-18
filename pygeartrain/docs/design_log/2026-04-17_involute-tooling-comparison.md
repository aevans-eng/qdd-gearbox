# 2026-04-17 — Involute Tooling Comparison

## Context

Current workspace status:

- Original QDD path uses a forked `pygeartrain`, originally from [EelcoHoogendoorn/pygeartrain](https://github.com/EelcoHoogendoorn/pygeartrain)
- Cycloidal planetary generation still fits the original `pygeartrain` model well
- The involute work is currently in a standalone copy:
  - `pygeartrain/generate_step_aaron_involute.py`

## Original animation path

The original library still supports animation through the geometry classes:

- local code: `pygeartrain/pygeartrain/core/geometry.py`
- methods: `animate()` and `save_animation()`

That matches the upstream repo description that concrete gear profile geometries can be "plot and animate[d] ... to validate their intended functioning" ([upstream pygeartrain README](https://github.com/EelcoHoogendoorn/pygeartrain)).

## Why the involute copy drifted out of sync

The root cause was **not** that planetary equations were wrong.

The original `pygeartrain` planetary path works because:

- one coherent gear set is generated together
- the internal tooth indexing is consistent before any motion is applied
- the `arrange(...)` step then moves an already-meshing set

The first involute copy did something different:

- sun generated independently
- planets generated independently
- ring generated independently
- then only the carrier-placement logic was reused

That meant there was no shared initial tooth phase between:

- sun and planet
- planet and ring

So the 2D/GIF motion was not a true inherited `pygeartrain` meshing result. It was a custom placement/rotation approximation layered on top of independently generated involute profiles.

## Candidate alternatives

### 1. `heartworm/py_gear_gen`

Repo: [heartworm/py_gear_gen](https://github.com/heartworm/py_gear_gen)

What the README explicitly claims:

- involute spur gear generation
- adjustable accuracy
- gear root filleting
- internal ring gearing option
- adjustable module, tooth number, pressure angle, and backlash

Source: repo README on GitHub.

Limitations explicitly acknowledged by the author:

- author says it was their "first foray" and there may be math errors
- docs are minimal: "check out `example_usage.py` and comments"
- TODO includes:
  - review all mathematics and algorithms
  - get fillets working on internal gears
  - STL output for helical and other gears

Fit for QDD:

- good as a **2D involute reference**
- useful if the main need is spur/ring profile generation with backlash
- weaker fit for the current workflow because it does not present itself as a mature 3D/CadQuery planetary export tool

### 2. `meadiode/cq_gears`

Repo: [meadiode/cq_gears](https://github.com/meadiode/cq_gears)

What the README explicitly claims:

- CadQuery-based involute gear parametric modelling
- can generate:
  - spur
  - helical
  - herringbone
  - ring gear
  - planetary gearsets
  - bevel gears
  - racks

Source: repo README on GitHub.

Important caveat explicitly stated in the README:

- "Work in progress..."
- "Might be unstable, but somewhat usable."

Other practical notes from the README:

- requires CadQuery
- examples are provided
- build model is already CadQuery-native rather than 2D-first

Fit for QDD:

- strongest functional fit for the current workflow
- especially relevant because the current QDD script already uses CadQuery for STEP/STL export
- likely a better base if the goal is to move from ad-hoc involute export toward a more complete involute planetary generator

## Recommendation

If we keep involute work alive, the best next candidate is:

- `cq_gears`

Reason:

- it already targets involute geometry
- it already supports ring gears and planetary gearsets
- it is CadQuery-native, which matches the current export flow much better than a 2D SVG/DXF-first script

`py_gear_gen` is still useful as a compact math/reference implementation, but it looks more like a profile generator than a full replacement for the current QDD export path.

## Practical next step

Best next move is not to keep expanding the current standalone involute copy blindly.

Instead:

1. keep the current copy as a sandbox/reference
2. evaluate whether `cq_gears` can directly produce the QDD involute planetary set
3. if yes, pivot involute generation onto that base rather than reimplementing more meshing logic manually

## Files affected locally

- `pygeartrain/generate_step_aaron_involute.py`
- `pygeartrain/docs/design_log/2026-04-17_involute-generator-copy.md`
- this note
