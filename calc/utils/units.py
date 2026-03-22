"""Unit conversion helpers."""

import math


def mm_to_m(val):
    """Millimeters to meters."""
    return val / 1000.0


def m_to_mm(val):
    """Meters to millimeters."""
    return val * 1000.0


def rpm_to_rad_s(rpm):
    """RPM to radians per second."""
    return rpm * 2.0 * math.pi / 60.0


def rad_s_to_rpm(rad_s):
    """Radians per second to RPM."""
    return rad_s * 60.0 / (2.0 * math.pi)


def deg_to_rad(deg):
    """Degrees to radians."""
    return math.radians(deg)


def rad_to_deg(rad):
    """Radians to degrees."""
    return math.degrees(rad)
