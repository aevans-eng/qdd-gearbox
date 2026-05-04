"""Log QDD thermistor serial CSV output to testing/data.

Default Arduino sketch settings:
  - Port: COM6
  - Baud: 115200
  - CSV: time_ms,adc_counts,voltage_v,resistance_ohm,temp_c,temp_f
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
import sys
import time

import serial
from serial.tools import list_ports


EXPECTED_HEADER = [
    "time_ms",
    "adc_counts",
    "voltage_v",
    "resistance_ohm",
    "temp_c",
    "temp_f",
]


def default_output_path() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root / "testing" / "data" / f"thermistor-log-{timestamp}.csv"


def find_arduino_port() -> str | None:
    ports = list(list_ports.comports())

    for port in ports:
        text = " ".join(
            str(value)
            for value in [
                port.device,
                port.description,
                port.manufacturer,
                port.hwid,
            ]
            if value
        ).lower()
        if "arduino" in text or "ch340" in text or "wch" in text:
            return port.device

    if len(ports) == 1:
        return ports[0].device

    return None


def parse_row(line: str) -> list[str] | None:
    parts = [part.strip() for part in line.split(",")]

    if parts == EXPECTED_HEADER:
        return None

    if len(parts) != len(EXPECTED_HEADER):
        return None

    try:
        float(parts[0])
        float(parts[1])
        float(parts[2])
        float(parts[3])
        float(parts[4])
        float(parts[5])
    except ValueError:
        return None

    return parts


def log_serial(
    port: str,
    baud: int,
    output_path: Path,
    max_rows: int | None,
    max_seconds: float | None,
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows_written = 0
    started_at = datetime.now().isoformat(timespec="seconds")

    print(f"Opening {port} at {baud} baud")
    print(f"Writing {output_path}")
    print("Press Ctrl+C to stop.")

    with serial.Serial(port, baudrate=baud, timeout=2) as ser:
        # Opening an Uno resets it. Give the sketch time to reboot and print header.
        time.sleep(2.5)
        ser.reset_input_buffer()

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["pc_timestamp", *EXPECTED_HEADER])

            deadline = time.monotonic() + max_seconds if max_seconds is not None else None

            while max_rows is None or rows_written < max_rows:
                if deadline is not None and time.monotonic() >= deadline:
                    break

                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="replace").strip()
                row = parse_row(line)
                if row is None:
                    continue

                pc_timestamp = datetime.now().isoformat(timespec="milliseconds")
                writer.writerow([pc_timestamp, *row])
                file.flush()
                rows_written += 1

                temp_c = row[4]
                voltage = row[2]
                print(f"{pc_timestamp}  temp={temp_c} C  voltage={voltage} V")

    print(f"Stopped. Rows written: {rows_written}. Started: {started_at}")
    return rows_written


def main() -> int:
    parser = argparse.ArgumentParser(description="Log QDD thermistor Arduino CSV data.")
    parser.add_argument("--port", default=None, help="Serial port, for example COM6.")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate.")
    parser.add_argument("--output", type=Path, default=default_output_path())
    parser.add_argument("--rows", type=int, default=None, help="Stop after this many rows.")
    parser.add_argument("--seconds", type=float, default=None, help="Stop after this many seconds.")
    args = parser.parse_args()

    port = args.port or find_arduino_port()
    if port is None:
        print("Could not auto-detect Arduino port. Try --port COM6.", file=sys.stderr)
        return 2

    try:
        rows = log_serial(port, args.baud, args.output, args.rows, args.seconds)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        return 0
    except serial.SerialException as exc:
        print(f"Serial error: {exc}", file=sys.stderr)
        return 1

    return 0 if rows > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
