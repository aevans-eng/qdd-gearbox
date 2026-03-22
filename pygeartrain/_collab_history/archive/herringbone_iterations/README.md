# Herringbone Planetary Iterations Archive

This folder contains failed and intermediate attempts at generating correct herringbone planetary gear geometry.

## Summary of Iterations

| Version | Approach | Result | Lesson |
|---------|----------|--------|--------|
| v2 | arrange() pre-positioning | Worse - twist around wrong center | Planets must twist around their own centers |
| v3 | Mesh rotation + standard twist | Sun-planet OK, planet-ring misaligned | Different rotation centers cause drift |
| v4 | Gear ratio twist compensation | Worse | Don't trust theoretical formulas blindly |
| v5 | Same reference radius | Worse | - |
| v6 | 1.37° compensation | Wrong direction | - |
| v7 | Mesh axis alignment | Broke sun-planet | Don't change what's working |
| v8 | 2.74° then 4.11° ring comp | Kept getting worse | - |
| v9 | Sweep approach | Found ~0.34° neighborhood | Use empirical search when theory fails |
| v10 | error/4 formula = 0.341° | Overshot, 0.131° remaining | Formula is approximation |
| v11 | Measured 0.21° | Close, 0.0007° remaining | Measure and iterate |
| v12 | Iterated to 0.21068° | Perfect, 0° offset | Final working value |

## Key Lessons

1. **Isolate changes** - Only modify what's broken
2. **Validate empirically** - Theory gives estimates, measurement gives truth
3. **Use visual sweeps** - When stuck, create parameter sweeps
4. **Understand geometry** - Ring compensation needed because planets orbit at offset
5. **Iterate to precision** - Formula → Measure → Adjust → Repeat

## Final Formula

```
ring_compensation = z × tan(helix) × (1/ring_inner_r - 1/mesh_radius)
```

Gets within ~0.005° of perfect. One iteration of measurement refinement achieves 0°.
