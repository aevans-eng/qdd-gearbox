"""BLE capture session for the Saris H2 trainer.

Connects via Cycling Power Service, logs all fields + derived quantities,
and writes to CSV with optional live terminal display.
"""

import asyncio
import csv
import math
import time
from pathlib import Path

from bleak import BleakClient, BleakScanner

from .protocol import (
    DEFAULT_ADDR,
    CPS_MEASUREMENT_UUID,
    WHEEL_TIME_RESOLUTION,
    WHEEL_TIME_ROLLOVER,
    DynoSample,
    parse_cps,
)


class DynoSession:
    """Manages a BLE capture session with real-time derived quantity computation.

    Fixes from v0 monolithic script:
        - RPM holds last valid value instead of alternating with zero
        - Tracks flywheel-stopped condition via power + rev count
    """

    def __init__(self, quiet: bool = False):
        self.samples: list[DynoSample] = []
        self.quiet = quiet
        self._t0: float | None = None
        self._prev_wheel_revs: int | None = None
        self._prev_wheel_time: int | None = None
        self._prev_acc_torque: float | None = None
        self._prev_rpm: float = 0.0
        self._prev_omega: float = 0.0
        self._prev_timestamp: float | None = None
        self._last_valid_rpm: float = 0.0

    def on_notify(self, sender, data: bytearray):
        """BLE notification callback. Parses CPS and computes derived quantities."""
        now = time.time()
        if self._t0 is None:
            self._t0 = now
        elapsed = now - self._t0

        m = parse_cps(data)

        # --- RPM from wheel revolution deltas ---
        rpm = 0.0
        if self._prev_wheel_revs is not None and m.wheel_revs != self._prev_wheel_revs:
            # New wheel event — compute fresh RPM
            d_revs = m.wheel_revs - self._prev_wheel_revs
            d_time = (m.wheel_event_time - self._prev_wheel_time) % WHEEL_TIME_ROLLOVER
            if d_time > 0:
                seconds = d_time / WHEEL_TIME_RESOLUTION
                rpm = (d_revs / seconds) * 60.0
                self._last_valid_rpm = rpm
        elif self._prev_wheel_revs is not None:
            # No new wheel event — hold last valid RPM if power > 0
            if m.power_w > 0:
                rpm = self._last_valid_rpm
            else:
                rpm = 0.0
                self._last_valid_rpm = 0.0

        omega = rpm * 2.0 * math.pi / 60.0

        # --- Instantaneous torque from accumulated torque delta ---
        inst_torque = 0.0
        if self._prev_acc_torque is not None and self._prev_wheel_revs is not None:
            d_torque = m.acc_torque_nm - self._prev_acc_torque
            d_revs_t = m.wheel_revs - self._prev_wheel_revs
            if d_revs_t > 0:
                inst_torque = d_torque / d_revs_t * (2.0 * math.pi)
            elif rpm == 0 and self._prev_rpm > 0:
                inst_torque = 0.0

        # --- Angular acceleration ---
        alpha = 0.0
        if self._prev_timestamp is not None:
            dt = now - self._prev_timestamp
            if dt > 0:
                alpha = (omega - self._prev_omega) / dt

        # --- Torque from power (cross-check: T = P / omega) ---
        torque_from_power = 0.0
        if omega > 0.1:
            torque_from_power = m.power_w / omega

        # Update state
        self._prev_wheel_revs = m.wheel_revs
        self._prev_wheel_time = m.wheel_event_time
        self._prev_acc_torque = m.acc_torque_nm
        self._prev_rpm = rpm
        self._prev_omega = omega
        self._prev_timestamp = now

        sample = DynoSample(
            elapsed_s=elapsed,
            power_w=m.power_w,
            acc_torque_nm=m.acc_torque_nm,
            wheel_revs=m.wheel_revs,
            wheel_event_time=m.wheel_event_time,
            crank_revs=m.crank_revs,
            crank_event_time=m.crank_event_time,
            rpm=rpm,
            omega_rad_s=omega,
            inst_torque_nm=inst_torque,
            torque_from_power_nm=torque_from_power,
            alpha_rad_s2=alpha,
        )
        self.samples.append(sample)

        if not self.quiet:
            print(
                f"[{elapsed:6.1f}s] {m.power_w:4d}W | "
                f"T={inst_torque:6.2f} Nm | "
                f"{rpm:6.1f} RPM | "
                f"w={omega:5.2f} rad/s | "
                f"a={alpha:+6.2f} rad/s2 | "
                f"Revs:{m.wheel_revs}"
            )

    def write_csv(self, path: Path):
        """Write captured samples to CSV."""
        if not self.samples:
            print("No data to write.")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = [s.to_dict() for s in self.samples]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=DynoSample.FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nSaved {len(rows)} samples to {path}")

    def print_summary(self):
        """Print capture statistics."""
        if not self.samples:
            return
        powers = [s.power_w for s in self.samples if s.power_w > 0]
        rpms = [s.rpm for s in self.samples if s.rpm > 0]
        duration = self.samples[-1].elapsed_s
        print(f"Duration: {duration:.1f}s, {len(self.samples)} samples")
        if powers:
            avg_p = sum(powers) / len(powers)
            print(f"Power:    {min(powers)}-{max(powers)}W (avg {avg_p:.1f}W)")
        if rpms:
            avg_r = sum(rpms) / len(rpms)
            print(f"RPM:      {min(rpms):.0f}-{max(rpms):.0f} (avg {avg_r:.0f})")


async def scan_for_trainer(timeout: float = 5.0) -> str | None:
    """Scan BLE for a Saris Hammer trainer. Returns address or None."""
    print(f"Scanning for Hammer trainer ({timeout}s)...")
    devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
    for addr, (device, adv) in devices.items():
        name = adv.local_name or device.name or ""
        if "hammer" in name.lower():
            print(f"Found: {name} at {addr}")
            return addr
    return None


async def run_capture(
    duration: float,
    output: Path,
    addr: str = DEFAULT_ADDR,
    quiet: bool = False,
) -> DynoSession:
    """Connect to the trainer and capture data for the specified duration.

    Tries the known BLE address first, falls back to scanning.
    """
    session = DynoSession(quiet=quiet)

    print(f"Connecting to Hammer at {addr}...")
    try:
        async with BleakClient(addr, timeout=15) as client:
            print(f"Connected! Recording for {duration}s -- spin it up!\n")
            await client.start_notify(CPS_MEASUREMENT_UUID, session.on_notify)
            await asyncio.sleep(duration)
            await client.stop_notify(CPS_MEASUREMENT_UUID)
    except Exception as e:
        print(f"Direct connection failed ({e}), scanning...")
        found = await scan_for_trainer()
        if not found:
            print("No Hammer trainer found. Is it powered on?")
            return session
        async with BleakClient(found, timeout=15) as client:
            print(f"Connected! Recording for {duration}s\n")
            await client.start_notify(CPS_MEASUREMENT_UUID, session.on_notify)
            await asyncio.sleep(duration)
            await client.stop_notify(CPS_MEASUREMENT_UUID)

    session.write_csv(output)
    session.print_summary()
    return session
