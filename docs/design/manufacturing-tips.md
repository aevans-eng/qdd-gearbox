# Manufacturing Tips — QDD Gearbox

Practical tips, lessons learned, and design-for-manufacturing knowledge collected over the project. Useful for documentation, blog posts, and future reference.

**Last updated:** 2026-02-19

---

## Heat-Set Inserts (Brass, FDM)

### Pilot Hole Sizing
- Model the hole at the **insert's OD** (outer diameter from datasheet/package)
- FDM naturally prints holes ~0.1-0.2mm undersized, creating the right interference
- Do NOT use generic "recommended pilot hole" tables from Ruthex/McMaster — those assume injection-molded parts. FDM is different

### Hole Depth
- Make the hole **1.5× the insert length** to give displaced plastic somewhere to go
- Without this extra depth, melted plastic fills the insert's internal threads

| Insert | OD | Length | Pilot Hole Diameter | Pilot Hole Depth |
|--------|-----|--------|-------------------|-----------------|
| M3xL4xOD4.2 | 4.2mm | 4mm | 4.2mm | 6.0mm |
| M4xL4xOD5 | 5.0mm | 4mm | 5.0mm | 6.0mm |

### Installation
- Use a **non-tapered** soldering iron tip (tapered tips get stuck — the insert contracts around the taper as it cools, "Chinese finger trap" effect)
- Heat the insert for 10-15 seconds until ~90% seated
- **Plate-press technique:** Remove iron, flip part onto a flat metal surface (small sheet metal square works), press down gently. This seats the insert flush and consistent without needing precision
- Let cool 6-10 seconds before handling
- **TS100 iron tip kit** available specifically for heat-set inserts (in Aaron's inventory)

### Design Tips
- Use **minimum 4 perimeters** in slicer settings around insert holes (default is usually 2). More walls = better grip, less surface dimpling on the outside
- Optional: add a **45° chamfer** at the top of the hole to contain displaced material and guide the insert
- Insert holes should be vertical (parallel to print Z-axis) for best results — inserting into a side wall works but is harder to keep straight

---

## FDM Tolerancing (General)

### Dimensional Accuracy
- General accuracy: **±0.2mm**
- Bores print **undersized** by ~0.1-0.2mm (model oversized to compensate)
- Shafts print **slightly oversized** (model undersized to compensate)
- Large diameters have more absolute error — scale clearance with feature size

### Fit Strategy for FDM
- **Snug/transition fit:** Model bore +0.10mm over nominal
- **Press fit:** Model at nominal — FDM undersizing does the work
- **Clearance fit:** Model bore +0.2-0.3mm over nominal
- These are starting points — calibration print determines actual offsets for your printer

### Print Orientation Matters
- **Critical bores:** Orient vertically for best roundness (built up layer by layer)
- **Flat surfaces:** Best accuracy on the build plate (first layer)
- **Overhangs:** Avoid unsupported features on critical mating surfaces
- **Gear teeth:** Print flat for consistent tooth geometry across all teeth

### Calibration Print
Before committing to the full build, print a test coupon with representative features:
- Various bore diameters matching your design
- A boss/shaft feature
- Heat-set insert holes
- Measure everything with calipers, calculate offsets, apply to parametric model

---

## Fastener Clearance Holes (ISO 273)

Model clearance holes at the **close fit** value, not the bolt diameter:

| Bolt | Bolt Diameter | Close Fit Hole | Normal Fit Hole |
|------|--------------|----------------|-----------------|
| M2 | 2.0mm | 2.4mm | 2.6mm |
| M2.5 | 2.5mm | 2.9mm | 3.1mm |
| M3 | 3.0mm | 3.4mm | 3.6mm |
| M4 | 4.0mm | 4.5mm | 4.8mm |
| M5 | 5.0mm | 5.5mm | 5.8mm |

For FDM: use close fit values. Holes will print slightly undersized, landing between close and nominal. Drill out if needed.

---

## Shoulder Bolts as Pins

Shoulder bolts can serve as both fastener and precision pin:
- The **shoulder** (unthreaded cylindrical section) acts as the bearing surface / pin
- The **threaded end** clamps parts together
- Shoulder diameter is precision-ground — much more accurate than 3D-printed features
- In the QDD gearbox: D5mm shoulder screws act as planet pins + carrier clamshell fasteners

---

*Add new tips as they come up — from test prints, assembly experience, research, etc.*
