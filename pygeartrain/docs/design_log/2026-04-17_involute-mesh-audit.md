# 2026-04-17 Involute Mesh Audit

## Current Generator State

- Family: `R72 / P27 / S18`
- Pressure angle: `20.0 deg`
- Module: `1.0204 mm`
- Current static phases (deg): sun `8.3333`, planet `11.1111`, ring `0.4167`

## Current Static Pair Metrics

- Sun-planet sampled overlap count: `0`
- Sun-planet min sampled boundary gap: `0.0123 mm`
- Planet-ring sampled overlap count: `720` (not reliable for internal-ring inside/outside classification)
- Planet-ring min sampled boundary gap: `0.0105 mm`

## Notes

- This audit follows the same static body placement as the STEP assembly export.
- It is a sampled-outline screen, not a full analytic tooth-contact solver.
- It is intended to catch obvious indexing mistakes quickly before export or print.
- The expensive phase sweep was removed because it was too slow to be useful in this workflow.
- For the internal ring pair, use the sampled minimum gap and direct solid-intersection checks, not the overlap count alone.
