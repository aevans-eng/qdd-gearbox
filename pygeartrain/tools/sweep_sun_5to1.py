"""
Sweep sun gear teeth from 4 to 7, targeting ~5:1 gear ratio.
Iteration: 2026-01-15_sun_sweep_5to1

For 5:1 ratio with sun input, carrier output, ring fixed:
  ratio = 1 + R/S = 5  -->  R = 4*S

Constraint for meshing: R = S + 2*P  -->  P = (R-S)/2 = 3S/2

For integer P, S must be even. For odd S, we round P and accept slight ratio deviation.
"""

import matplotlib.pyplot as plt
import numpy as np
from pygeartrain.planetary import Planetary, PlanetaryGeometry

# Configuration: sun input, carrier output, ring fixed --> gives reduction ratio
KINEMATICS = Planetary('s', 'c', 'r')
ITERATION_ID = "2026-01-15_sun_sweep_5to1"

# Parameters for ~5:1 ratio
# R = S + 2*P (meshing constraint)
# For exact 5:1: R = 4*S, so P = (4S-S)/2 = 1.5*S
CONFIGS = [
    # (R, P, S) - ordered as expected by PlanetaryGeometry
    {"S": 4, "P": 6,  "R": 16, "N": 4, "b": 0.8, "note": "exact 5:1"},
    {"S": 5, "P": 8,  "R": 21, "N": 3, "b": 0.8, "note": "P rounded up, ratio=5.2"},
    {"S": 6, "P": 9,  "R": 24, "N": 3, "b": 0.8, "note": "exact 5:1"},
    {"S": 7, "P": 10, "R": 27, "N": 3, "b": 0.8, "note": "P rounded down, ratio=4.86"},
]

def calculate_ratio(R, S):
    """Calculate actual gear ratio for sun-in, carrier-out, ring-fixed config"""
    return (R + S) / S

def generate_labeled_png(config, output_dir="pngs"):
    """Generate a PNG with labels in filename and on the plot"""
    R, P, S = config["R"], config["P"], config["S"]
    N, b = config["N"], config["b"]

    ratio = calculate_ratio(R, S)

    # Create gear geometry
    gear = PlanetaryGeometry.create(KINEMATICS, (R, P, S), N, b=b)

    # Create figure with room for title
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    # Plot gear at phase 0
    gear._plot(ax, phase=0, col='steelblue')

    ax.set_aspect('equal')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.grid(True, alpha=0.3)

    # Title with all parameters - clear identification
    title = (
        f"{ITERATION_ID}\n"
        f"Sun={S}t | Planet={P}t | Ring={R}t | N={N} planets | b={b}\n"
        f"Ratio = {ratio:.2f}:1 (sun→carrier, ring fixed)"
    )
    ax.set_title(title, fontsize=12, fontweight='bold')

    # Add text annotation in corner with key params
    info_text = f"S={S}, P={P}, R={R}\nN={N}, b={b}\nRatio={ratio:.2f}:1"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # Filename with iteration ID and parameters
    filename = f"{output_dir}/{ITERATION_ID}_S{S}_P{P}_R{R}_N{N}_ratio{ratio:.2f}.png"

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved: {filename}")
    print(f"  Config: R={R}, P={P}, S={S}, N={N}, b={b}")
    print(f"  Actual ratio: {ratio:.3f}:1")
    print(f"  Note: {config['note']}")
    print()

    return filename, ratio

def main():
    print(f"=" * 60)
    print(f"Sun Gear Sweep - Targeting 5:1 Ratio")
    print(f"Iteration: {ITERATION_ID}")
    print(f"Kinematics: {KINEMATICS}")
    print(f"=" * 60)
    print()

    results = []
    for config in CONFIGS:
        try:
            filename, ratio = generate_labeled_png(config)
            results.append({**config, "filename": filename, "actual_ratio": ratio})
        except Exception as e:
            print(f"ERROR with S={config['S']}: {e}")
            results.append({**config, "error": str(e)})

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        if "error" in r:
            print(f"S={r['S']}: FAILED - {r['error']}")
        else:
            print(f"S={r['S']}: R={r['R']}, P={r['P']}, ratio={r['actual_ratio']:.2f}:1 -> {r['filename']}")

    return results

if __name__ == "__main__":
    main()
