"""
Validation tests for QDD gearbox design calculators.
Run with: python -m pytest tests/ -v
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calc.gear_geometry import (
    design_planetary_set, compute_contact_ratio, tooth_profile, involute_profile,
)
from calc.tooth_stress import (
    lewis_form_factor, lewis_bending_stress, hertzian_contact_stress,
    analyze_stresses, tangential_force_on_sun, find_minimum_geometry,
)
from calc.bearing_life import (
    basic_life_revolutions, life_hours, equivalent_dynamic_load, spectrum_life,
    gear_forces_to_bearing_loads,
)
from calc.thermal import (
    build_conductance_matrix, motor_losses, heat_generation_vector,
    solve_steady_state, solve_transient, NUM_NODES, WINDING, AMBIENT,
)
from calc.utils.data import (
    GearParams, PlanetarySet, BearingData, LoadCase,
    PLA_PLUS, NYLON_PA6, BEARING_6805,
)
from calc.utils.units import mm_to_m, m_to_mm, rpm_to_rad_s, deg_to_rad


# ═══════════════════════════════════════════════════════════════════════
# Gear Geometry Tests
# ═══════════════════════════════════════════════════════════════════════

class TestGearGeometry:
    def test_planetary_ratio(self):
        """Gear ratio must equal 1 + Z_ring/Z_sun = 5.0."""
        gs = design_planetary_set(1.5, 12)
        assert abs(gs.ratio - 5.0) < 0.01

    def test_ring_sun_planet_relation(self):
        """Z_ring = Z_sun + 2*Z_planet."""
        gs = design_planetary_set(1.5, 12)
        assert gs.ring_teeth == gs.sun.num_teeth + 2 * gs.planet.num_teeth

    def test_assembly_condition(self):
        """(Z_sun + Z_ring) must be divisible by num_planets."""
        gs = design_planetary_set(1.5, 12, num_planets=3)
        assert (gs.sun.num_teeth + gs.ring_teeth) % gs.num_planets == 0

    def test_pitch_diameter(self):
        """d = m * z."""
        g = GearParams(2.0, 20)
        assert abs(g.pitch_diameter_mm - 40.0) < 0.001

    def test_contact_ratio_above_one(self):
        """Contact ratio for standard gears should be > 1.0."""
        cr = compute_contact_ratio(1.5, 12, 18)
        assert cr > 1.0

    def test_contact_ratio_known_value(self):
        """Check contact ratio against textbook range (1.2-2.0 typical)."""
        cr = compute_contact_ratio(1.0, 20, 30, 20.0)
        assert 1.2 < cr < 2.0

    def test_tooth_profile_output(self):
        """tooth_profile should return arrays of reasonable length."""
        g = GearParams(1.5, 12)
        x, y = tooth_profile(g, num_points=80)
        assert len(x) > 10
        assert len(y) == len(x)

    def test_involute_starts_at_base_circle(self):
        """Involute curve at t=0 should be on the base circle."""
        rb = 10.0
        x, y = involute_profile(rb, num_points=50)
        r0 = math.sqrt(x[0]**2 + y[0]**2)
        assert abs(r0 - rb) < 0.01

    def test_gear_diameters_order(self):
        """root < pitch < outer diameter."""
        g = GearParams(1.5, 20)
        assert g.root_diameter_mm < g.pitch_diameter_mm < g.outer_diameter_mm


# ═══════════════════════════════════════════════════════════════════════
# Tooth Stress Tests
# ═══════════════════════════════════════════════════════════════════════

class TestToothStress:
    def test_lewis_form_factor_positive(self):
        """Form factor should be positive for reasonable tooth counts."""
        for z in [10, 15, 20, 30, 50]:
            y = lewis_form_factor(z)
            assert y > 0

    def test_lewis_form_factor_increases_with_teeth(self):
        """More teeth -> higher form factor (stronger tooth)."""
        y10 = lewis_form_factor(10)
        y30 = lewis_form_factor(30)
        assert y30 > y10

    def test_bending_stress_positive(self):
        """Bending stress must be positive for positive force."""
        sigma = lewis_bending_stress(100.0, 1.5, 10.0, 12)
        assert sigma > 0

    def test_bending_stress_scales_with_force(self):
        """Doubling force should double stress."""
        s1 = lewis_bending_stress(100.0, 1.5, 10.0, 12)
        s2 = lewis_bending_stress(200.0, 1.5, 10.0, 12)
        assert abs(s2 / s1 - 2.0) < 0.01

    def test_hertzian_stress_positive(self):
        """Contact stress must be positive."""
        g1 = GearParams(1.5, 12, face_width_mm=10)
        g2 = GearParams(1.5, 18, face_width_mm=10)
        sigma = hertzian_contact_stress(100.0, g1, g2, PLA_PLUS)
        assert sigma > 0

    def test_tangential_force_positive(self):
        """Force on sun must be positive for positive output torque."""
        gs = design_planetary_set(1.5, 12)
        ft = tangential_force_on_sun(16.0, gs)
        assert ft > 0

    def test_safety_factor_calculation(self):
        """Safety factors should be ratio of yield to stress."""
        gs = design_planetary_set(1.5, 12, face_width_mm=10.0)
        res = analyze_stresses(gs, PLA_PLUS, 16.0)
        expected_sf = PLA_PLUS.yield_strength_mpa / res["bending_stress_sun_mpa"]
        assert abs(res["sf_bending_sun"] - expected_sf) < 0.01

    def test_iterative_solver_finds_solutions(self):
        """Solver should find at least one valid config for Nylon."""
        configs = find_minimum_geometry(NYLON_PA6)
        assert len(configs) > 0

    def test_iterative_solver_meets_targets(self):
        """All returned configs should meet safety factor targets."""
        configs = find_minimum_geometry(NYLON_PA6)
        for cfg in configs:
            assert cfg["sf_bending_sun"] >= 2.0
            assert cfg["sf_bending_planet"] >= 2.0
            assert cfg["sf_contact"] >= 1.5


# ═══════════════════════════════════════════════════════════════════════
# Bearing Life Tests
# ═══════════════════════════════════════════════════════════════════════

class TestBearingLife:
    def test_basic_life_positive(self):
        """L10 life should be positive for load < rating."""
        l10 = basic_life_revolutions(BEARING_6805, 1.0)
        assert l10 > 0

    def test_basic_life_infinite_at_zero_load(self):
        """Zero load -> infinite life."""
        l10 = basic_life_revolutions(BEARING_6805, 0.0)
        assert l10 == float('inf')

    def test_basic_life_cube_law(self):
        """Ball bearing: halving load should give 8x life."""
        l10_full = basic_life_revolutions(BEARING_6805, 2.0)
        l10_half = basic_life_revolutions(BEARING_6805, 1.0)
        assert abs(l10_half / l10_full - 8.0) < 0.01

    def test_life_hours_conversion(self):
        """Check hours conversion math."""
        hrs = life_hours(1.0, 1000.0)  # 1M rev at 1000 RPM
        expected = 1e6 / (1000.0 * 60.0)  # 16.67 hours
        assert abs(hrs - expected) < 0.01

    def test_equivalent_load_pure_radial(self):
        """Pure radial: P = Fr for deep groove."""
        b = BearingData("test", 10, 20, 5, 5.0, 3.0)
        p = equivalent_dynamic_load(1.0, 0.0, b)
        assert abs(p - 1.0) < 0.001

    def test_gear_forces_positive(self):
        """All bearing forces should be positive."""
        gs = design_planetary_set(1.5, 12)
        forces = gear_forces_to_bearing_loads(gs, 12.0)
        for loc, f in forces.items():
            assert f > 0


# ═══════════════════════════════════════════════════════════════════════
# Thermal Model Tests
# ═══════════════════════════════════════════════════════════════════════

class TestThermal:
    def test_conductance_matrix_symmetric(self):
        """G matrix should be symmetric."""
        G = build_conductance_matrix()
        assert (abs(G - G.T) < 1e-10).all()

    def test_conductance_matrix_row_sum_zero(self):
        """Each row of G should sum to approximately zero."""
        import numpy as np
        G = build_conductance_matrix()
        row_sums = G.sum(axis=1)
        assert (abs(row_sums) < 1e-10).all()

    def test_motor_losses_positive(self):
        """Losses should be positive for positive torque/speed."""
        losses = motor_losses(12.0, 600.0)
        assert losses["total_loss_w"] > 0
        assert losses["winding_w"] > 0

    def test_motor_losses_efficiency(self):
        """P_mech + P_loss = P_elec."""
        losses = motor_losses(12.0, 600.0)
        assert abs(losses["p_mech_w"] + losses["total_loss_w"] - losses["p_elec_w"]) < 0.01

    def test_steady_state_above_ambient(self):
        """All internal nodes should be above ambient with heat input."""
        losses = motor_losses(12.0, 600.0)
        Q = heat_generation_vector(losses)
        T = solve_steady_state(Q)
        for i in range(NUM_NODES - 1):
            assert T[i] > T[AMBIENT]

    def test_steady_state_ambient_unchanged(self):
        """Ambient temperature should remain at 25C."""
        losses = motor_losses(12.0, 600.0)
        Q = heat_generation_vector(losses)
        T = solve_steady_state(Q)
        assert abs(T[AMBIENT] - 25.0) < 0.001

    def test_transient_starts_at_ambient(self):
        """Transient should start at ambient temperature."""
        import numpy as np
        losses = motor_losses(12.0, 600.0)
        Q = heat_generation_vector(losses)
        time, T_hist = solve_transient(Q, 10.0, dt=1.0)
        for i in range(NUM_NODES):
            assert abs(T_hist[0, i] - 25.0) < 0.001

    def test_transient_monotonic_increase(self):
        """Temperature should monotonically increase with constant heat input."""
        import numpy as np
        losses = motor_losses(12.0, 600.0)
        Q = heat_generation_vector(losses)
        time, T_hist = solve_transient(Q, 60.0, dt=1.0)
        # Check winding temperature is non-decreasing
        diffs = np.diff(T_hist[:, WINDING])
        assert (diffs >= -0.01).all()  # Allow tiny numerical noise

    def test_transient_no_divergence(self):
        """Transient solution should not diverge (implicit solver stability)."""
        import numpy as np
        losses = motor_losses(16.0, 600.0)
        Q = heat_generation_vector(losses)
        time, T_hist = solve_transient(Q, 300.0, dt=1.0)
        # No temperature should exceed 10000C (reasonable sanity check)
        assert T_hist.max() < 10000.0


# ═══════════════════════════════════════════════════════════════════════
# Unit Conversion Tests
# ═══════════════════════════════════════════════════════════════════════

class TestUnits:
    def test_mm_m_roundtrip(self):
        assert abs(m_to_mm(mm_to_m(25.4)) - 25.4) < 1e-10

    def test_rpm_rad_s(self):
        # 60 RPM = 2*pi rad/s
        assert abs(rpm_to_rad_s(60.0) - 2 * math.pi) < 1e-10

    def test_deg_rad(self):
        assert abs(deg_to_rad(180.0) - math.pi) < 1e-10


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
