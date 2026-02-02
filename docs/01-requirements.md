# QDD Actuator — Design Requirements

## Project Goal

Create a quasi-direct-drive actuator by designing a 3D-printable gearbox to interface with a BLDC motor, magnetic encoder, and ODrive controller.

## Primary Objective

Reach "Manufacturing Readiness" — complete CAD assembly, locked BOM, and all COTS components ordered.

## Secondary Objective

Complete "Design Intent" documentation (justification for ratio, motor choice, materials).

## Scope

### In-Scope

- Mechanical design of a reduction stage (gearbox) optimized for FDM 3D printing
- Integration of a specific BLDC motor, magnetic encoder, and ODrive controller
- Interface design of the housing and output interface
- Basic modeling of the control system

### Out-of-Scope

- Custom motor winding or controller PCB design
- Complex firmware coding (basic ODrive config is assumed)
- Exotic manufacturing (no CNC aluminum; design must be printable)

## Performance Requirements (Ranked by Priority)

| # | Requirement | Metric | Hard/Soft |
|---|------------|--------|-----------|
| 1 | Low Backlash | ≤ 0.5° of backlash | Hard |
| 2 | Low Cost | Under $120 CAD | Hard |
| 3 | DFM/DFA | All off-the-shelf + 3D printed parts. No complex tools for assembly | Hard |
| 4 | Quasi-Direct Drive | Backdriveable under human impulse loading | Hard |
| 5 | High Durability | Cannot break itself in under 1 minute (SW + HW limits) | Hard |
| 6 | Peak Torque | ≥ 16 Nm peak | Hard |
| 7 | Continuous Torque | ≥ 12 Nm continuous | Hard |
| 8 | Output Integration | Supports shafts or bolted plates | Soft |
| 9 | Thermal Performance | No melting in < 5 minutes | Hard |
| 10 | Efficiency | > 90% | Soft |
| 11 | Weight | Under 2 kg | Soft |
| 12 | RPM Range | ≥ 600 RPM continuous | Soft |

## What Makes a QDD Different

A QDD is not a regular geared motor. If the gearbox has high friction or backlash, it is not a QDD — it must be backdrivable. **Transparency** and **backlash** are the defining characteristics.
