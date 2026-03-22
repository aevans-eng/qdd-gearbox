"""Physical and design constants for QDD gearbox calculations."""

import math

# --- Physical Constants ---
PI = math.pi
GRAVITY = 9.81  # m/s^2

# --- QDD Design Parameters ---
GEAR_RATIO = 5.0
NUM_PLANETS = 3
PRESSURE_ANGLE_DEG = 20.0
PRESSURE_ANGLE_RAD = math.radians(PRESSURE_ANGLE_DEG)

# --- Motor Specs (update when confirmed) ---
MOTOR_PEAK_TORQUE_NM = 16.0 / GEAR_RATIO       # Motor-side peak (3.2 Nm)
MOTOR_CONT_TORQUE_NM = 12.0 / GEAR_RATIO       # Motor-side continuous (2.4 Nm)
MOTOR_MAX_SPEED_RPM = 600.0 * GEAR_RATIO        # Motor-side max (3000 RPM)
OUTPUT_PEAK_TORQUE_NM = 16.0
OUTPUT_CONT_TORQUE_NM = 12.0
OUTPUT_MAX_SPEED_RPM = 600.0

# --- Thermal Limits ---
WINDING_TEMP_LIMIT_C = 120.0
HOUSING_TEMP_LIMIT_C = 80.0
AMBIENT_TEMP_C = 25.0

# --- Material Defaults (PLA+) ---
PLA_PLUS_YIELD_MPA = 50.0
PLA_PLUS_UTS_MPA = 60.0
PLA_PLUS_ELASTIC_MODULUS_GPA = 3.5
PLA_PLUS_POISSON = 0.36

# --- Material Defaults (Nylon PA6) ---
NYLON_YIELD_MPA = 70.0
NYLON_UTS_MPA = 85.0
NYLON_ELASTIC_MODULUS_GPA = 2.8
NYLON_POISSON = 0.40

# --- Safety Factors ---
MIN_SAFETY_FACTOR_BENDING = 2.0
MIN_SAFETY_FACTOR_CONTACT = 1.5
