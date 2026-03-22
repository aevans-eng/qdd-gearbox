# Design Requirements

## What Makes a Good Actuator (for us)? Ranked by Priority

1. **Low Backlash**
   - Requirement: ≤ 0.5° of backlash
   - Hard
2. **Low Cost**
   - Requirement: Under $120 CAD
   - Hard
3. **DFM/DFA**
   - Requirement: All off-the-shelf + 3D printed parts. Assemblable without complex tools.
   - Hard
4. **Quasi-Direct Driveness**
   - Friction torque < 1 Nm (motor disconnected). Qualitative gate — R-09 (efficiency) is the quantitative measure of transmission transparency.
   - Hard
5. **High Durability**
   - Should not be able to break itself in under 1 minute. Combination of software and hardware limits.
   - Hard
6. **Peak Torque Output**
   - Should reach 16 Nm peak
   - Hard
7. **High Continuous Torque Output**
   - Should do 12 Nm continuous
   - Hard
8. **Easily Integratable with Outputs**
   - Should support either shafts or bolted plates
   - Soft
9. **High Torque Density (volume)**
   - (No specific target set)
   - Soft
10. **High Thermal Performance**
    - Should not be melting in less than 5 minutes
    - Hard
11. **High Efficiency**
    - Should be >90% efficient
    - Soft
12. **High Torque Density (weight)**
    - Should be under 2 kg
    - Soft
13. **High RPM Range**
    - Should continuously spin at 600 RPM
    - Soft

## Revision History

| Date | Item | Change | Rationale |
|------|------|--------|-----------|
| 2026-03-11 | R-04 Backdrivability | Changed from "backdriveable under human impulse" to "friction torque < 1 Nm (motor disconnected)" | Original spec was untestable — no defined threshold, no measurement method. During first prototype testing, tight gear mesh passed the vague spec but raised concerns about actual transparency. Researched industry QDD specs (e.g., CubeMars AK70-10: ~0.97 Nm friction torque at 17.5 Nm output). Adopted friction torque as the standard metric — it's what commercial QDD actuators use, it's measurable with basic tools (lever + known weight), and it gives a single-number pass/fail. Efficiency (R-09, >90%) remains the quantitative performance spec; R-04 now serves as a testable qualitative gate confirming QDD behavior. |

## How We Defined These
- What quantifiable outputs can we apply?
- Is it a hard requirement or a nice to have?

## What Makes a QDD Different
A QDD is not a regular geared motor. If the gearbox has high friction or backlash, it is not a QDD — it must be back-drivable. **Transparency** and **backlash** are the defining characteristics.
