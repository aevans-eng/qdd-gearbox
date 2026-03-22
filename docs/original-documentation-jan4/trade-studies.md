# Trade Studies

## Evaluation Criteria

| Metric | Weight | What does it mean |
|--------|--------|-------------------|
| **Cost** | 5 | Price in money |
| **Transparency** | 4 | Can the motor feel the reflected response of the output system |
| **Torque Density** | 3 | How does this help our volumetric and weight based torque density |
| **Precision** | 4 | How does this contribute to the backlash of our system |
| **DFM/DFA** | 4 | Can this be easily made/assembled |
| **Efficiency** | 3 | How efficient is this choice |
| **Durability** | 4 | How safe is this against our loading |

Scoring: 5 = good, 1 = bad

---

## Reduction Method

| Metric | Weight | Planetary | Cycloidal | Drive Belt | Capstan | Strain Wave | Sequential Horizontal |
|--------|--------|-----------|-----------|------------|---------|-------------|----------------------|
| **Cheapness** | 0.2 | 5 | 3 | 3.5 | 4 | 3.5 | 4.5 |
| **Transparency** | 0.15 | 4 | 3.5 | 5 | 4 | 3 | 4 |
| **Torque Density** | 0.1 | 4 | 4 | 3 | 3 | 5 | 2 |
| **Precision** | 0.15 | 4 | 5 | 3.5 | 3 | 5 | 4 |
| **DFM/DFA** | 0.15 | 4 | 3 | 4 | 3 | 3 | 4 |
| **Efficiency** | 0.1 | 4.5 | 4 | 5 | 4.5 | 3.5 | 4 |
| **Durability** | 0.15 | 5 | 4 | 4 | 4 | 3 | 5 |
| **Weighted Score** | | **4.4** | 3.725 | 3.975 | 3.65 | 3.65 | 4.05 |

**Winner: Planetary**

---

## Gear Ratio

| Metric | Weight | 4:1 | 5:1 | 6:1 | 7:1 |
|--------|--------|-----|-----|-----|-----|
| **Cheapness** | 0.1 | 5 | 5 | 5 | 5 |
| **Transparency** | 0.15 | 5 | 4.5 | 4 | 3.5 |
| **Torque Density** | 0.2 | 4 | 4.5 | 4.5 | 5 |
| **Precision** | 0.15 | 5 | 5 | 5 | 5 |
| **DFM/DFA** | 0.1 | 5 | 5 | 5 | 5 |
| **Efficiency** | 0.1 | 5 | 5 | 4.5 | 4.5 |
| **Durability** | 0.2 | 5 | 5 | 4.5 | 4 |
| **Weighted Score** | | 4.8 | **4.825** | 4.6 | 4.525 |

**Winner: 5:1**

---

## Bearing Type

| Metric | Weight | Ball Bearing | Roller Bearing | Needle Bearing | Taper Bearing | Bushing | Crossed Roller |
|--------|--------|-------------|----------------|----------------|---------------|---------|----------------|
| **Cheapness** | 0.6 | 5 | 3 | 4 | 2 | 5 | 1 |
| **Radial Loading** | 0.2 | 4 | 5 | 5 | 4 | 2 | 5 |
| **Axial Load** | 0.05 | 2 | 1 | 1 | 5 | 2 | 5 |
| **Moment Loading** | 0.15 | 1 | 1 | 1 | 3 | 1 | 5 |
| **Weighted Score** | | **4.05** | 3 | 3.6 | 2.7 | 3.65 | 2.6 |

**Winner: Ball Bearing**

---

## Design Choices Still Open (at time of sprint)

- What type of teeth? (Cycloidal vs Involute)
- Material choice (3D printing filament types)
- Friction reduction / lubricants
- Fixturing methods (screws/pins/inserts)
- Bearing arrangement / placement
- Input coupling method (press fit, screw collar, keyed shaft)
- Output coupling (size, fastening, supported vs unsupported)
