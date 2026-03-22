# CATIA Skeleton — Auto-Captured Notes

*Notes captured from conversation. Raw details to be compiled into formal documentation later.*

---

## Assembly Structure (Feb 14, 2026)

**Top-level:** Gearbox master assembly

**Siblings at gearbox level:**
- Gear set (part file)
- Carrier assembly

**These don't nest** — they're parallel branches, both driven by skeleton.

---

## Skeleton-Driven Approach

**Skeleton publishes variables:**
- Number of planets
- Gear sizes (pitch diameters?)
- (other parameters TBD)

**Carrier consumes skeleton parameters:**
- Carrier is a "body assembly" with sketches
- Sketches are parametrically driven by published variables from skeleton
- Carrier geometry (pin positions, etc.) derives from these parameters

**Gear set:**
- Currently: single part file with sun, planets, ring as simplified cylinders (pitch diameter placeholders)
- Future: imported file with all gears together (real tooth geometry)
- Will also reference skeleton parameters

---

## Key Insight

Gear set and carrier align because they both reference the same source of truth (skeleton), not because one contains the other.

---

*Add more notes below as conversation continues...*
