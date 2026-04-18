# 2026-04-18 Involute Status Note

## Scope

- This note covers only the involute development path.
- The original cycloidal generator at `pygeartrain/generate_step_aaron.py` is intentionally unchanged and remains the reference path.

## Current Involute Files

- `pygeartrain/generate_step_aaron_involute.py`
- `pygeartrain/generate_step_aaron_cq_gears.py`
- `calc/involute_print_verification.py`
- `calc/involute_mesh_audit.py`

## Current State

- The current packaging-matched involute baseline is `R72 / P27 / S18` at `20 deg`.
- The assembly export path is `pygeartrain/generate_step_aaron_cq_gears.py`.
- The current assembly STEP export is intended to come out already positioned correctly in one export step.
- Static phasing is no longer being judged by the old preview logic alone.
- Root cause of the apparent overlap: the old static preview path rotated each planet body with its orbit angle, while the solid STEP assembly path uses a constant planet tooth phase at each translated planet center.
- Direct solid checks for the current static STEP placement gave zero intersection volume for sun-vs-planet and ring-vs-planet on all three planets.
- A fast sampled-outline audit now follows the same static body placement as the STEP export path.
- Current verified static outputs:
  - `pygeartrain/step_output_aaron_cq_gears/spur/011/gearbox_CAD.step`
  - `pygeartrain/step_output_aaron_cq_gears/spur/011/mesh_preview_contact.png`
  - `pygeartrain/docs/design_log/2026-04-17_involute-mesh-audit.md`

## Important Dependency Note

- The local clone at `C:/Users/aaron/Documents/c-projects/_dump/cq_gears` was patched during this work so `PlanetaryGearset` forwards `addendum_coeff` and `dedendum_coeff` into the generated sun, planet, and ring gears.
- That dependency patch is outside the `qdd-gearbox` repo and is therefore not captured by this repo commit.
- Next revision should either vendor that change into the repo or remove the dependency on the external patched clone.

## Next Revision Focus

- Replace the slow mesh-audit approach with a fast sampled-outline audit.
- Use that audit to verify or correct the static phasing analytically instead of by preview image inspection.
- Keep the same ratio and keep the cycloidal path untouched.
