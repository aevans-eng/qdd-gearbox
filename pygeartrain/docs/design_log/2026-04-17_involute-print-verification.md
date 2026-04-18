# 2026-04-17 Involute Print Verification

## Current Design

- Source generator: `pygeartrain\generate_step_aaron_cq_gears.py`
- Gearset: `R72 / P27 / S18`
- Ratio: `5.000:1`
- Module: `1.0204 mm`
- Pressure angle: `20.0 deg`
- Face width: `18.6 mm`
- Orbit radius: `22.959 mm`
- Sun OD: `19.898 mm`
- Planet OD: `29.082 mm`
- Ring inner tip diameter: `71.938 mm`
- Ring root diameter: `75.000 mm`
- Ring OD: `95.000 mm`

## Tooth Proportions

- Addendum coefficient: `0.7501`
- Dedendum coefficient: `0.6866`
- Addendum depth: `0.765 mm`
- Dedendum depth including root clearance: `0.766 mm`
- Radial root clearance target: `0.065 mm`

## Mesh Checks

- External sun-planet contact ratio estimate: `1.236`
- This is the strongest simple check available locally for the current involute export path.

## Rough Torque Capacity

- PLA+ target-safety-factor torque: `8.38 Nm`
- PLA+ first-yield-ish torque: `18.86 Nm`
- PLA+ governing mode: `contact`
- Nylon PA6 target-safety-factor torque: `19.82 Nm`
- Nylon PA6 first-yield-ish torque: `44.60 Nm`
- Nylon PA6 governing mode: `contact`

## Same-Package Same-Ratio Family Sweep

Families compared by keeping the same pitch diameters and ratio, then changing tooth counts and module together.

| Family | Module (mm) | Contact ratio | PLA+ target SF torque (Nm) | Nylon target SF torque (Nm) |
| --- | ---: | ---: | ---: | ---: |
| `R48/P18/S12` | 1.5306 | 0.824 | 8.38 | 19.82 |
| `R72/P27/S18` | 1.0204 | 1.236 | 8.38 | 19.82 |
| `R96/P36/S24` | 0.7653 | 1.648 | 8.38 | 19.82 |
| `R120/P45/S30` | 0.6122 | 2.059 | 8.38 | 19.82 |

## Recommendation

- The first same-package family that clears the `contact ratio >= 1.2` screen is `R72/P27/S18`.
- That makes `18/27/72` the better printable baseline than `12/18/48` under the current packaging constraints because the mesh overlap is no longer obviously deficient.
- The visible shallow dedendum problem is materially improved by moving away from the `12/18/48` family.
- This can be treated as the better fit-checked involute baseline, but it is still not a verified 16 Nm PLA+ design.

## Static Assembly Verification

- Updated baseline export: `pygeartrain/step_output_aaron_cq_gears/spur/009/gearbox_CAD.step`
- Static phasing for the current `R72 / P27 / S18` baseline was corrected from the generic `cq_gears` default.
- Verified by direct CadQuery solid-intersection checks:
  - sun vs each planet: `0.0 mm^3`
  - ring vs each planet: `0.0 mm^3`
- Updated preview image: `pygeartrain/step_output_aaron_cq_gears/spur/009/mesh_preview_contact.png`
- This resolves the earlier out-of-phase sun/planet overlap seen in the previous PNG previews.
