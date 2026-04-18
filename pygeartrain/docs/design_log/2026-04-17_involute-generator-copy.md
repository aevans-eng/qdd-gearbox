# 2026-04-17 — Involute Generator Copy: Phase Fix + Print Tweaks

## Scope

Work applies only to:

- `pygeartrain/generate_step_aaron_involute.py`

The original cycloidal exporter in `pygeartrain/generate_step_aaron.py` was left intact.

## Problem

The first involute preview exported valid solids, but the teeth were visibly out of phase:

- planet teeth did not index correctly against the sun
- ring teeth did not line up with the planet gaps
- root transitions were sharp and not ideal for FDM printing

## Root cause

The original cycloidal generator *does* predefine the interfacing, but only because it generates a single internally consistent gear set through `PlanetaryGeometry.create(...)` and `planetary.generate_profiles(...)`.

That path:

- creates ring, planet, and sun from the same cycloidal construction
- uses a shared tooth-phase convention during profile generation
- applies a special even-tooth sun offset before animation/export
- then uses `arrange(...)` only to move an already meshing set through kinematic motion

The first involute copy did **not** have that property.

It built:

- sun profile independently
- planet profile independently
- ring profile independently

Each profile started from its own local tooth-center reference, then I reused only the carrier-placement term from the cycloidal arrangement logic:

- `spin = (1 - R/P) * carrier_angle`

That was not enough for involute geometry, because there was no shared initial tooth indexing between:

- sun vs planet
- planet vs ring

So the gears were not "mathematically broken" at the pitch-diameter level. They were missing the **base phase relationship** that the original cycloidal path gets implicitly from its shared generator.

## Changes made

### 1. Added involute-specific mesh phase offsets

The cycloidal arrangement logic was not enough on its own for the involute copy.

- Added a fixed planet base phase offset before applying the carrier-dependent spin term
- Added a fixed ring base phase offset so the internal teeth line up with the planet gaps

These are now reported in script output for traceability.

### 2. Kept the overall gearbox size envelope the same

Did **not** increase module, because for a fixed tooth count that would force a larger pitch diameter and drift away from the current QDD package size.

Instead, the involute copy keeps:

- `R48 / P18 / S12`
- ring pitch diameter target = `75 mm`

That preserves the general size reference from the existing cycloidal setup.

### 3. Switched to more print-friendly tooth proportions

Changed from a more standard full-depth involute toward a stubbier, stronger tooth:

- pressure angle: `20 deg -> 25 deg`
- addendum coefficient: `1.00 -> 0.85`
- dedendum coefficient: `1.25 -> 1.00`

Intent:

- thicker tooth bases
- less undercut risk pressure on the low-tooth-count sun
- less slender tooth tips for FDM

### 4. Added root blending

The earlier version effectively had a hard transition from root circle to involute flank.

Added a root blend in the involute copy:

- cubic blend segment between root circle and involute flank
- blend radius target = `0.45 mm`

Intent:

- reduce stress concentration
- reduce sharp internal corners
- produce a shape that is more printable and less notch-sensitive

This is a print-oriented blend, not a strict trochoid fillet model.

### 5. Increased backlash slightly

Changed per-gear radial profile offset from:

- `-0.025 mm -> -0.040 mm`

Intent:

- give the printed involute teeth a bit more assembly margin
- reduce the chance that printer OD growth locks the mesh

## Verification outputs

The involute copy now saves 2D top-down verification images in each run folder:

- `mesh_preview_full.png`
- `mesh_preview_zoom.png`
- `mesh_preview_contact.png`
- `mesh_animation.gif`

These are meant for quick visual checks of:

- tooth outline shape
- phasing
- sun/planet and planet/ring mesh alignment
- rolling motion across a short kinematic cycle

## Follow-up

If this involute path becomes more serious, the next improvement should be:

- true involute profile-shift support for the low-tooth-count sun

That would be a more correct way to fight undercut than continuing to push printability only through pressure angle and stub tooth proportions.
