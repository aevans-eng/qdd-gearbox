# QDD Gearbox — Media Next Steps
> Checklist of photos, renders, graphs, and diagrams needed for website, blog post, and portfolio.
> Last updated: 2026-03-15.

---

## Photos To Take

| Shot | Description | Notes |
|---|---|---|
| Hero shot | Assembled Rev 00B, lid on, clean background | Good lighting, slightly angled top-down. This is the portfolio thumbnail. |
| Side profile | Assembled unit showing proportions and height | Neutral background, shows motor interface side |
| Backdriving demo | Hand turning the output shaft | Shows QDD transparency — the whole point of the project |
| Gear mesh close-up | Spur gear tooth engagement detail | Macro or close crop, shows print quality and mesh |
| Motor + gearbox | ODrive + motor + gearbox mounted together | Once integration is done — shows full actuator |
| Rev 00A vs 00B | Side-by-side comparison of both revisions | Highlights visible changes (spur vs herringbone, carrier redesign) |

## CAD Renders To Generate

Can use `/cad-render` skill with STL files in `prototypes/rev00b/prints/`.

| Render | Description | Files Needed |
|---|---|---|
| Exploded view | All Rev 00B components separated along assembly axis | All part STLs |
| Cross-section | Updated cut-away showing internal gear train | Full assembly STL or CATIA export |
| Transparent housing | Housing shown transparent, internals visible | Housing + internals STLs |
| Hero render | Clean product shot of assembled unit | Full assembly STL |
| Before/after | Rev 00A vs 00B renders side-by-side | Both revision assemblies |

## Graphs & Data Visualizations

| Visual | Description | Data Source | When |
|---|---|---|---|
| Backlash measurement | Angular backlash at output vs torque | Rev 00B testing | After Rev 00B test |
| Friction torque comparison | Rev 00A vs 00B friction torque bar chart | T-001 data + Rev 00B retest | After Rev 00B test |
| Efficiency curve | Efficiency vs speed (or vs load) | Motor testing with ODrive | After controls integration |
| Tolerance stack-up | Bearing interface stack-up diagram | Skeleton offset params | Can do now |
| Cost breakdown | BOM cost — pie or horizontal bar | BOM spreadsheet | Can do now |
| Trade study radar | Spider/radar chart of top 3 gear types | Trade study scores | Can do now (nice-to-have) |

## Diagrams

| Diagram | Description | When |
|---|---|---|
| Power flow schematic | Sun → planet → ring gear train schematic | Can do now |
| Skeleton parameter flow | Which skeleton params drive which parts | Can do now |
| Test dependency map | Component → Interface → Subsystem → System | Can do now |
| Assembly sequence | Step-by-step visual assembly guide | After Rev 00B finalized |
| Tolerance chain | Linear tolerance chain through bearing stack | With GD&T section |

## Available Photos (Rev 00B — completed)

Location: `prototypes/rev00b/photos/` (full-res) and `Portfolio/Website/src/qdd-gearbox/images/` (web-optimized)

| File | Description | On Website |
|---|---|---|
| `rev00b-3d-printing.jpg` | Parts on Bambu P1S print bed | Yes |
| `rev00b-parts-laid-out.jpg` | All parts laid out with bearings and hardware | Yes |
| `rev00b-parts-laid-out-no-body.jpg` | Parts laid out, housing body not in view | No (backup) |
| `rev00b-sun-planets-ring-bearings-installed.jpg` | Ring gear with planets and sun, bearings installed | Yes |
| `rev00b-lower-carrier-planets-sun-installed.jpg` | Lower carrier with gear train installed, top-down | Yes |
| `rev00b-lid-off-rest-installed.jpg` | Assembled gearbox with lid removed | Yes |
| `rev00b-testing-with-claude-code.jpg` | Test bench setup with laptop and ODrive | Yes |

## Available Photos (Documentation)

Location: `docs/images/`

| File | Description |
|---|---|
| `rev00a-cross-section.png` | Rev 00A CATIA cross-section (from dropbox) |
| `full-assembly-cross-section.png` | Full assembly cross-section render |
| Various CATIA screenshots | Assembly trees, detail views |

## Priority Order

1. **Hero shot** — needed for portfolio thumbnail, LinkedIn, OG image
2. **Cost breakdown** + **tolerance stack-up** — can generate now, adds substance
3. **CAD renders** — exploded view and cross-section add polish
4. **Backdriving demo** — the money shot for QDD, ideally a short video/GIF
5. **Graphs** — after Rev 00B quantitative testing
