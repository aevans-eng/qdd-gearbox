"""BLE protocol definitions for the Saris Hammer H2 trainer.

The H2 uses Cycling Power Service (0x1818), NOT standard FTMS (0x1826).
Resistance control uses a Saris proprietary characteristic.

References:
    - Bluetooth CPS Spec: bluetooth.com/specifications/specs/cycling-power-service-1-1/
    - qdomyos-zwift: github.com/cagnulein/qdomyos-zwift (resistance protocol)
"""

import struct
from dataclasses import dataclass
from enum import IntEnum

# --- BLE identifiers ---
DEFAULT_ADDR = "EE:51:A8:51:70:1A"
CPS_MEASUREMENT_UUID = "00002a63-0000-1000-8000-00805f9b34fb"
SARIS_SERVICE_UUID = "c0f4013a-a837-4165-bab9-654ef70747c6"
SARIS_RESISTANCE_UUID = "ca31a533-a858-4dc7-a650-fdeb6dad4c14"

# --- CPS constants ---
WHEEL_TIME_RESOLUTION = 2048.0   # 1/2048 s per tick
WHEEL_TIME_ROLLOVER = 65536      # uint16 rollover
TORQUE_RESOLUTION = 32.0         # 1/32 Nm per LSB


class ResistanceMode(IntEnum):
    """Saris proprietary resistance modes (reverse-engineered, UNTESTED).

    Source: qdomyos-zwift CycleOps Phantom Bike driver.
    """
    MANUAL_POWER = 0x01  # ERG mode - hold target watts
    MANUAL_SLOPE = 0x02  # SIM mode - simulate road grade


@dataclass
class CpsMeasurement:
    """Parsed Cycling Power Service 0x2A63 notification."""
    power_w: int = 0
    acc_torque_nm: float = 0.0
    wheel_revs: int = 0
    wheel_event_time: int = 0
    crank_revs: int = 0
    crank_event_time: int = 0


@dataclass
class DynoSample:
    """Single data point: raw CPS fields + derived quantities."""
    elapsed_s: float = 0.0
    power_w: int = 0
    acc_torque_nm: float = 0.0
    wheel_revs: int = 0
    wheel_event_time: int = 0
    crank_revs: int = 0
    crank_event_time: int = 0
    rpm: float = 0.0
    omega_rad_s: float = 0.0
    inst_torque_nm: float = 0.0
    torque_from_power_nm: float = 0.0
    alpha_rad_s2: float = 0.0

    FIELDS = [
        "elapsed_s", "power_w", "acc_torque_nm",
        "wheel_revs", "wheel_event_time",
        "crank_revs", "crank_event_time",
        "rpm", "omega_rad_s",
        "inst_torque_nm", "torque_from_power_nm", "alpha_rad_s2",
    ]

    def to_dict(self) -> dict:
        return {
            "elapsed_s": round(self.elapsed_s, 3),
            "power_w": self.power_w,
            "acc_torque_nm": round(self.acc_torque_nm, 4),
            "wheel_revs": self.wheel_revs,
            "wheel_event_time": self.wheel_event_time,
            "crank_revs": self.crank_revs,
            "crank_event_time": self.crank_event_time,
            "rpm": round(self.rpm, 2),
            "omega_rad_s": round(self.omega_rad_s, 4),
            "inst_torque_nm": round(self.inst_torque_nm, 4),
            "torque_from_power_nm": round(self.torque_from_power_nm, 4),
            "alpha_rad_s2": round(self.alpha_rad_s2, 4),
        }


def parse_cps(data: bytes) -> CpsMeasurement:
    """Parse a Cycling Power Measurement (0x2A63) BLE notification.

    The H2 reports flags 0x3418: accumulated torque, wheel revs, crank revs.
    """
    m = CpsMeasurement()
    flags = struct.unpack_from("<H", data, 0)[0]
    m.power_w = struct.unpack_from("<h", data, 2)[0]
    offset = 4

    # Bit 0: pedal power balance
    if flags & 0x01:
        offset += 1

    # Bit 2: accumulated torque (1/32 Nm)
    if flags & 0x04:
        raw = struct.unpack_from("<H", data, offset)[0]
        m.acc_torque_nm = raw / TORQUE_RESOLUTION
        offset += 2

    # Bit 4: wheel revolution data
    if flags & 0x10:
        m.wheel_revs = struct.unpack_from("<I", data, offset)[0]
        m.wheel_event_time = struct.unpack_from("<H", data, offset + 4)[0]
        offset += 6

    # Bit 5: crank revolution data
    if flags & 0x20:
        m.crank_revs = struct.unpack_from("<H", data, offset)[0]
        m.crank_event_time = struct.unpack_from("<H", data, offset + 2)[0]
        offset += 4

    return m


def build_resistance_cmd(mode: ResistanceMode, value: int) -> bytes:
    """Build a 10-byte Saris proprietary resistance command.

    WARNING: Reverse-engineered protocol, NOT YET TESTED on hardware.

    Args:
        mode: MANUAL_POWER (ERG) or MANUAL_SLOPE (SIM)
        value: Target watts (ERG) or grade * 100 (SIM, e.g. 500 = 5.0%)
    """
    lo = value & 0xFF
    hi = (value >> 8) & 0xFF
    return bytes([0x00, 0x10, int(mode), lo, hi, 0x00, 0x00, 0x00, 0x00, 0x00])
