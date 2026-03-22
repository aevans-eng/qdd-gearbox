# STEP File Generation Experiment

This experiment converts XYZ gear profile points to STEP solid files using CadQuery.

## Results Summary

### File Size Comparison

| Gear | XYZ Files (total) | STEP File | Ratio |
|------|-------------------|-----------|-------|
| Sun | 20.9 KB (3 Z-levels) | 130.6 KB | 6.3x larger |
| Planet | 31.8 KB (3 Z-levels) | 192.8 KB | 6.1x larger |
| Ring | 87.1 KB (3 Z-levels) | 504.9 KB | 5.8x larger |

STEP files are larger because they contain:
- Full solid geometry (not just profiles)
- NURBS curve definitions (mathematically precise)
- B-Rep topology data

### Verification Results

All checks **PASSED**:
- Bounding box dimensions match expected values
- Ring gear: 70.02mm diameter (expected: 70mm)
- Gear thickness: 10.00mm (expected: 10mm)
- Solids are valid with proper top/bottom faces
- Geometry is symmetric about Z=0

### Visual Comparison

Side-by-side comparisons in `output/renders/` show:
- Original XYZ profiles (left) vs STEP tessellation (right)
- Tooth profiles are accurately captured
- 4-tooth sun, 6-tooth planet, 16-tooth ring all correct

## Import into 3DEXPERIENCE

### STEP Method (Recommended)
1. **File > Import > 3D Part**
2. Select `.step` file
3. Done - solid geometry imports directly

Advantages:
- One-click import
- Geometry is already a solid
- No manual lofting required
- Preserves smooth curves (NURBS)

### XYZ Method (Manual)
1. Import curves from 3 Z-level files
2. Use Loft operation to create solid
3. Requires careful profile alignment

## Files

```
step_experiment/
├── generate_step.py      # Main generator script
├── verify_step.py        # Automated verification
├── visual_compare.py     # Visual comparison tool
├── requirements.txt      # Dependencies
└── output/
    ├── sun.step          # Sun gear solid
    ├── planet.step       # Planet gear solid
    ├── ring.step         # Ring gear solid
    ├── verification_report.txt
    └── renders/
        ├── sun_comparison.png
        ├── planet_comparison.png
        └── ring_comparison.png
```

## Dependencies

- cadquery (v2.6.1)
- cadquery-ocp (OpenCASCADE bindings)
- numpy
- matplotlib (for visualization)

Install with:
```bash
pip install cadquery numpy matplotlib
```

## Verification Approach

1. **Geometric verification**: Automated checks on bounding box, thickness, face count
2. **Visual verification**: Side-by-side profile comparison
3. **Re-import test**: Load STEP back into CadQuery, extract geometry
4. **External validation**: Open in 3DEXPERIENCE or online viewer (3dviewer.net)

## Limitations Found

1. **Tessellation resolution**: The spline approximation uses CadQuery's default tolerance. Very fine details might lose some precision.

2. **Ring gear**: Currently exports as a solid disc with gear profile. For a true ring gear, you'd need to:
   - Create the outer profile
   - Boolean subtract the inner bore

3. **Assembly**: Planet gears need to be patterned manually in CAD (use planet_centers.txt for positions)

## How Verification Works

The verification script:
1. Loads each STEP file back into CadQuery
2. Extracts bounding box dimensions
3. Compares against expected values from gearset_info.txt
4. Tessellates the top face and extracts boundary points
5. Creates visual comparison with original XYZ data
