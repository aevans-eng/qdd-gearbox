"""
Sweep sun gear teeth from 4 to 7, targeting ~5:1 gear ratio (+-1 tolerance).
Iteration: 2026-01-15_sun_sweep_5to1_v2

FIXES FROM v1:
- Corrected N values to prevent planet overlap (max N=3 for these configs)
- Added overlap validation
- Clearly documented which gear is LOCKED

LOCKED GEAR CONFIGURATION:
==========================
This sweep uses: RING LOCKED, SUN INPUT, CARRIER OUTPUT
- The RING gear is held stationary (bolted to housing)
- The SUN gear is the input (connected to motor)
- The CARRIER is the output (connected to load)
- Ratio = (R + S) / S = 1 + R/S

Other configurations give different ratios:
- Sun locked, Carrier->Ring: ratio = R/(R+S) < 1 [speed increase]
- Carrier locked, Sun->Ring: ratio = -R/S [reverses direction]

OVERLAP DESIGN RULE:
====================
For N planets evenly spaced on carrier radius 1:
- Planet spacing = 2 * sin(pi/N)
- Planet outer diameter ~ (P + 1.5) / (S + P)
- Require: spacing > diameter * 1.1 (10% clearance)

For ~5:1 ratio configs, max planets is typically N=3.
"""

import matplotlib.pyplot as plt
import numpy as np
from pygeartrain.planetary import Planetary, PlanetaryGeometry
from gear_design_rules import check_planet_overlap, valid_planet_counts, calculate_ratio

# Configuration: RING LOCKED, sun input, carrier output --> gives reduction ratio
KINEMATICS = Planetary('s', 'c', 'r')
ITERATION_ID = "2026-01-15_sun_sweep_5to1_v2"

# Configurations with validated N values (no overlap)
# Ratio tolerance: 4:1 to 6:1
CONFIGS = [
    # S=4: exact 5:1, but reduced to N=3 to avoid overlap
    {"S": 4, "P": 6, "R": 16, "N": 3, "b": 0.8,
     "note": "exact 5:1, N reduced from 4 to 3 (overlap fix)"},

    # S=5: P must be integer, closest is P=7 (ratio=4.8) or P=8 (ratio=5.2)
    {"S": 5, "P": 8, "R": 21, "N": 3, "b": 0.8,
     "note": "P rounded up, ratio=5.2"},

    # S=6: exact 5:1
    {"S": 6, "P": 9, "R": 24, "N": 3, "b": 0.8,
     "note": "exact 5:1"},

    # S=7: P=10.5 needed, using P=10 gives ratio=4.86
    {"S": 7, "P": 10, "R": 27, "N": 3, "b": 0.8,
     "note": "P rounded down, ratio=4.86"},
]


def generate_labeled_png(config, output_dir="design_log"):
    """Generate a PNG with labels in filename and on the plot, with overlap validation."""
    R, P, S = config["R"], config["P"], config["S"]
    N, b = config["N"], config["b"]

    # Validate no overlap
    overlap_check = check_planet_overlap(S, P, N, safety_margin=1.1, b=b)
    if not overlap_check['valid']:
        print(f"WARNING: S={S}, P={P}, N={N} has planet overlap!")
        print(f"  Clearance: {overlap_check['clearance']:.3f} ({overlap_check['clearance_pct']:.1f}%)")
        valid_N = valid_planet_counts(S, P, R, safety_margin=1.1, b=b)
        print(f"  Valid N values: {valid_N}")

    # Calculate actual ratio
    ratio = calculate_ratio(S, P, R, ('s', 'c', 'r'))

    # Create gear geometry
    gear = PlanetaryGeometry.create(KINEMATICS, (R, P, S), N, b=b)

    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Plot gear at phase 0
    gear._plot(ax, phase=0, col='steelblue')

    ax.set_aspect('equal')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.grid(True, alpha=0.3)

    # Title with all parameters and LOCKED GEAR info
    title = (
        f"{ITERATION_ID}\n"
        f"Sun={S}t | Planet={P}t | Ring={R}t | N={N} planets | b={b}\n"
        f"Ratio = {ratio:.2f}:1 | RING LOCKED | Sun(in)->Carrier(out)"
    )
    ax.set_title(title, fontsize=11, fontweight='bold')

    # Add text annotation with key params and clearance
    clearance_pct = overlap_check['clearance_pct']
    info_text = (
        f"S={S}, P={P}, R={R}\n"
        f"N={N}, b={b}\n"
        f"Ratio={ratio:.2f}:1\n"
        f"Clearance={clearance_pct:.1f}%\n"
        f"RING LOCKED"
    )
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Filename with iteration ID and parameters
    filename = f"{output_dir}/{ITERATION_ID}_S{S}_P{P}_R{R}_N{N}_ratio{ratio:.2f}.png"

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved: {filename}")
    print(f"  Config: R={R}, P={P}, S={S}, N={N}, b={b}")
    print(f"  Actual ratio: {ratio:.3f}:1 (RING LOCKED, Sun->Carrier)")
    print(f"  Planet clearance: {clearance_pct:.1f}%")
    print(f"  Note: {config['note']}")
    print()

    return filename, ratio, overlap_check


def main():
    print("=" * 70)
    print("Sun Gear Sweep v2 - Targeting 5:1 Ratio (+-1 tolerance)")
    print(f"Iteration: {ITERATION_ID}")
    print("=" * 70)
    print()
    print("LOCKED GEAR CONFIGURATION:")
    print("  - RING gear is LOCKED (held stationary)")
    print("  - SUN gear is INPUT (connected to motor)")
    print("  - CARRIER is OUTPUT (connected to load)")
    print(f"  - Kinematics: {KINEMATICS}")
    print("  - Ratio formula: (R + S) / S = 1 + R/S")
    print()
    print("OVERLAP DESIGN RULE:")
    print("  - Planets spaced at 2*sin(pi/N) on unit carrier")
    print("  - Require 10% minimum clearance between planets")
    print("  - Max N = 3 for these configurations")
    print()

    results = []
    for config in CONFIGS:
        try:
            filename, ratio, overlap = generate_labeled_png(config)
            results.append({
                **config,
                "filename": filename,
                "actual_ratio": ratio,
                "clearance_pct": overlap['clearance_pct'],
                "overlap_valid": overlap['valid'],
            })
        except Exception as e:
            print(f"ERROR with S={config['S']}: {e}")
            import traceback
            traceback.print_exc()
            results.append({**config, "error": str(e)})

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Configuration: RING LOCKED | Sun(input) -> Carrier(output)")
    print()
    print(f"{'S':>3} {'P':>3} {'R':>3} {'N':>2} {'Ratio':>7} {'Clear%':>7} {'Status':>10}")
    print("-" * 50)

    for r in results:
        if "error" in r:
            print(f"{r['S']:>3}: FAILED - {r['error']}")
        else:
            status = "OK" if r['overlap_valid'] else "OVERLAP!"
            print(f"{r['S']:>3} {r['P']:>3} {r['R']:>3} {r['N']:>2} {r['actual_ratio']:>6.2f}:1 {r['clearance_pct']:>6.1f}% {status:>10}")

    return results


if __name__ == "__main__":
    main()
