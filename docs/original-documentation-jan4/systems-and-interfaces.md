# Systems & Interfaces

## System Breakdown

- **Power Supply**
  - Input: Wall power
  - Purpose: Provide electrical power to ESC
  - Output: Conditioned DC power to ESC
- **Brain**
  - Purpose: Tells the ESC what to do
  - Input: Our commands
  - Output: Signal to ESC
- **ODrive ESC**
  - Purpose: Control motor
  - Input: Conditioned DC power, signal from brain
  - Output: Motor winding current
- **BLDC Motor**
  - Purpose: Torque to coupling
  - Input: Current from ESC
  - Output: Torque
- **Encoder**
  - Purpose: Sensing of control system
  - Input: Coupled to motor
  - Output: Signal to ESC
- **Input Coupling**
  - Purpose: Couples motor to gearbox
  - Input: Motor shaft
  - Output: Gearbox
- **Gear Reduction**
  - Purpose: Increase torque
  - Input: Coupling
  - Output: Output coupling
- **Output Coupling**
  - Purpose: Control output arm
  - Input: Gearbox
  - Output: Control arm

## Interface Definitions
- **Thermal Interface:** Motor to mount
- **Mechanical Interface:** Output shaft to load
- **Data Interface:** Magnet position relative to encoder chip

## Control Strategy
Confirm the ODrive control mode (Position vs. Velocity vs. Torque control) matches the mechanical design — does the encoder have enough resolution for the gear reduction?

## Component Sourcing
Verify availability of critical hardware (bearings, fasteners) *before* concept selection.
