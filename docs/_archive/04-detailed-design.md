# QDD Actuator — Detailed Design & CAD

## 3D Modeling Strategy

- Master assembly designed to be modular with different gearing layouts, minimizing iteration time
- Sun, planet, and ring gears are interlinked but should be independent systems
- Carrier designed to be parametric with the gear systems — always compatible
- Ring gear modular from gearbox housing — easily swappable for prototyping
- Housing may need two parts: ring gear installs into housing, carrier sits under planets
- Sun, planet, and ring to be printed together

## Assembly Stack (Bottom → Top)

1. Bottom housing face
2. Housing bottom carrier bearing
3. Bottom carrier plate
4. Sun gear on shaft, planet gears aligning with bottom carrier plate and pins, ring gear slides into housing
   - Planet gears
5. Top carrier plate
6. Ring gear locking feature
7. Lid top carrier bearing
8. Lid

## Parts to Design

- Housing that bolts to motor
- Sun gear that interfaces with motor output
- Planet gears
- Ring gear with output connection
- Lid

## Design for Manufacturing (DFM)

- Apply printing tolerances (offsets)
- Design orientation features (avoid supports on gear faces)
- Virtual assembly in CAD to catch interference

## Design Calculators Needed

- Bearing placement calculator
- Bearing lifetime calculator
- Involute teeth stress calculator
- Cycloidal teeth stress calculator
- Shear on pins/screws calculator

## CAD Creation Pipeline (Parallel Tasks)

1. Get gear teeth generator working
2. Make arbitrary gearset to try out different input and output strategies

## Design Decision: 5:1 Ratio Maintained

Decision was made to maintain 5:1 gear ratio based on trade study results (see 02-trade-studies.md).
