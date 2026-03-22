# CATIA Modeling Guide — QDD Gearbox

*Living document. Add to this as you model. Quick reference for "how does this work?" moments.*

---

## Principles

Core rules that keep the assembly clean and maintainable.

### Single Source of Truth
All positioning data lives in the skeleton. Parts don't define their own locations — they read from skeleton geometry.

### Constraint Rule
**Parts constrain to skeleton, never to each other.**

If Part A and Part B need to align, they both reference the same skeleton geometry. This prevents fragile chains where moving one part breaks another.

### B-Rep Free Rule
**Never reference edges or faces of solid bodies.** Sketch on Planes and reference Skeleton wireframes (axes, points, curves) instead. B-Rep (boundary representation) references break when features reorder or geometry regenerates. If you need a position, publish a point or plane from the skeleton — not a face of a pad.

### Clean Publication Rule
Don't publish an entire Sketch. Use `Extract` or `Output Features` to publish only the specific curves/points needed. Other parts should only see the interface, not the internals.

### Pattern Rule
Use the skeleton's center axis for angular patterns. The skeleton publishes the number of instances (e.g., number of planets), and patterns reference that.

**Body-level patterning is more stable than feature-level.** Pattern the entire Body (containing the feature), not the individual Pad/Pocket. Feature-level patterns can break when upstream geometry changes.

### Placeholder Philosophy
Placeholder gears are "geometric contracts" — they define the interface (pitch diameter, position) without the complexity of real tooth geometry. When real gears are ready, they swap in and inherit the same constraints.

---

## Workarounds

CATIA quirks and their solutions. Add new ones as you discover them.

### Sketches Don't Support Circular Patterns
**Problem:** You can't circular-pattern geometry within a sketch in CATIA.

**Solution:** Pattern at the part or assembly level instead. Create the base feature from the sketch, then use Circular Pattern on the resulting geometry.

### Sketch H/V Axis Is Local, Not Global
**Problem:** The H and V axes in the sketcher are arbitrary local axes — they don't necessarily align with the global X, Y, or Z.

**Solution:** Always reference the global X/Y/Z directions explicitly. Use Positioned Sketches (see below) to control orientation.

### Positioned Sketch Setup
**Problem:** Default sketches can end up with unexpected orientation, causing geometry surprises.

**Setup:** Select Positioned Sketch → Origin = Projection Point (select Part Origin) → Orientation = Parallel to Line (select Z-axis as Vertical).

**Rescue:** If an existing sketch has wrong orientation: `Right-click Sketch > Sketch Object > Change Sketch Support` → switch to Positioned and re-define references.

### "Cycle Detected" Error
**Root cause:** Bidirectional loop — Part follows Skeleton (via Paste Link), but Skeleton follows Part (via assembly face/edge constraints).

**Method A (Hard Delete):** Delete face/edge constraints in the assembly. Replace with Plane-to-Plane coincidence constraints.

**Method B (Isolation):** Open Skeleton and Part in *separate windows* with no assembly context open. Perform the Paste Link there — avoids the cycle at paste time.

**Re-lock position safely:** Use Coincidence Constraints between XY, YZ, and ZX planes only — never face references.

**Flipped orientation:** Toggle constraint from "Opposite" to "Same."

---

## Structure (As-Built)

Current assembly organization. Update this as the model evolves.

### Top-Level
```
QDD Master Assem (Top-down) A.1
├── Gearbox_Master_Assem A.1
│   ├── SKL_Skeleton A.1 (SKL_Gearbox.1)    ← master reference, FIXED
│   ├── gear_set A.1                          ← sun, planets, ring gears
│   ├── carrier_assem A.1
│   │   ├── carrier_bottom A.1
│   │   ├── carrier_top A.1
│   │   ├── cutting_bodies A.1                ← shared boolean cutter tool
│   │   └── skeleton_refs A.1                 ← pasted skeleton geometry
│   ├── housing_assem A.1
│   │   ├── housing_body A.1
│   │   ├── housing_lid A.1
│   │   ├── cutting_bodies A.1
│   │   ├── skeleton_ref A.1
│   │   └── 6805-2RS Ball Bearings (×2)
│   └── 6805-2RS Ball Bearings (×2)
├── MotorHousing A.1
│   ├── D6374_150kv A.1
│   ├── Motor_enclosure_cap A.1
│   └── Motor_enclosure_housing A.1
└── Engineering Connections
```

**Reference screenshots:** `docs/images/`
- `full-assembly-cross-section.png` — complete assembly stack, cross-sectioned
- `master-assembly-tree.png` — top-level tree with housing and motor visible
- `carrier-assembly-tree.png` — carrier sub-assembly with cutting_bodies and external refs
- `housing-lid-detail.png` — lid part showing external references from skeleton

### What the Skeleton Publishes
- Number of planets
- Gear sizes (pitch diameters)
- Center axis (for patterns)
- (add more as you build them)

### Key Relationship
Gear set and carrier align because they both reference the same source of truth (skeleton), not because one contains the other. They're parallel branches, both driven by skeleton.

---

*Last updated: Feb 18, 2026*
