# QDD Actuator — System Design

## System Block Diagram

Power Supply → ODrive ESC → BLDC Motor → Input Coupling → Gear Reduction → Output Coupling → Load
                  ↑
               Encoder (feedback to ESC)
               Brain (commands to ESC)

## Subsystem Definitions

### Power Supply
- **Input:** Wall power
- **Purpose:** Provide electrical power to ESC
- **Output:** Conditioned DC power to ESC

### Brain
- **Purpose:** Tells the ESC what to do
- **Input:** User commands
- **Output:** Signal to ESC

### ODrive ESC
- **Purpose:** Control motor
- **Input:** Conditioned DC power, signal from brain
- **Output:** Motor winding current

### BLDC Motor
- **Purpose:** Torque to coupling
- **Input:** Current from ESC
- **Output:** Torque

### Encoder
- **Purpose:** Sensing for control system
- **Input:** Coupled to motor
- **Output:** Signal to ESC

### Input Coupling
- **Purpose:** Couples motor to gearbox
- **Input:** Motor shaft
- **Output:** Gearbox input
- **Options considered:** Press fit, screw collar, keyed shaft

### Gear Reduction
- **Purpose:** Increase torque
- **Input:** Coupling
- **Output:** Output coupling

### Output Coupling
- **Purpose:** Control output arm
- **Input:** Gearbox output
- **Output:** Control arm
- **Considerations:** Size, fastening methods, supported vs unsupported bearing interaction

## Critical Interfaces

1. **Thermal Interface:** Motor to mount
2. **Mechanical Interface:** Output shaft to load
3. **Data Interface:** Magnet position relative to encoder chip

## Control Strategy

Confirm ODrive control mode (Position vs. Velocity vs. Torque) matches the mechanical design. Verify encoder resolution is sufficient for the gear reduction.

## Key Design Lesson

> The #1 failure mode in student robotics projects is not the gearbox itself, but how the gearbox attaches to the motor or how the magnet attaches to the shaft. — Interface definition is critical.
