"""
Lumped-Parameter Thermal Model
==============================
Models the motor + gearbox thermal behavior with a resistor-capacitor
network. Solves steady-state (algebraic) and transient (time-stepping)
thermal problems.

Validates:
- Continuous torque rating (steady-state winding temp < 120°C)
- 5-minute peak torque thermal limit (transient)

Skills demonstrated: iterative solvers, numerical methods
"""

import math
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from calc.utils.constants import (
    WINDING_TEMP_LIMIT_C, HOUSING_TEMP_LIMIT_C, AMBIENT_TEMP_C,
    OUTPUT_CONT_TORQUE_NM, OUTPUT_PEAK_TORQUE_NM, GEAR_RATIO,
    MOTOR_MAX_SPEED_RPM,
)


# ── Thermal Network Definition ────────────────────────────────────────

# Node indices
WINDING = 0
STATOR = 1
HOUSING = 2
GEARBOX = 3
AMBIENT = 4
NUM_NODES = 5
NODE_NAMES = ["Winding", "Stator", "Housing", "Gearbox", "Ambient"]

# Thermal capacitances (J/K) — estimated for small BLDC motor + 3D-printed gearbox
# These should be refined with actual motor data
CAPACITANCES = np.array([
    15.0,    # Winding (copper, small mass)
    80.0,    # Stator (steel laminations)
    120.0,   # Housing (aluminum or 3D-printed shell)
    60.0,    # Gearbox (3D-printed gears + bearings)
    1e10,    # Ambient (infinite heat sink)
])

# Thermal resistances (K/W) between nodes
# Format: (node_a, node_b, resistance)
RESISTANCES = [
    (WINDING, STATOR, 1.5),     # Winding to stator (slot insulation)
    (STATOR, HOUSING, 0.8),     # Stator to housing (press-fit interface)
    (HOUSING, AMBIENT, 3.0),    # Housing to ambient (natural convection)
    (HOUSING, GEARBOX, 2.0),    # Housing to gearbox (mechanical interface)
    (GEARBOX, AMBIENT, 5.0),    # Gearbox to ambient (natural convection, plastic)
]


def build_conductance_matrix():
    """Build the thermal conductance matrix G (W/K) from resistances."""
    G = np.zeros((NUM_NODES, NUM_NODES))
    for na, nb, R in RESISTANCES:
        conductance = 1.0 / R
        G[na, nb] += conductance
        G[nb, na] += conductance
        G[na, na] -= conductance
        G[nb, nb] -= conductance
    return G


# ── Heat Generation ───────────────────────────────────────────────────

def motor_losses(output_torque_nm, speed_rpm, efficiency=0.85):
    """
    Estimate motor heat generation.

    Total loss = P_mech / efficiency - P_mech
    Split: ~70% copper (winding), ~25% iron (stator), ~5% mechanical (gearbox)
    """
    motor_torque = output_torque_nm / GEAR_RATIO
    motor_speed = speed_rpm * GEAR_RATIO
    omega = motor_speed * 2.0 * math.pi / 60.0

    p_mech = motor_torque * omega  # Mechanical output (W)
    p_elec = p_mech / efficiency   # Electrical input (W)
    p_loss = p_elec - p_mech       # Total losses (W)

    return {
        "winding_w": p_loss * 0.70,    # Copper losses (I²R)
        "stator_w": p_loss * 0.25,     # Iron losses (hysteresis + eddy)
        "gearbox_w": p_loss * 0.05,    # Bearing friction, gear mesh
        "total_loss_w": p_loss,
        "p_mech_w": p_mech,
        "p_elec_w": p_elec,
        "efficiency": efficiency,
    }


def heat_generation_vector(losses):
    """Build heat source vector Q (W) for each node."""
    Q = np.zeros(NUM_NODES)
    Q[WINDING] = losses["winding_w"]
    Q[STATOR] = losses["stator_w"]
    Q[GEARBOX] = losses["gearbox_w"]
    # Ambient node: no heat generation
    return Q


# ── Steady-State Solver ──────────────────────────────────────────────

def solve_steady_state(Q):
    """
    Solve steady-state temperatures: G * T = -Q (with ambient fixed).

    We fix T_ambient = AMBIENT_TEMP_C and solve for the remaining nodes.
    Rearranging: G_reduced * T_reduced = -Q_reduced + G_ambient_col * T_ambient
    """
    G = build_conductance_matrix()

    # Remove ambient node (last row/col) and solve reduced system
    idx = list(range(NUM_NODES - 1))  # All nodes except ambient

    G_red = G[np.ix_(idx, idx)]
    Q_red = Q[idx]

    # Add contribution from ambient connections
    rhs = -Q_red.copy()
    for i in idx:
        rhs[i] += G[i, AMBIENT] * AMBIENT_TEMP_C

    # Solve G_red * T_red = rhs
    # Note: G diagonal is negative (convention), so we solve -G_red * T = Q - ...
    T_red = np.linalg.solve(-G_red, Q_red + np.array([G[i, AMBIENT] * AMBIENT_TEMP_C for i in idx]))

    T = np.zeros(NUM_NODES)
    T[AMBIENT] = AMBIENT_TEMP_C
    for k, i in enumerate(idx):
        T[i] = T_red[k]

    return T


# ── Transient Solver (Forward Euler) ─────────────────────────────────

def solve_transient(Q, duration_s, dt=1.0, T_initial=None):
    """
    Solve transient thermal response using implicit (backward) Euler.

    C * dT/dt = Q + G * T   (G has negative diagonal, positive off-diagonal)

    Implicit Euler: C * (T^{n+1} - T^n) / dt = Q + G * T^{n+1}
    => (C/dt - G) * T^{n+1} = C/dt * T^n + Q

    This is unconditionally stable regardless of time step size.
    Returns time array and temperature history for each node.
    """
    G = build_conductance_matrix()
    C_diag = np.diag(CAPACITANCES.copy())

    num_steps = int(duration_s / dt) + 1
    time = np.linspace(0, duration_s, num_steps)

    T_history = np.zeros((num_steps, NUM_NODES))

    if T_initial is not None:
        T_history[0] = T_initial
    else:
        T_history[0] = AMBIENT_TEMP_C

    T_history[0, AMBIENT] = AMBIENT_TEMP_C

    # Work with reduced system (exclude ambient node)
    idx = list(range(NUM_NODES - 1))
    G_red = G[np.ix_(idx, idx)]
    C_red = C_diag[np.ix_(idx, idx)]
    Q_red = Q[idx].copy()

    # Add ambient coupling contribution to RHS
    # G[i, AMBIENT] * T_ambient contributes to the heat flow into node i
    ambient_coupling = np.array([G[i, AMBIENT] * AMBIENT_TEMP_C for i in idx])

    # LHS matrix: (C/dt - G) — note G diagonal is negative, so -G diagonal is positive
    A = C_red / dt - G_red

    for step in range(1, num_steps):
        T_prev = T_history[step - 1, idx]

        # RHS: C/dt * T_prev + Q + ambient_coupling
        rhs = C_red @ T_prev / dt + Q_red + ambient_coupling

        T_new_red = np.linalg.solve(A, rhs)

        T_history[step, idx] = T_new_red
        T_history[step, AMBIENT] = AMBIENT_TEMP_C

    return time, T_history


# ── Analysis ──────────────────────────────────────────────────────────

def print_thermal_analysis():
    """Run and print full thermal analysis."""
    print("=" * 60)
    print("  QDD Gearbox — Thermal Analysis")
    print("=" * 60)
    print()

    # --- Steady-state at continuous torque ---
    print("--- Steady-State: Continuous Torque ---\n")
    losses_cont = motor_losses(OUTPUT_CONT_TORQUE_NM, MOTOR_MAX_SPEED_RPM / GEAR_RATIO)
    print(f"  Operating point: {OUTPUT_CONT_TORQUE_NM} Nm @ {MOTOR_MAX_SPEED_RPM / GEAR_RATIO:.0f} RPM output")
    print(f"  Mechanical power:  {losses_cont['p_mech_w']:.1f} W")
    print(f"  Electrical power:  {losses_cont['p_elec_w']:.1f} W")
    print(f"  Total losses:      {losses_cont['total_loss_w']:.1f} W")
    print(f"    Winding (Cu):    {losses_cont['winding_w']:.1f} W")
    print(f"    Stator (Fe):     {losses_cont['stator_w']:.1f} W")
    print(f"    Gearbox:         {losses_cont['gearbox_w']:.1f} W")
    print()

    Q_cont = heat_generation_vector(losses_cont)
    T_ss = solve_steady_state(Q_cont)

    print(f"  Steady-State Temperatures:")
    for i in range(NUM_NODES):
        limit = ""
        status = ""
        if i == WINDING:
            limit = f"  (limit: {WINDING_TEMP_LIMIT_C}°C)"
            status = " PASS" if T_ss[i] < WINDING_TEMP_LIMIT_C else " FAIL"
        elif i == HOUSING:
            limit = f"  (limit: {HOUSING_TEMP_LIMIT_C}°C)"
            status = " PASS" if T_ss[i] < HOUSING_TEMP_LIMIT_C else " FAIL"
        print(f"    {NODE_NAMES[i]:>10s}: {T_ss[i]:6.1f} °C{limit}{status}")
    print()

    # --- Transient at peak torque (5 minutes) ---
    print("--- Transient: Peak Torque for 5 Minutes ---\n")
    losses_peak = motor_losses(OUTPUT_PEAK_TORQUE_NM, MOTOR_MAX_SPEED_RPM / GEAR_RATIO)
    print(f"  Operating point: {OUTPUT_PEAK_TORQUE_NM} Nm @ {MOTOR_MAX_SPEED_RPM / GEAR_RATIO:.0f} RPM output")
    print(f"  Total losses: {losses_peak['total_loss_w']:.1f} W")
    print()

    Q_peak = heat_generation_vector(losses_peak)
    duration = 300.0  # 5 minutes in seconds
    time, T_hist = solve_transient(Q_peak, duration, dt=1.0)

    # Report temperatures at key times
    print(f"  {'Time':>8s}  {'Winding':>8s}  {'Stator':>8s}  {'Housing':>8s}  {'Gearbox':>8s}")
    print(f"  {'(s)':>8s}  {'(°C)':>8s}  {'(°C)':>8s}  {'(°C)':>8s}  {'(°C)':>8s}")
    print("  " + "-" * 45)

    report_times = [0, 30, 60, 120, 180, 240, 300]
    for t in report_times:
        idx = min(int(t), len(time) - 1)
        print(f"  {time[idx]:>8.0f}  {T_hist[idx, WINDING]:>8.1f}  "
              f"{T_hist[idx, STATOR]:>8.1f}  {T_hist[idx, HOUSING]:>8.1f}  "
              f"{T_hist[idx, GEARBOX]:>8.1f}")

    print()
    T_final = T_hist[-1]
    winding_ok = T_final[WINDING] < WINDING_TEMP_LIMIT_C
    housing_ok = T_final[HOUSING] < HOUSING_TEMP_LIMIT_C
    print(f"  After 5 minutes at peak torque:")
    print(f"    Winding: {T_final[WINDING]:.1f}°C — {'PASS' if winding_ok else 'FAIL'} (limit {WINDING_TEMP_LIMIT_C}°C)")
    print(f"    Housing: {T_final[HOUSING]:.1f}°C — {'PASS' if housing_ok else 'FAIL'} (limit {HOUSING_TEMP_LIMIT_C}°C)")
    print()

    return time, T_hist


def main():
    time, T_hist = print_thermal_analysis()

    # Summary
    print("--- Thermal Network Parameters ---\n")
    print("  Capacitances (J/K):")
    for i in range(NUM_NODES - 1):
        print(f"    {NODE_NAMES[i]:>10s}: {CAPACITANCES[i]:.1f}")
    print()
    print("  Resistances (K/W):")
    for na, nb, R in RESISTANCES:
        print(f"    {NODE_NAMES[na]:>10s} <-> {NODE_NAMES[nb]:<10s}: {R:.1f}")
    print()
    print("  Note: Thermal parameters are estimates. Refine with actual motor data")
    print("  and measured temperatures from prototype testing.")


if __name__ == "__main__":
    main()
