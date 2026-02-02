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

- `docs/` — all project documentation, split by topic
  - `01-requirements.md` — performance requirements and priorities
  - `02-trade-studies.md` — Pugh matrices and concept selection
  - `03-system-design.md` — system architecture, subsystems, interfaces
  - `04-detailed-design.md` — CAD strategy, assembly stack, DFM
  - `05-parts-list.md` — BOM and sourcing
  - `06-references.md` — external links and open questions
- `src/` — future firmware and control code (C, ODrive config)

## Design Context

- **Reduction type:** Planetary (selected via trade study)
- **Gear ratio:** 5:1 (selected via trade study)
- **Bearings:** Ball bearings (selected via trade study)
- **Manufacturing:** FDM 3D printing only, no CNC
- **Budget:** Under $120 CAD
- **Key QDD property:** Must be backdrivable — low backlash (≤ 0.5°) and high transparency

## Conventions

- When discussing design decisions, reference the trade studies in `docs/02-trade-studies.md`
- Keep docs updated as the design evolves
- Use engineering units (Nm, mm, RPM, degrees)
- When I ask about requirements, refer to `docs/01-requirements.md`
