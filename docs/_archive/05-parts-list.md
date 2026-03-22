# QDD Actuator — Parts List / BOM

## Electronics

| Component | Part Number | Qty | Est. Cost (CAD) | Notes |
|-----------|-------------|-----|-----------------|-------|
| BLDC Motor | TBD — confirm model | 1 | — | On hand |
| Magnetic Encoder | AS5047P (or AS5048A) | 1 | — | On hand; 14-bit, SPI interface |
| Motor Controller | ODrive v3.6 (or S1) | 1 | — | On hand; FOC control |
| Power Supply | 24V DC, ≥10A | 1 | — | On hand |
| Diametric Magnet | 6×2.5 mm | 1 | ~$2 | For encoder, epoxied to shaft |

## Bearings

| Bearing | Size | Qty | Est. Cost (CAD) | Notes |
|---------|------|-----|-----------------|-------|
| 6805 2RS | 25×37×7 mm | 10 | ~$15 | ABEC-1, metric thin section |
| Deep groove ball | 5×14×5 mm (685ZZ) | 10 | ~$8 | Planet gear shafts |
| Deep groove ball | 3×7×3 mm (683ZZ) | 10 | ~$6 | Carrier pin bearings |
| 6710ZZ / 6710-2RS | 50×62×6 mm | 2 | ~$12 | NBZH ultra-thin, output bearing |

## Fasteners & Hardware

| Component | Size | Qty | Est. Cost (CAD) | Notes |
|-----------|------|-----|-----------------|-------|
| Socket head cap screw | M3×10 mm | 12 | ~$3 | Housing assembly |
| Socket head cap screw | M3×16 mm | 8 | ~$2 | Motor mount |
| Socket head cap screw | M4×12 mm | 6 | ~$2 | Lid / output coupling |
| Heat-set threaded insert | M3×5×4 mm | 20 | ~$5 | For 3D-printed bosses |
| Heat-set threaded insert | M4×6×5 mm | 6 | ~$3 | Output interface |
| Dowel pin | 3×12 mm | 3 | ~$2 | Planet carrier alignment |
| Retaining ring (E-clip) | 3 mm shaft | 6 | ~$1 | Planet pin retention |

## 3D Printing Materials

| Material | Type | Qty (est.) | Est. Cost (CAD) | Notes |
|----------|------|------------|-----------------|-------|
| PLA+ or PETG | 1.75 mm FDM filament | ~200 g | ~$5 | Housing, lid, carrier |
| Nylon (PA6/PA12) | 1.75 mm FDM filament | ~100 g | ~$8 | Gears (if strength needed) |

## Lubrication

| Product | Qty | Est. Cost (CAD) | Notes |
|---------|-----|-----------------|-------|
| White lithium grease | 1 tube | ~$5 | Gear mesh, bearing repack |

## Cost Summary

| Category | Est. Cost (CAD) |
|----------|-----------------|
| Electronics | On hand ($0) |
| Bearings | ~$41 |
| Fasteners & Hardware | ~$16 |
| 3D Printing | ~$13 |
| Lubrication | ~$5 |
| **Total** | **~$75** |
| **Budget** | **$120** |
| **Margin** | **~$45** |

## Sourcing Notes

- Electronics are on hand — confirm exact part numbers and update this table
- Bearings sourced from AliExpress / Amazon Canada — verify lead times
- Heat-set inserts: McMaster-Carr or Amazon (Ruthex brand recommended)
- Budget constraint: under $120 CAD total — currently well within budget

## TODO

- [ ] Confirm exact motor model and KV rating
- [ ] Confirm ODrive version (v3.6 vs S1)
- [ ] Confirm encoder model (AS5047P vs AS5048A)
- [ ] Finalize filament choice after gear tooth stress analysis
- [ ] Add actual purchase links / order numbers once sourced
