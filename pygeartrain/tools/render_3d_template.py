"""
render_3d_template.py - Reusable 3D Part Renderer

Creates 3D visualizations from XYZ profile files using matplotlib.
Edit the CONFIGURATION section below for your part.

Usage:
    python render_3d_template.py

Requirements:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Remove this line if you want interactive display
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

# =============================================================================
# CONFIGURATION - Edit this section for your part
# =============================================================================

# Output settings
OUTPUT_DIR = "output_herringbone_v17"  # Folder containing your XYZ files
OUTPUT_FILE = "my_render.png"          # Output image filename
DPI = 200                               # Image resolution

# Figure settings
FIGURE_SIZE = (14, 10)                  # (width, height) in inches
TITLE = "My 3D Part Render"             # Plot title
BACKGROUND_COLOR = 'white'              # Background color

# View angle (camera position)
# elev: elevation angle (0=side, 90=top-down)
# azim: azimuth angle (rotation around Z axis)
VIEW_ELEV = 25                          # Try: 25 (isometric), 90 (top), 0 (side)
VIEW_AZIM = 45                          # Try: 45 (corner), 0 (front), 90 (side)

# Axis limits (set to None for auto)
X_LIMITS = (-45, 45)                    # (min, max) or None
Y_LIMITS = (-45, 45)                    # (min, max) or None
Z_LIMITS = (-15, 15)                    # (min, max) or None

# Define your parts here
# Each part needs: name, list of Z-level files (bottom to top), color, alpha
PARTS = [
    {
        "name": "Sun Gear",
        "files": [
            "sun_12_z_neg.txt",         # Bottom profile
            "sun_12_z0.txt",            # Middle profile
            "sun_12_z_pos.txt",         # Top profile
        ],
        "color": "red",
        "alpha": 0.9,
        "edge_color": "darkred",
        "edge_width": 2,
    },
    {
        "name": "Planet 0",
        "files": [
            "planet_18_0_z_neg.txt",
            "planet_18_0_z0.txt",
            "planet_18_0_z_pos.txt",
        ],
        "color": "green",
        "alpha": 0.8,
        "edge_color": "darkgreen",
        "edge_width": 1.5,
    },
    {
        "name": "Planet 1",
        "files": [
            "planet_18_1_z_neg.txt",
            "planet_18_1_z0.txt",
            "planet_18_1_z_pos.txt",
        ],
        "color": "green",
        "alpha": 0.8,
        "edge_color": "darkgreen",
        "edge_width": 1.5,
    },
    {
        "name": "Planet 2",
        "files": [
            "planet_18_2_z_neg.txt",
            "planet_18_2_z0.txt",
            "planet_18_2_z_pos.txt",
        ],
        "color": "green",
        "alpha": 0.8,
        "edge_color": "darkgreen",
        "edge_width": 1.5,
    },
    {
        "name": "Ring Gear",
        "files": [
            "ring_48_z_neg.txt",
            "ring_48_z0.txt",
            "ring_48_z_pos.txt",
        ],
        "color": "blue",
        "alpha": 0.4,                   # Lower alpha to see through
        "edge_color": "darkblue",
        "edge_width": 1,
    },
]

# =============================================================================
# RENDERING CODE - You shouldn't need to edit below this line
# =============================================================================

def load_profile(filepath):
    """Load XYZ points from a text file."""
    return np.loadtxt(filepath)


def create_surface_mesh(bottom, top, color, alpha=0.7):
    """Create a surface mesh between two profile curves."""
    verts = []
    n = min(len(bottom), len(top))
    for i in range(n):
        i_next = (i + 1) % n
        quad = [
            bottom[i],
            bottom[i_next],
            top[i_next],
            top[i]
        ]
        verts.append(quad)
    return Poly3DCollection(verts, alpha=alpha, facecolor=color, edgecolor='none')


def render_parts():
    """Main rendering function."""
    
    fig = plt.figure(figsize=FIGURE_SIZE)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(BACKGROUND_COLOR)
    
    # Render each part
    for part in PARTS:
        print(f"Rendering: {part['name']}")
        
        # Load all Z-level profiles
        profiles = []
        for filename in part["files"]:
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                profiles.append(load_profile(filepath))
            else:
                print(f"  Warning: File not found: {filepath}")
        
        if len(profiles) < 2:
            print(f"  Skipping {part['name']} - need at least 2 profiles")
            continue
        
        # Create surfaces between consecutive profiles
        for i in range(len(profiles) - 1):
            surface = create_surface_mesh(
                profiles[i], 
                profiles[i + 1], 
                part["color"], 
                part["alpha"]
            )
            ax.add_collection3d(surface)
        
        # Draw edge lines on top profile for definition
        top_profile = profiles[-1]
        ax.plot(
            top_profile[:, 0], 
            top_profile[:, 1], 
            top_profile[:, 2],
            color=part.get("edge_color", part["color"]),
            linewidth=part.get("edge_width", 1)
        )
    
    # Set axis properties
    if X_LIMITS:
        ax.set_xlim(X_LIMITS)
    if Y_LIMITS:
        ax.set_ylim(Y_LIMITS)
    if Z_LIMITS:
        ax.set_zlim(Z_LIMITS)
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(TITLE, fontsize=14, fontweight='bold')
    
    # Set view angle
    ax.view_init(elev=VIEW_ELEV, azim=VIEW_AZIM)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', facecolor=BACKGROUND_COLOR)
    print(f"\nSaved: {output_path}")
    
    # Uncomment to show interactive window (remove matplotlib.use('Agg') above)
    # plt.show()


if __name__ == "__main__":
    print("=" * 50)
    print("3D Part Renderer")
    print("=" * 50)
    render_parts()
    print("Done!")
