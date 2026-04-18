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
- Static phasing is still the active technical risk. A CadQuery solid-intersection check showed zero solid overlap for the current manual phase values, but the preview images still need a stronger sampled-outline audit before calling the mesh verified.

## Important Dependency Note

- The local clone at `C:/Users/aaron/Documents/c-projects/_dump/cq_gears` was patched during this work so `PlanetaryGearset` forwards `addendum_coeff` and `dedendum_coeff` into the generated sun, planet, and ring gears.
- That dependency patch is outside the `qdd-gearbox` repo and is therefore not captured by this repo commit.
- Next revision should either vendor that change into the repo or remove the dependency on the external patched clone.

## Next Revision Focus

- Replace the slow mesh-audit approach with a fast sampled-outline audit.
- Use that audit to verify or correct the static phasing analytically instead of by preview image inspection.
- Keep the same ratio and keep the cycloidal path untouched.
