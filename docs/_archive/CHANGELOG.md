# Changelog — QDD Gearbox Project

All notable design decisions and milestones are logged here.

## 2026-03-01

- **Reorganized `pygeartrain/` folder**
  - Top level went from 70+ items to 11 — Aaron's active files stay, everything else sorted
  - `docs/` — reference docs, images, design log, version history
  - `tools/` — utility/validation/visualization scripts
  - `_collab_history/` — collaborator's versioned scripts (v17–v24) and their output dirs
  - Core library `pygeartrain/`, `generate_step_aaron.py`, `step_output_aaron/` unchanged

- **Herringbone loft: investigated intermediate sections, reverted to original**
  - Tried adding intermediate loft profiles to improve helix fidelity (original was 2 profiles per half = ruled surface)
  - Attempt 1 (smooth loft, `LOFT_SECTIONS_PER_HALF=1`): B-spline interpolation caused inward/outward bulging at midplane
  - Attempt 2 (ruled loft, `isRuled=True`, 4 sections): still produced bad geometry
  - Fully reverted to original v24 loft logic — byte-for-byte match, confirmed by entity counts
  - Known-good script saved to `step_output_aaron/_versions/generate_step_aaron_2026-03-01_working.py`
  - **Lesson:** don't modify geometry code without visual verification and a committed rollback point
  - **TODO:** improving herringbone helix fidelity needs a fundamentally different approach (sweep along helical path, not loft between rotated cross-sections)

- **STEP reference geometry: investigated and rejected**
  - Tried adding thin construction bodies (planes, axes) to assembly STEP for CATIA constraining
  - Problem 1: if you constrain to them then deactivate, constraints break — they'd show up in prints
  - Problem 2: STEP doesn't carry per-body coordinate systems — all embedded planes/axes land at global origin regardless of body position
  - Investigated SolidWorks/Parasolid export — not possible from CadQuery (proprietary formats)
  - AP214/AP242 don't help either for CadQuery-generated geometry
  - **Resolution:** create reference geometry manually in CATIA after import (sun bore = axis, ring split face = midplane, planet\_0 at +X = rotation fix)

- **Adopted multi-body part workflow for CATIA integration**
  - Based on established CAD integration principles: STEP as assembly = bad (DOF drift), STEP as multi-body part = good (one coordinate system, frozen bodies)
  - Renamed exports: `_PRINT` files (individual parts for manufacturing), `_CAD` file (multi-body compound for CATIA)
  - `gearbox_CAD.step` = `TopoDS_Compound`, imports as a part not an assembly
  - Dropped STL export for the compound (not needed — manufacturing uses individual `_PRINT` files)
  - Rewrote `catia-step-integration.md` with full 5-stage workflow: CadQuery export → STEP import as part → skeleton mating → boolean operations → manufacturing output
  - Documented STEP limitations (no per-body datums) and how to create reference geometry from pickable faces in CATIA

## 2026-02-28

- **Gear tooth profile: Cycloidal (not involute)**
  - pygeartrain library generates cycloidal (epi/hypocycloid) teeth via CadQuery
  - This means `gear_module = 2.5mm` (involute concept) doesn't apply — scaling is done via `TARGET_RING_DIAMETER_MM` + tooth counts
  - Existing stress calcs in `calc/tooth_stress.py` assume involute Lewis bending + Hertzian contact — they don't directly apply to cycloidal teeth
  - Cycloidal profile is well-suited for 3D-printed, low-speed, low-tooth-count gears
  - Trade-off accepted: simpler manufacturing/meshing vs. less standard stress analysis

- **Generated STEP files for CATIA integration**
  - Script: `pygeartrain/generate_step_aaron.py`
  - Parameters: R48/P18/S12, 3 planets, 5:1 ratio, 75mm ring ID, 18.6mm face width
  - Ring output as two halves (ring_top/ring_bottom) — required for herringbone internal teeth
  - No fastener holes in STEP — CATIA skeleton handles all features
  - Output: `pygeartrain/step_output_aaron/`
  - Key dimensions for skeleton update:
    - Sun outer diameter: 19.9mm
    - Planet outer diameter: 29.1mm
    - Ring inner diameter: 71.9mm
    - Ring outer diameter: 95.0mm
    - Carrier radius (planet center): 23.0mm

## 2026-02-01

- Restructured project: added `calc/`, `ui/`, `drawings/`, `tests/` directories
- Added Python design calculators: gear_geometry, tooth_stress, bearing_life, thermal
- Completed BOM with fasteners, inserts, filament, lubrication (est. ~$75 CAD)
- Added GD&T notes for critical features
- Added test/verification plan

## 2026-01 (Project Kickoff)

- Established requirements (docs/01-requirements.md)
- Completed trade studies: planetary reduction, 5:1 ratio, ball bearings (docs/02-trade-studies.md)
- Defined system architecture and interfaces (docs/03-system-design.md)
- Created detailed design plan and assembly stack (docs/04-detailed-design.md)
- Initial BOM with bearings (docs/05-parts-list.md)
