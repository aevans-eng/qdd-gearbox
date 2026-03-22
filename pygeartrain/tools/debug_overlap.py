"""
Debug tool to visualize gear overlaps and understand what's happening
"""

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from pygeartrain.planetary import Planetary, PlanetaryGeometry


def debug_config(S, P, R, N, b=0.8, phase=0):
    """Debug a single configuration visually."""
    print(f"\n{'='*60}")
    print(f"Debugging S={S}, P={P}, R={R}, N={N}, b={b}, phase={phase}")
    print(f"{'='*60}")

    kinematics = Planetary('s', 'c', 'r')
    gear = PlanetaryGeometry.create(kinematics, (R, P, S), N, b=b)

    # Get profiles
    profiles = gear.arrange(phase)
    ring_profile, planet_profiles, sun_profile, carrier_profile = profiles

    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot 1: Full assembly
    ax1 = axes[0]
    ax1.set_title(f"Full Assembly\nS={S}, P={P}, R={R}, N={N}")

    # Plot ring
    ring_v = ring_profile.vertices
    ax1.plot(ring_v[:, 0], ring_v[:, 1], 'b-', linewidth=0.5, label='ring')

    # Plot sun
    sun_v = sun_profile.vertices
    ax1.plot(sun_v[:, 0], sun_v[:, 1], 'g-', linewidth=1, label='sun')

    # Plot planets in different colors
    colors = ['r', 'm', 'orange', 'brown', 'pink']
    for i, planet in enumerate(planet_profiles):
        pv = planet.vertices
        ax1.plot(pv[:, 0], pv[:, 1], color=colors[i % len(colors)],
                linewidth=1, label=f'planet_{i}')

    ax1.set_aspect('equal')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Zoom on center (sun-planet meshing)
    ax2 = axes[1]
    ax2.set_title("Zoom: Sun-Planet Meshing")

    sun_v = sun_profile.vertices
    ax2.fill(sun_v[:, 0], sun_v[:, 1], 'lightgreen', alpha=0.5, edgecolor='green', linewidth=1)

    for i, planet in enumerate(planet_profiles):
        pv = planet.vertices
        ax2.fill(pv[:, 0], pv[:, 1], alpha=0.3, edgecolor=colors[i % len(colors)], linewidth=1)

    # Calculate zoom extent based on sun and first planet
    sun_max = np.max(np.abs(sun_v))
    ax2.set_xlim(-sun_max * 2, sun_max * 2)
    ax2.set_ylim(-sun_max * 2, sun_max * 2)
    ax2.set_aspect('equal')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Planet-to-planet check
    ax3 = axes[2]
    ax3.set_title("Planet-to-Planet Overlap Check")

    # Convert planets to shapely polygons and check intersection
    planet_polys = []
    for i, planet in enumerate(planet_profiles):
        pv = planet.vertices
        if not np.allclose(pv[0], pv[-1]):
            pv = np.vstack([pv, pv[0]])
        try:
            poly = Polygon(pv)
            if not poly.is_valid:
                poly = poly.buffer(0)
            planet_polys.append(poly)

            # Plot the polygon
            x, y = poly.exterior.xy
            ax3.fill(x, y, alpha=0.3, edgecolor=colors[i % len(colors)], linewidth=1,
                    label=f'planet_{i} (area={poly.area:.4f})')
        except Exception as e:
            print(f"  Error creating polygon for planet {i}: {e}")

    # Check intersections
    print("\nPlanet-to-Planet Intersection Check:")
    for i in range(len(planet_polys)):
        for j in range(i + 1, len(planet_polys)):
            try:
                intersection = planet_polys[i].intersection(planet_polys[j])
                if not intersection.is_empty:
                    area = intersection.area
                    smaller = min(planet_polys[i].area, planet_polys[j].area)
                    pct = (area / smaller) * 100 if smaller > 0 else 0
                    print(f"  Planet {i} vs Planet {j}: intersection_area={area:.6f} ({pct:.2f}%)")

                    # Plot intersection
                    if intersection.geom_type == 'Polygon':
                        x, y = intersection.exterior.xy
                        ax3.fill(x, y, 'red', alpha=0.8, edgecolor='darkred', linewidth=2)
                    elif intersection.geom_type == 'MultiPolygon':
                        for geom in intersection.geoms:
                            x, y = geom.exterior.xy
                            ax3.fill(x, y, 'red', alpha=0.8, edgecolor='darkred', linewidth=2)
                else:
                    print(f"  Planet {i} vs Planet {j}: NO INTERSECTION")
            except Exception as e:
                print(f"  Planet {i} vs Planet {j}: ERROR - {e}")

    ax3.set_aspect('equal')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Also check sun-planet intersections
    print("\nSun-Planet Intersection Check:")
    sun_v = sun_profile.vertices
    if not np.allclose(sun_v[0], sun_v[-1]):
        sun_v = np.vstack([sun_v, sun_v[0]])
    try:
        sun_poly = Polygon(sun_v)
        if not sun_poly.is_valid:
            sun_poly = sun_poly.buffer(0)
        print(f"  Sun polygon area: {sun_poly.area:.4f}")

        for i, planet_poly in enumerate(planet_polys):
            intersection = sun_poly.intersection(planet_poly)
            if not intersection.is_empty:
                area = intersection.area
                smaller = min(sun_poly.area, planet_poly.area)
                pct = (area / smaller) * 100 if smaller > 0 else 0
                print(f"  Sun vs Planet {i}: intersection_area={area:.6f} ({pct:.2f}%)")
                if pct > 1:
                    print(f"    *** SIGNIFICANT OVERLAP DETECTED ***")
            else:
                print(f"  Sun vs Planet {i}: NO INTERSECTION")
    except Exception as e:
        print(f"  Error checking sun: {e}")

    plt.tight_layout()
    filename = f"design_log/debug_S{S}_P{P}_R{R}_N{N}.png"
    plt.savefig(filename, dpi=150)
    plt.close()
    print(f"\nSaved: {filename}")

    return filename


if __name__ == "__main__":
    # Debug the v2 configs
    configs = [
        (4, 6, 16, 3, 0.8),
        (5, 8, 21, 3, 0.8),
        (6, 9, 24, 3, 0.8),
        (7, 10, 27, 3, 0.8),
    ]

    for S, P, R, N, b in configs:
        debug_config(S, P, R, N, b, phase=0)
