#!/usr/bin/env python3
"""Saris H2 Bike Trainer Dyno -- CLI

Usage:
    python dyno.py capture [--duration 60] [--output runs/run_002.csv]
    python dyno.py plot runs/run_001.csv [--save]
    python dyno.py scan [--timeout 10]
"""

import argparse
import asyncio
import sys
from pathlib import Path


def cmd_capture(args):
    from saris_h2.capture import run_capture
    from saris_h2.plot import plot_dyno
    from saris_h2.protocol import DEFAULT_ADDR

    output = Path(args.output)
    session = asyncio.run(
        run_capture(args.duration, output, args.addr or DEFAULT_ADDR, quiet=args.quiet)
    )

    if session.samples and not args.no_plot:
        rows = [s.to_dict() for s in session.samples]
        plot_dyno(rows, title=output.stem, save_path=output.with_suffix(".png"))
    if not session.samples:
        print("No dyno samples captured.")
        sys.exit(1)


def cmd_plot(args):
    from saris_h2.plot import load_csv, plot_dyno

    path = Path(args.csv)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    rows = load_csv(path)
    save_path = path.with_suffix(".png") if args.save else None
    plot_dyno(rows, title=path.stem, save_path=save_path)


def cmd_scan(args):
    from saris_h2.capture import scan_for_trainer

    addr = asyncio.run(scan_for_trainer(timeout=args.timeout))
    if not addr:
        print("No Saris Hammer trainer found.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Saris H2 Bike Trainer Dyno",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python dyno.py capture --duration 120\n"
               "  python dyno.py plot runs/run_001.csv --save\n"
               "  python dyno.py scan\n",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- capture ---
    p = sub.add_parser("capture", help="Record dyno data via BLE")
    p.add_argument("--duration", "-d", type=float, default=60,
                   help="Capture duration in seconds (default: 60)")
    p.add_argument("--output", "-o", type=str, default="runs/run_001.csv",
                   help="Output CSV path (default: runs/run_001.csv)")
    p.add_argument("--addr", type=str, default=None,
                   help="BLE address override (default: auto-detect)")
    p.add_argument("--no-plot", action="store_true",
                   help="Skip plotting after capture")
    p.add_argument("--quiet", "-q", action="store_true",
                   help="Suppress live sample output")
    p.set_defaults(func=cmd_capture)

    # --- plot ---
    p = sub.add_parser("plot", help="Plot existing CSV data")
    p.add_argument("csv", help="Path to dyno CSV file")
    p.add_argument("--save", "-s", action="store_true",
                   help="Save plot as PNG alongside CSV")
    p.set_defaults(func=cmd_plot)

    # --- scan ---
    p = sub.add_parser("scan", help="Scan for Saris Hammer trainer via BLE")
    p.add_argument("--timeout", "-t", type=float, default=5,
                   help="Scan timeout in seconds (default: 5)")
    p.set_defaults(func=cmd_scan)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
