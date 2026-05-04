"""Resistance control for the Saris H2 trainer.

!! WARNING: This module uses a reverse-engineered protocol and is UNTESTED !!

The command format was extracted from qdomyos-zwift's CycleOps driver.
Write 10-byte commands to the Saris proprietary characteristic:
    Service:  c0f4013a-a837-4165-bab9-654ef70747c6
    Char:     ca31a533-a858-4dc7-a650-fdeb6dad4c14

Timing: 3+ seconds between commands, 4-5 seconds for full brake engagement.
"""

import asyncio

from bleak import BleakClient

from .protocol import (
    SARIS_RESISTANCE_UUID,
    ResistanceMode,
    build_resistance_cmd,
)


async def set_erg_power(client: BleakClient, watts: int):
    """Set target power in ERG mode (constant wattage).

    The trainer adjusts brake force to maintain the target power
    regardless of cadence.

    Args:
        client: Connected BleakClient
        watts: Target power 0-2000W
    """
    cmd = build_resistance_cmd(ResistanceMode.MANUAL_POWER, watts)
    await client.write_gatt_char(SARIS_RESISTANCE_UUID, cmd)
    print(f"[UNTESTED] ERG target: {watts}W")


async def set_sim_grade(client: BleakClient, grade_pct: float):
    """Set simulated road grade in SIM mode.

    Args:
        client: Connected BleakClient
        grade_pct: Grade in percent (e.g. 5.0 = 5% climb, -3.0 = 3% descent)
    """
    value = int(grade_pct * 100)
    cmd = build_resistance_cmd(ResistanceMode.MANUAL_SLOPE, value)
    await client.write_gatt_char(SARIS_RESISTANCE_UUID, cmd)
    print(f"[UNTESTED] SIM grade: {grade_pct:.1f}%")


async def sweep_resistance(
    client: BleakClient,
    mode: ResistanceMode,
    start: int,
    stop: int,
    step: int,
    hold_seconds: float = 5.0,
):
    """Step through resistance levels, holding each for a set time.

    Useful for mapping the brake torque curve empirically. Run this
    while capturing data to get T vs RPM at each resistance setting.

    Args:
        client: Connected BleakClient
        mode: MANUAL_POWER or MANUAL_SLOPE
        start: Starting value (watts or grade*100)
        stop: Ending value (inclusive)
        step: Increment per step
        hold_seconds: Dwell time at each level (5s+ recommended)
    """
    for value in range(start, stop + 1, step):
        cmd = build_resistance_cmd(mode, value)
        await client.write_gatt_char(SARIS_RESISTANCE_UUID, cmd)
        if mode == ResistanceMode.MANUAL_POWER:
            label = f"{value}W"
        else:
            label = f"{value / 100:.1f}%"
        print(f"[UNTESTED] Set {label}, holding {hold_seconds}s...")
        await asyncio.sleep(hold_seconds)
    print("Sweep complete.")
