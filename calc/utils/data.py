"""Data structures for QDD gearbox calculations."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GearParams:
    """Parameters defining a single gear."""
    module_mm: float          # Gear module (mm)
    num_teeth: int            # Number of teeth
    pressure_angle_deg: float = 20.0  # Pressure angle (degrees)
    face_width_mm: float = 10.0       # Face width (mm)
    helix_angle_deg: float = 0.0      # 0 = spur gear

    @property
    def pitch_diameter_mm(self) -> float:
        return self.module_mm * self.num_teeth

    @property
    def base_diameter_mm(self) -> float:
        import math
        return self.pitch_diameter_mm * math.cos(math.radians(self.pressure_angle_deg))

    @property
    def addendum_mm(self) -> float:
        return self.module_mm

    @property
    def dedendum_mm(self) -> float:
        return 1.25 * self.module_mm

    @property
    def outer_diameter_mm(self) -> float:
        return self.pitch_diameter_mm + 2 * self.addendum_mm

    @property
    def root_diameter_mm(self) -> float:
        return self.pitch_diameter_mm - 2 * self.dedendum_mm


@dataclass
class PlanetarySet:
    """Complete planetary gear set definition."""
    sun: GearParams
    planet: GearParams
    ring_teeth: int
    num_planets: int = 3

    @property
    def ratio(self) -> float:
        """Gear ratio (ring fixed, carrier output)."""
        return 1.0 + self.ring_teeth / self.sun.num_teeth

    @property
    def ring_pitch_diameter_mm(self) -> float:
        return self.sun.module_mm * self.ring_teeth


@dataclass
class MaterialProps:
    """Material mechanical properties."""
    name: str
    yield_strength_mpa: float
    uts_mpa: float
    elastic_modulus_gpa: float
    poisson_ratio: float

    @property
    def elastic_modulus_mpa(self) -> float:
        return self.elastic_modulus_gpa * 1000.0


# Pre-defined materials
PLA_PLUS = MaterialProps("PLA+", 50.0, 60.0, 3.5, 0.36)
NYLON_PA6 = MaterialProps("Nylon PA6", 70.0, 85.0, 2.8, 0.40)
STEEL_1045 = MaterialProps("Steel 1045", 530.0, 625.0, 205.0, 0.29)


@dataclass
class BearingData:
    """Bearing catalog data for life calculations."""
    designation: str
    bore_mm: float
    od_mm: float
    width_mm: float
    dynamic_rating_kn: float   # C — basic dynamic load rating
    static_rating_kn: float    # C0 — basic static load rating
    bearing_type: str = "deep_groove"  # deep_groove, angular_contact, etc.
    contact_angle_deg: float = 0.0


# Pre-defined bearings from BOM
BEARING_6805 = BearingData("6805-2RS", 25.0, 37.0, 7.0, 6.37, 4.15)
BEARING_685 = BearingData("685ZZ", 5.0, 11.0, 5.0, 1.14, 0.42)
BEARING_683 = BearingData("683ZZ", 3.0, 7.0, 3.0, 0.54, 0.20)
BEARING_6710 = BearingData("6710-2RS", 50.0, 62.0, 6.0, 4.75, 4.00)


@dataclass
class LoadCase:
    """A single load case for bearing life analysis."""
    radial_load_n: float
    axial_load_n: float = 0.0
    speed_rpm: float = 0.0
    duration_fraction: float = 1.0  # Fraction of total duty cycle
    description: str = ""


@dataclass
class ThermalNode:
    """A node in the lumped-parameter thermal model."""
    name: str
    thermal_mass_j_per_k: float      # Capacitance: mass * specific_heat
    heat_generation_w: float = 0.0   # Internal heat source
    temperature_c: float = 25.0      # Current temperature


@dataclass
class ThermalResistance:
    """Thermal resistance between two nodes."""
    node_a: str
    node_b: str
    resistance_k_per_w: float  # Thermal resistance (K/W)
