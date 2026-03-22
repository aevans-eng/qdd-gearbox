# CLAUDE.md — QDD Gearbox Project

## Overview

This is a quasi-direct-drive (QDD) actuator project. We are designing a 3D-printed planetary gearbox (5:1 ratio) to interface with a BLDC motor, magnetic encoder, and ODrive controller. CAD work is done in CATIA.

## Environment (STRICT)

- Platform: Windows
- Shell: PowerShell ONLY
  - NEVER use bash/Unix syntax (no `&&`, `||`, `2>/dev/null`, `./`, `cat`, `ls`, `grep`, `rm`, etc.)
  - Use PowerShell equivalents only
  - All Bash tool calls MUST contain valid PowerShell commands

## Project Structure

- `docs/` — project documentation (see `docs/README.md` for full index)
  - `design/` — design reference: tolerances, assembly profile, gear params, fasteners, DFM
  - `catia/` — CATIA workflows: STEP integration, skeleton, modeling guide
  - `log/` — dated work log entries
  - `images/` — screenshots and diagrams
  - `original-documentation-jan4/` — original design sprint docs (requirements, trade studies, etc.)
  - `_archive/` — old numbered docs (01-09), superseded
- `prototypes/` — organized by revision
  - `rev00a/` — notes, photos, print STEP files
  - `rev00b/` — planned changes for next revision
- `testing/` — test tracker, test bench design, testing methodology
- `calc/` — Python design calculators (run with `python <script>.py`)
- `ui/` — Tkinter dashboard for calc results
- `pygeartrain/` — gear profile generation (external tool)
- `src/` — future firmware and control code (C, ODrive config)
- `drawings/` — GD&T annotation notes and tolerance schemes
- `tests/` — pytest validation for calculators

## Design Context

- **Reduction type:** Planetary (selected via trade study)
- **Gear ratio:** 5:1 (selected via trade study)
- **Bearings:** Ball bearings (selected via trade study)
- **Manufacturing:** FDM 3D printing only, no CNC
- **Budget:** Under $120 CAD
- **Key QDD property:** Must be backdrivable — low backlash (≤ 0.5°) and high transparency

## Conventions

- When discussing design decisions, reference the trade studies in `docs/original-documentation-jan4/trade-studies.md`
- Keep docs updated as the design evolves
- Use engineering units (Nm, mm, RPM, degrees)
- When I ask about requirements, refer to `docs/original-documentation-jan4/design-requirements.md`
