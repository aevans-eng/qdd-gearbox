# CATIA Skeleton-Driven Assembly Workflow

Quick reference for skeleton-driven design patterns in CATIA. These are mini-workflows Aaron keeps forgetting.

---

## Importing Skeleton Geometry into Sub-Assemblies

**Problem:** Can't paste external references directly into a Product — must go into a Part.

**Solution — Reference Geometry Part:**
1. Create an empty Part in your sub-assembly (e.g., `CarrierSkeletonRef`)
2. Paste all published skeleton geometry (axis systems, planes) into this part
3. Other parts in the assembly reference this part
4. Keeps skeleton references separate from actual geometry

---

## Sub-Assembly Positioning (Datum Strategy)

**Problem:** Which part is the "master" that everything else references?

**Workflow:**
1. **Fix the skeleton ref part first** — This is your local datum. Everything else positions relative to it.
2. **Mate each part individually** to the skeleton ref planes (not to each other when possible)
3. **Never manually drag parts** — Position flows from constraints only

**Why this matters:**
- If you drag a constrained part, you break constraints and features
- Skeleton-driven = you don't position things manually, ever
- To move something, update the skeleton → everything downstream updates

---

## Handling Planet-Centered Features (Non-Axisymmetric)

**Problem:** Bearing pockets are centered on planet axes, not gearbox axis. Revolve cuts don't work.

**Solution — Two-Body Circular Pattern:**
1. **Body A (Remove):** Model one bearing pocket/bore at one planet location
2. **Body B (Add):** Model any raised shoulders/features at one planet location
3. **Circular pattern both** around the main gearbox axis (N = number of planets)
4. Boolean subtract Body A, Boolean add Body B

**Advanced — "Shared Tool" / Master Cutter workflow:**

For complex cutouts that repeat across multiple parts (e.g., bearing pockets in both carrier halves), use a dedicated `cutting_bodies` tool part:

1. Create a dedicated Part in the assembly (e.g., `cutting_bodies A.1`)
2. Import skeleton geometry into it (planet positions, bore diameters)
3. Pad the cutter shape at one planet location
4. **Circular Pattern the Body** (not the feature — more stable)
5. Publish the patterned Body
6. In each target part: Paste Link the cutter Body → Boolean Remove from PartBody

**Chain of Zeros:** The tool part's local origin must match the Skeleton's functional center (e.g., Gear Midplane). If origins are misaligned, cutters land at the wrong position. This is visible in the carrier assembly — see `cutting_bodies A.1` in the part tree.

---

## Fixing Plane Offset Issues

**Problem:** Published planes from skeleton paste in at weird offsets.

**Root cause:** "As Result" geometry is absolute in world space. If your Part's origin and the Skeleton's functional center are at different positions, pasted geometry lands with an offset equal to that difference. Mating to the **Gear Midplane** (not the Bottom Datum) aligns both coordinate "universes" at the functional center.

**Fix:**
1. Publish the **axis system** from skeleton (not just planes) — use the functional gearbox center axis
2. Paste axis system into your skeleton ref part
3. Constrain your assembly parts to this axis system **first**
4. Now paste planes — they share the same coordinate context, no offset

**Safe pasting:** Always copy/paste in separate windows (no assembly context open) to avoid creating accidental cycles. See "Cycle Detected" in the modeling guide.

---

## Snap to Assembly Origin

The assembly origin is invisible by default. The skeleton makes it visible/usable.

**Two methods to snap a part to origin:**
- **Method A:** Compass right-click on the red/white square
- **Method B:** Action Bar > Assembly > Manipulation > Snap to Origin

**Chain of Zeros (positioning hierarchy):**
1. Snap Master Skeleton to (0,0,0)
2. Constrain Sub-Assembly to Skeleton Midplane
3. Constrain Parts to Sub-Assembly Origin

This ensures all coordinate systems are aligned and geometry pastes without offsets.

---

## Golden Rules

- Skeleton ref part = always FIXED
- Never drag parts manually
- Features update when skeleton updates (that's the point)
- If something breaks, check if you accidentally moved a constrained part
