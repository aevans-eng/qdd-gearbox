# Test & Verification Plan

How each requirement from `01-requirements.md` will be verified.

## Test Matrix

| # | Requirement | Target | Test Method | Pass Criteria |
|---|------------|--------|-------------|---------------|
| 1 | Backlash | ≤ 0.5° | Dial indicator on output, lock input | Measured backlash < 0.5° |
| 2 | Budget | < $120 CAD | Sum BOM costs | Total < $120 |
| 3 | Backdrivability | Qualitative | Hand-rotate output shaft, measure input response | Smooth, low-effort backdriving |
| 4 | Peak torque | 16 Nm | Torque wrench on output, stall motor at rated current | Output holds ≥ 16 Nm without tooth failure |
| 5 | Continuous torque | 12 Nm | Run at 12 Nm continuous, monitor thermal | Sustained without overtemp |
| 6 | Speed | 600+ RPM output | Tachometer / encoder readout at no-load | ≥ 600 RPM continuous |
| 7 | Thermal limit | 5 min safe | Thermocouple on motor + housing, run at peak torque | Temp < 120°C winding, < 80°C housing after 5 min |
| 8 | Gear ratio | 5:1 | Count teeth, verify with encoder input/output ratio | Measured ratio = 5.00 ± 0.01 |
| 9 | Fit & assembly | Parts fit | Assemble by hand, check all interfaces | All bearings seat, gears mesh, housing closes |
| 10 | Print quality | Functional gears | Visual inspection, runout measurement | No delamination, teeth intact, runout < 0.1 mm |

## Test Procedures

### T1: Backlash Measurement
1. Mount gearbox on test fixture, clamp input shaft
2. Attach dial indicator to output shaft at known radius
3. Rock output shaft CW/CCW until resistance
4. Record angular displacement — this is backlash
5. Repeat 3× at different output positions, average

### T2: Backdrivability
1. Hold input shaft stationary (no motor power)
2. Apply torque to output by hand
3. Qualitative: rate effort as low/medium/high
4. Quantitative (optional): use torque wrench, record breakaway torque

### T3: Torque Test
1. Power ODrive, set current limit to rated peak
2. Attach torque wrench to output coupler
3. Command motor to hold position (stall)
4. Slowly increase resistance on output until slip or failure
5. Record max torque held

### T4: Thermal Test
1. Attach thermocouples: motor winding (if accessible), motor case, housing exterior
2. Run at continuous torque (12 Nm) for 30 minutes
3. Log temperature every 30 seconds
4. Run at peak torque (16 Nm) for 5 minutes
5. Record max temperatures, compare to limits

### T5: Speed Test
1. Run motor at max speed command, no load on output
2. Read output RPM from encoder (input RPM / 5)
3. Verify ≥ 600 RPM sustained

### T6: Gear Ratio Verification
1. Mark input and output shafts
2. Rotate input exactly 5 turns (encoder count)
3. Verify output completes exactly 1 turn
4. Or: compare encoder input/output counts over 100 revolutions

## Calculator Validation

Each Python calculator is validated against known results:

| Calculator | Validation Method |
|-----------|-------------------|
| gear_geometry.py | Compare output to textbook gear tables (Shigley's) |
| tooth_stress.py | Cross-check with Shigley's worked examples |
| bearing_life.py | Compare to SKF bearing calculator online tool |
| thermal.py | Compare steady-state to simple hand calc (P = ΔT/R_total) |

## Test Equipment Needed

- Dial indicator (0.01 mm resolution)
- Torque wrench (0–20 Nm range)
- K-type thermocouples + data logger (or multimeter with thermocouple input)
- Tachometer or encoder readout via ODrive
- Calipers (for dimensional checks)
