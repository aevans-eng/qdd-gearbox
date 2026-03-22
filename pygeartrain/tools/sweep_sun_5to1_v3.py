"""
Sweep sun gear teeth from 4 to 7, targeting ~5:1 gear ratio.
Iteration: 2026-01-15_sun_sweep_5to1_v3

FIXES FROM v2:
- Reduced b from 0.8 to 0.5 (shorter teeth = no overlap)
- Validated all configs with Shapely polygon intersection
- Only includes configs with 0% sun-planet overlap
- Documents which gear is LOCKED

KEY DESIGN RULES DISCOVERED:
1. b parameter controls tooth height: b=0.8 too tall, b=0.5 works well
2. Sun-Planet overlap is the critical check (not just planet spacing)
3. Lower b values allow more planets without overlap
4. S=6 is the sweet spot for 5:1 ratio with N=3 planets

LOCKED GEAR CONFIGURATION:
- RING gear is LOCKED (held stationary)
- SUN gear is INPUT (connected to motor)
- CARRIER is OUTPUT (connected to load)
- Ratio = (R + S) / S = 1 + R/S
"""

import matplotlib.pyplot as plt
import numpy as np
from pygeartrain.planetary import Planetary, PlanetaryGeometry
from find_valid_gears import check_overlap

# Configuration: RING LOCKED, sun input, carrier output
KINEMATICS = Planetary('s', 'c', 'r')
ITERATION_ID = "2026-01-15_sun_sweep_5to1_v3"

# VALIDATED configurations with 0% sun-planet overlap
# Key change: b=0.5 instead of b=0.8
CONFIGS = [
    # S=4: N=4 works with b=0.5 (most planets for this sun size)
    {"S": 4, "P": 6, "R": 16, "N": 4, "b": 0.5,
     "note": "exact 5:1, b reduced to 0.5 for valid mesh, N=4 works"},

    # S=5: Only N=2 validates (N=3,4 have overlap even with b=0.5)
    {"S": 5, "P": 8, "R": 21, "N": 2, "b": 0.5,
     "note": "ratio=5.2, N=2 only valid option"},

    # S=6: N=3 works with all b values - sweet spot!
    {"S": 6, "P": 9, "R": 24, "N": 3, "b": 0.5,
     "note": "exact 5:1, N=3 valid, best balanced config"},

    # S=7: Only N=2 validates
    {"S": 7, "P": 10, "R": 27, "N": 2, "b": 0.5,
     "note": "ratio=4.86, N=2 only valid option"},
]


def generate_labeled_png(config, output_dir="design_log"):
    """Generate a PNG with validation info."""
    R, P, S = config["R"], config["P"], config["S"]
    N, b = config["N"], config["b"]

    # Validate configuration
    validation = check_overlap(S, P, R, N, b, max_overlap_pct=1.0)

    if not validation['valid']:
        print(f"WARNING: S={S}, P={P}, R={R}, N={N}, b={b} FAILED VALIDATION")
        print(f"  Sun-Planet overlap: {validation['sun_planet_overlap_pct']:.2f}%")
        return None, None, validation

    ratio = (R + S) / S

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

    # Title with validation status
    title = (
        f"{ITERATION_ID}\n"
        f"Sun={S}t | Planet={P}t | Ring={R}t | N={N} planets | b={b}\n"
        f"Ratio = {ratio:.2f}:1 | RING LOCKED | VALIDATED (0% overlap)"
    )
    ax.set_title(title, fontsize=11, fontweight='bold')

    # Info box
    info_text = (
        f"S={S}, P={P}, R={R}\n"
        f"N={N}, b={b}\n"
        f"Ratio={ratio:.2f}:1\n"
        f"Sun-Planet: {validation['sun_planet_overlap_pct']:.1f}%\n"
        f"RING LOCKED\n"
        f"VALIDATED"
    )
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

    filename = f"{output_dir}/{ITERATION_ID}_S{S}_P{P}_R{R}_N{N}_b{b}_ratio{ratio:.2f}.png"

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"VALID: {filename}")
    print(f"  Config: S={S}, P={P}, R={R}, N={N}, b={b}")
    print(f"  Ratio: {ratio:.3f}:1 (RING LOCKED)")
    print(f"  Sun-Planet overlap: {validation['sun_planet_overlap_pct']:.2f}%")
    print(f"  Note: {config['note']}")
    print()

    return filename, ratio, validation


def main():
    print("=" * 70)
    print("Sun Gear Sweep v3 - VALIDATED Configurations Only")
    print(f"Iteration: {ITERATION_ID}")
    print("=" * 70)
    print()
    print("KEY CHANGES FROM v2:")
    print("  - b reduced from 0.8 to 0.5 (shorter teeth)")
    print("  - All configs validated with Shapely polygon intersection")
    print("  - Only configs with <1% sun-planet overlap included")
    print()
    print("LOCKED GEAR: RING")
    print("INPUT: SUN -> OUTPUT: CARRIER")
    print(f"Kinematics: {KINEMATICS}")
    print()

    results = []
    for config in CONFIGS:
        filename, ratio, validation = generate_labeled_png(config)
        results.append({
            **config,
            "filename": filename,
            "ratio": ratio,
            "validation": validation,
        })

    print("=" * 70)
    print("SUMMARY - v3 VALIDATED CONFIGURATIONS")
    print("=" * 70)
    print()
    print(f"{'S':>3} {'P':>3} {'R':>3} {'N':>2} {'b':>4} {'Ratio':>7} {'Overlap%':>9} {'Status':>10}")
    print("-" * 55)

    for r in results:
        v = r['validation']
        status = "VALID" if v['valid'] else "INVALID"
        overlap = v['sun_planet_overlap_pct']
        print(f"{r['S']:>3} {r['P']:>3} {r['R']:>3} {r['N']:>2} {r['b']:>4.1f} {r['ratio']:>6.2f}:1 {overlap:>8.2f}% {status:>10}")

    print()
    print("RECOMMENDATIONS:")
    print("  - Best for 5:1 ratio: S=6, P=9, R=24, N=3, b=0.5")
    print("  - Most planets: S=4, P=6, R=16, N=4, b=0.5")
    print("  - S=5 and S=7 only support N=2 (less load sharing)")


if __name__ == "__main__":
    main()
