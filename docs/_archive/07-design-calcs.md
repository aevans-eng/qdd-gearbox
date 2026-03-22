# Design Calculators

Python-based engineering calculators in `calc/`. Each validates a design requirement.

## Overview

| Calculator | File | Purpose | Key Requirement |
|-----------|------|---------|-----------------|
| Gear Geometry | `calc/gear_geometry.py` | Involute profile generation, parametric gear math | Foundation for stress analysis |
| Tooth Stress | `calc/tooth_stress.py` | Lewis bending + Hertzian contact stress | Safety factor ≥ 2.0 |
| Bearing Life | `calc/bearing_life.py` | L10 lifetime prediction (ISO 281) | > 5000 hrs at rated load |
| Thermal Model | `calc/thermal.py` | Lumped-parameter motor+gearbox thermal | < 5 min thermal limit met |

## Running Calculators

Each script runs standalone from the command line:

```
python calc/gear_geometry.py
python calc/tooth_stress.py
python calc/bearing_life.py
python calc/thermal.py
```

Or use the dashboard to run all at once:

```
python ui/dashboard.py
```

## Dependencies

- Python 3.10+
- `sympy` — symbolic math (gear_geometry)
- `numpy` — numerical computation (all)
- `matplotlib` — plotting (dashboard, thermal)

Install: `pip install sympy numpy matplotlib`

## Calculator Details

### gear_geometry.py — Symbolic Gear Profile

Uses SymPy to derive involute tooth profiles parametrically. Given module, tooth count, and pressure angle, generates:
- Pitch diameter, base circle, addendum/dedendum circles
- Involute curve coordinates for tooth profile
- Contact ratio calculation
- Gear mesh geometry for sun, planet, and ring gears

### tooth_stress.py — Stress Analysis with Iterative Solver

Calculates gear tooth stresses using standard methods:
- **Lewis bending stress** — tooth root bending load
- **Hertzian contact stress** — tooth surface contact pressure
- **Iterative optimizer** — given a target safety factor, iterates on module and face width to find minimum acceptable geometry

### bearing_life.py — Bearing Lifetime Prediction

ISO 281 L10 basic rating life calculation:
- Input: radial/axial loads from gear force analysis, bearing catalog ratings
- Output: predicted lifetime in hours and revolutions
- Supports load spectrum analysis for variable-duty operation

### thermal.py — Thermal Model

Lumped-parameter thermal network:
- Motor winding, stator, housing, gearbox nodes
- Steady-state and transient (time-stepping) solver
- Validates continuous torque rating and 5-minute peak thermal limit
