# QDD Actuator — Trade Studies & Concept Selection

## Scoring Criteria

| Metric | Weight | Meaning |
|--------|--------|---------|
| Cost | 5 | Price in money |
| Transparency | 4 | Can the motor feel the reflected response of the output system |
| Torque Density | 3 | Volumetric and weight-based torque density |
| Precision | 4 | Contribution to system backlash |
| DFM/DFA | 4 | Ease of manufacturing and assembly |
| Efficiency | 3 | Mechanical efficiency |
| Durability | 4 | Safety against expected loading |

Scoring: 5 = good, 1 = bad

## Reduction Method Selection

| Metric | Weight | Planetary | Cycloidal | Drive Belt | Capstan | Strain Wave | Sequential Horizontal |
|--------|--------|-----------|-----------|------------|---------|-------------|----------------------|
| Cheapness | 0.2 | 5 | 3 | 3.5 | 4 | 3.5 | 4.5 |
| Transparency | 0.15 | 4 | 3.5 | 5 | 4 | 3 | 4 |
| Torque Density | 0.1 | 4 | 4 | 3 | 3 | 5 | 2 |
| Precision | 0.15 | 4 | 5 | 3.5 | 3 | 5 | 4 |
| DFM/DFA | 0.15 | 4 | 3 | 4 | 3 | 3 | 4 |
| Efficiency | 0.1 | 4.5 | 4 | 5 | 4.5 | 3.5 | 4 |
| Durability | 0.15 | 5 | 4 | 4 | 4 | 3 | 5 |
| **Weighted Score** | | **4.4** | 3.725 | 3.975 | 3.65 | 3.65 | 4.05 |

**Winner: Planetary**

## Gear Ratio Selection

| Metric | Weight | 4:1 | 5:1 | 6:1 | 7:1 |
|--------|--------|-----|-----|-----|-----|
| Cheapness | 0.1 | 5 | 5 | 5 | 5 |
| Transparency | 0.15 | 5 | 4.5 | 4 | 3.5 |
| Torque Density | 0.2 | 4 | 4.5 | 4.5 | 5 |
| Precision | 0.15 | 5 | 5 | 5 | 5 |
| DFM/DFA | 0.1 | 5 | 5 | 5 | 5 |
| Efficiency | 0.1 | 5 | 5 | 4.5 | 4.5 |
| Durability | 0.2 | 5 | 5 | 4.5 | 4 |
| **Weighted Score** | | 4.8 | **4.825** | 4.6 | 4.525 |

**Winner: 5:1**

## Bearing Selection

| Metric | Weight | Ball Bearing | Roller | Needle | Taper | Bushing | Crossed Roller |
|--------|--------|-------------|--------|--------|-------|---------|----------------|
| Cheapness | 0.6 | 5 | 3 | 4 | 2 | 5 | 1 |
| Radial Loading | 0.2 | 4 | 5 | 5 | 4 | 2 | 5 |
| Axial Load | 0.05 | 2 | 1 | 1 | 5 | 2 | 5 |
| Moment Loading | 0.15 | 1 | 1 | 1 | 3 | 1 | 5 |
| **Weighted Score** | | **4.05** | 3.0 | 3.6 | 2.7 | 3.65 | 2.6 |

**Winner: Ball Bearing**

## Design Decisions Summary

- **Reduction:** Planetary gearbox
- **Ratio:** 5:1
- **Bearings:** Ball bearings
- **Gear teeth:** Decision pending between cycloidal-style and involute
- **Material:** 3D printed (FDM), filament type TBD
- **Lubrication:** TBD
