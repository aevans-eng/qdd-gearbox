"""
render_gearbox_v19.py - Render assembled gearbox with matte plastic materials

Based on CLI3DPart render workflow, adapted for planetary gearbox.
"""

import pyvista as pv
import os

# Input/Output
INPUT_DIR = "step_output_v19"
OUTPUT_FILE = os.path.join(INPUT_DIR, "render_matte_plastic.png")

# Matte plastic materials
MATERIALS = {
    "sun": {
        "color": "#e63946",  # Red
        "metallic": 0.0,
        "roughness": 0.7,
        "specular": 0.2,
    },
    "planet": {
        "color": "#2a9d8f",  # Teal/Green
        "metallic": 0.0,
        "roughness": 0.7,
        "specular": 0.2,
    },
    "ring": {
        "color": "#457b9d",  # Blue
        "metallic": 0.0,
        "roughness": 0.7,
        "specular": 0.2,
    },
}

print("=" * 50)
print("Gearbox Renderer - Matte Plastic")
print("=" * 50)

# Create plotter
p = pv.Plotter(window_size=(1920, 1080), off_screen=True)

# Light background (like product photography)
p.set_background("#f0f0f0", top="#e0e0e5")

# Load and add each part
print("\nLoading meshes...")

# Sun gear
sun_path = os.path.join(INPUT_DIR, "sun.stl")
if os.path.exists(sun_path):
    sun = pv.read(sun_path)
    p.add_mesh(
        sun,
        color=MATERIALS["sun"]["color"],
        pbr=True,
        metallic=MATERIALS["sun"]["metallic"],
        roughness=MATERIALS["sun"]["roughness"],
        specular=MATERIALS["sun"]["specular"],
        smooth_shading=True,
    )
    print(f"  Added sun ({sun.n_cells} faces)")

# Planet gears
for i in range(3):
    planet_path = os.path.join(INPUT_DIR, f"planet_{i}.stl")
    if os.path.exists(planet_path):
        planet = pv.read(planet_path)
        p.add_mesh(
            planet,
            color=MATERIALS["planet"]["color"],
            pbr=True,
            metallic=MATERIALS["planet"]["metallic"],
            roughness=MATERIALS["planet"]["roughness"],
            specular=MATERIALS["planet"]["specular"],
            smooth_shading=True,
        )
        print(f"  Added planet_{i} ({planet.n_cells} faces)")

# Ring gear
ring_path = os.path.join(INPUT_DIR, "ring.stl")
if os.path.exists(ring_path):
    ring = pv.read(ring_path)
    p.add_mesh(
        ring,
        color=MATERIALS["ring"]["color"],
        pbr=True,
        metallic=MATERIALS["ring"]["metallic"],
        roughness=MATERIALS["ring"]["roughness"],
        specular=MATERIALS["ring"]["specular"],
        smooth_shading=True,
        opacity=0.85,  # Slight transparency to see internals
    )
    print(f"  Added ring ({ring.n_cells} faces)")

# Lighting
print("\nSetting up lighting...")
p.add_light(pv.Light(position=(150, 150, 100), intensity=0.9))   # Key light
p.add_light(pv.Light(position=(-100, -50, 80), intensity=0.4))   # Fill light
p.add_light(pv.Light(position=(0, 0, -100), intensity=0.2))      # Back light

# Camera setup - isometric view
p.view_isometric()
p.camera.zoom(1.4)

# Add title
p.add_text(
    "v19 Herringbone Planetary Gearbox\nR48/P18/S12 | 80mm | 5:1 Ratio | 0.2mm Clearance",
    position="upper_left",
    font_size=12,
    color="#333333"
)

# Render
print(f"\nRendering to {OUTPUT_FILE}...")
p.screenshot(OUTPUT_FILE)
p.close()

print(f"Done! Saved: {OUTPUT_FILE}")
