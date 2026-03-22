"""
render_gearbox_blender.py - Caden Kraft style render

Matte black with soft studio lighting on neutral gray gradient.
Based on Product Render Style Guide.
"""

import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
INPUT_STL = os.path.join(SCRIPT_DIR, "step_output_v19", "gearbox_assembled.stl")
OUTPUT_PNG = os.path.join(SCRIPT_DIR, "step_output_v19", "render_red_matte.png")

BLENDER_SCRIPT = '''
import bpy
import sys
import math

argv = sys.argv[sys.argv.index("--") + 1:]
input_file = argv[0]
output_file = argv[1]

print(f"Input: {input_file}")
print(f"Output: {output_file}")

# === CLEAR SCENE ===
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for block in bpy.data.meshes:
    bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    bpy.data.materials.remove(block)

# === IMPORT STL ===
print("Importing STL...")
bpy.ops.wm.stl_import(filepath=input_file)

obj = None
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        obj = o
        break

if obj is None:
    print("Error: No mesh found")
    sys.exit(1)

print(f"Imported: {obj.name} ({len(obj.data.polygons)} faces)")

# Smooth shading
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()

# === MATERIAL (Caden Kraft style - matte dark with slight sheen) ===
print("Applying material...")
mat = bpy.data.materials.new(name="RedMattePlastic")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.4, 0.03, 0.03, 1)  # Deep dark red
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.6  # More matte
    # Specular input name varies by Blender version
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.5

obj.data.materials.clear()
obj.data.materials.append(mat)

# === GET BOUNDS ===
verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
min_co = type(verts[0])((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
max_co = type(verts[0])((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
center = (min_co + max_co) / 2
size = (max_co - min_co).length

print(f"Part size: {size:.1f}mm")

# === GROUND PLANE (Shadow Catcher) ===
print("Adding shadow catcher...")
bpy.ops.mesh.primitive_plane_add(
    size=size * 10,
    location=(center.x, center.y, min_co.z - 0.01)
)
ground = bpy.context.active_object
ground.name = "ShadowCatcher"
ground.is_shadow_catcher = True

# === 3-POINT LIGHTING (Soft, Caden Kraft style) ===
print("Setting up lighting...")

# Key light - 45° above, 45° left, large and soft
bpy.ops.object.light_add(type='AREA', location=(
    center.x + size * 1.5,
    center.y - size * 1.5,
    center.z + size * 2
))
key = bpy.context.active_object
key.name = "KeyLight"
key.data.energy = 1000
key.data.size = size * 2.5
key.rotation_euler = (math.radians(45), math.radians(15), math.radians(45))

# Fill light - opposite side, 30% of key
bpy.ops.object.light_add(type='AREA', location=(
    center.x - size * 1.2,
    center.y + size * 0.8,
    center.z + size * 1.2
))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 300
fill.data.size = size * 3

# Rim light - behind, subtle edge definition
bpy.ops.object.light_add(type='AREA', location=(
    center.x - size * 0.5,
    center.y + size * 2,
    center.z + size * 1.5
))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 400
rim.data.size = size

# === BACKGROUND (Neutral gray gradient) ===
print("Setting up background...")
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True

nodes = world.node_tree.nodes
links = world.node_tree.links
for node in nodes:
    nodes.remove(node)

output = nodes.new('ShaderNodeOutputWorld')
output.location = (300, 0)

bg = nodes.new('ShaderNodeBackground')
bg.location = (0, 0)
bg.inputs['Color'].default_value = (0.78, 0.8, 0.82, 1)  # Neutral gray with slight blue
bg.inputs['Strength'].default_value = 1.0

links.new(bg.outputs['Background'], output.inputs['Surface'])

# === CAMERA (3/4 angle, long focal length) ===
print("Setting up camera...")
dist = size * 2.8
angle_h = math.radians(40)
angle_v = math.radians(50)  # Higher angle - more top-down

cam_x = center.x + dist * math.cos(angle_h) * math.cos(angle_v)
cam_y = center.y - dist * math.sin(angle_h) * math.cos(angle_v)
cam_z = center.z + dist * math.sin(angle_v)

bpy.ops.object.camera_add(location=(cam_x, cam_y, cam_z))
camera = bpy.context.active_object
camera.name = "ProductCamera"

direction = center - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
camera.data.lens = 85  # Long focal length, minimal distortion

bpy.context.scene.camera = camera

# === RENDER SETTINGS ===
print("Configuring render...")
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True

scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = True

# Try GPU
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for device_type in ['OPTIX', 'CUDA', 'HIP']:
        try:
            prefs.compute_device_type = device_type
            prefs.get_devices()
            for device in prefs.devices:
                device.use = True
            scene.cycles.device = 'GPU'
            print(f"Using GPU ({device_type})")
            break
        except:
            continue
except:
    scene.cycles.device = 'CPU'
    print("Using CPU")

# === RENDER ===
print("Rendering...")
scene.render.filepath = output_file
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
bpy.ops.render.render(write_still=True)
print(f"Saved: {output_file}")
'''

def main():
    print("=" * 50)
    print("Caden Kraft Style Render")
    print("=" * 50)

    if not os.path.exists(INPUT_STL):
        print(f"Error: Input file not found: {INPUT_STL}")
        return

    if not os.path.exists(BLENDER_PATH):
        print(f"Error: Blender not found: {BLENDER_PATH}")
        return

    # Write temp script
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(BLENDER_SCRIPT)
        script_path = f.name

    cmd = [
        BLENDER_PATH,
        "--background",
        "--python", script_path,
        "--",
        INPUT_STL,
        OUTPUT_PNG
    ]

    print(f"\nRendering with Blender...")
    print(f"Input: {INPUT_STL}")
    print(f"Output: {OUTPUT_PNG}\n")

    result = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(script_path)

    if "Saved:" in result.stdout:
        print("\n" + "=" * 50)
        print(f"Done! Saved: {OUTPUT_PNG}")
        print("=" * 50)
    else:
        print("Blender output:")
        print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
        if result.stderr:
            print("\nErrors:")
            print(result.stderr[-1000:])

if __name__ == "__main__":
    main()
