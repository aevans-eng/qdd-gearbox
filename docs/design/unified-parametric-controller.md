# Unified Parametric Controller — Vision Doc

*Created: 2026-03-13 | Status: Concept*

## The Problem

The current workflow for making design changes spans multiple disconnected systems:

1. **CATIA skeleton** — master parameters, publications, formulas
2. **pygeartrain** (`generate_step_aaron.py`) — gear generation with hardcoded params
3. **CATIA cutting bodies** — bearing bores, bolt holes, shaft cutouts on gear STEPs
4. **Python calcs** (`calc/`) — stress, bearing life, thermal analysis
5. **Tkinter dashboard** (`ui/dashboard.py`) — visualization of calc results

Pain points:
- **Cutting bodies workflow is clunky and slow** — the STEP → import → constrain → boolean pipeline works architecturally but is painful to execute every revision
- **Parameters are scattered** — gear teeth counts in Python, clearances in CATIA, bearing sizes in both
- **No dependency validation** — nothing stops you from setting a clearance smaller than a tolerance stackup, or a shaft diameter incompatible with a bearing bore
- **Each revision requires manual sync** across all systems

## The Vision

**One Tkinter GUI that controls every design variable, validates constraints, and generates all outputs in one go.**

```
┌─────────────────────────────────────────────┐
│           Unified Parameter Controller       │
│                                             │
│  Gear:  R=48  P=18  S=12  N=3  helix=0°   │
│  Bearings: planet=686ZZ  main=6805-2RS     │
│  Shaft:  OD=___  clearance=___             │
│  Housing: wall=___  lid_gap=___            │
│  Fasteners: M3×___  M5×___                 │
│                                             │
│  [Validate]  [Generate All]  [Export]       │
│                                             │
│  ⚠ planet_bore + clearance > carrier_wall  │
│  ✓ ring_OD + housing_clearance < bore      │
└─────────────────────────────────────────────┘
         │
         ├──→ pygeartrain: gear STEPs (with cuts pre-applied)
         ├──→ CATIA design table: .xlsx for skeleton parameter import
         ├──→ calc/: updated analysis with current params
         └──→ dashboard: live results display
```

### Key Capabilities

**Parameter ownership:**
- All variables defined once, in Python
- CATIA reads them via design table import (Excel → parameter table)
- pygeartrain reads them directly
- Calcs read them directly

**Dependency validation:**
- Bearing bore must accommodate bearing OD + press fit
- Shoulder height must be > bearing width (or binding occurs — see T-005)
- Stackup through carrier assembly must leave axial clearance at lid (see T-002)
- Sun bore must match motor shaft + fit tolerance
- Ring OD + clearance must be < housing bore
- Bolt circle must clear gear OD

**Pre-cut gear STEPs:**
- Bearing pockets, shaft bores, bolt holes applied in CadQuery before STEP export
- Eliminates the CATIA cutting bodies workflow entirely for gear parts
- Cuts are parameterized from the same source as everything else
- CATIA still does housing, carrier, lid — those aren't generated from STEPs

**AI optimization (future):**
- Feed parameter ranges + constraints + objective function (minimize backlash, weight, cost)
- Solver explores valid design space
- Human reviews and selects from Pareto-optimal candidates

## What Changes from Current Architecture

| Aspect | Current | Proposed |
|--------|---------|----------|
| Gear STEPs | Pure tooth geometry | Include bearing pockets, shaft bore, bolt holes |
| Cutting bodies (gears) | Separate CATIA part, skeleton-driven booleans | Eliminated — cuts happen in CadQuery |
| Cutting bodies (carrier/housing) | CATIA | Still CATIA — these parts are natively modeled |
| Parameter source of truth | CATIA skeleton | Python controller → exports to CATIA design table |
| Skeleton role | Master reference for all params | Still master reference for positions/planes, but reads dimensions from design table |
| pygeartrain params | Hardcoded in generate_step_aaron.py | Read from controller |
| Calc params | Hardcoded per script | Read from controller |

### What Stays the Same
- Skeleton is still the geometric anchor (planes, axes, positions)
- Parts still constrain to skeleton publications, never to each other
- B-Rep free rule still applies for CATIA-native parts
- Carrier and housing are still modeled in CATIA

## Pre-Requisites / Blockers

### 1. CATIA Design Table Workflow (BLOCKER — needs learning)
Aaron needs to understand:
- How to create a design table (Excel ↔ CATIA parameter mapping)
- How to add/remove parameters from an existing design table
- How design tables interact with publications
- What happens when a parameter name changes or is deleted
- Whether design table updates can be triggered externally (macro? file watch?)

**Suggested experiment:** Pick 3-4 existing skeleton parameters (e.g., `gear_height`, `ring_wall_thickness`, `carrier_planet_clearance`). Create a small design table in Excel. Link it to the skeleton. Change values in Excel, update in CATIA, verify cascade. Then try adding a new parameter and removing one. This tests the full lifecycle without risking the whole model.

### 2. Parameter Audit
Need a complete inventory of:
- Every CATIA skeleton parameter (name, current value, what it drives)
- Every pygeartrain input variable
- Every calc input variable
- Which overlap and which are independent

### 3. CadQuery Cut Operations
Need to verify that CadQuery can reliably:
- Cut bearing pockets (cylindrical bore to specific depth with shoulder)
- Cut shaft through-holes
- Cut bolt holes at parametric positions (using planet center coords from gear geometry)
- Export the result as a clean STEP that CATIA handles well

### 4. Non-Parametric Shortcuts
`docs/design/non-parametric-shortcuts.md` may list places where the CATIA model bypasses the skeleton. These would break if an external design table tries to drive them.

## Implementation Phases

**Phase 0 — Document & learn (now)**
- Write this doc ✓
- Run the CATIA design table experiment
- Audit existing parameters

**Phase 1 — Parameter unification**
- Central Python config (dict or dataclass) with all params
- pygeartrain reads from it
- Calcs read from it
- Design table export function (Python → Excel)

**Phase 2 — Pre-cut gear STEPs**
- Add CadQuery operations for bearing pockets, shaft bore
- Validate against physical prints
- Remove CATIA cutting bodies for gears

**Phase 3 — Tkinter GUI**
- Extend existing `ui/dashboard.py` or build new controller
- Dependency validation with clear error messages
- One-button generate: gear STEPs + design table + calc results

**Phase 4 — Optimization (future)**
- Define objective functions and constraints formally
- Parameter sweep / optimization solver
- Pareto front visualization

## Risks

- **Design table fragility:** If CATIA design tables are finicky about parameter naming or ordering, the whole pipeline could be brittle. The experiment in Pre-Req 1 tests this.
- **CadQuery precision:** Cuts in CadQuery need to match CATIA's expectations for the STEP import. Tolerances, coordinate systems, and face quality matter.
- **Over-engineering too early:** Rev 00B is the priority. This tooling should be built incrementally, not as a big-bang rewrite.
