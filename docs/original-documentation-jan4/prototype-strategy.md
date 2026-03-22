# Initial Prototype Strategy

## 3D Modeling/Design Strategy
- Master assembly designed to be modular with different gearing layouts, minimizing time for design iterations
- Sun, planet, and ring gears are all interlinked, and should be independent systems
- Carrier should be parametric with the gear systems to always be compatible
- Possibly develop automated workflow for different gear designs
- Sun, planet, and ring to be printed together
- Ring gear should be modular from gearbox housing — easily swappable especially for prototyping
- Housing may need to be two parts as ring gear needs to be installed into housing, and carrier needs to be under planets
- Housing needs to be relatively stiff

## Assembly Stack (Bottom → Top)
1. Bottom housing face
2. Housing bottom carrier bearing
3. Bottom carrier plate
4. Sun gear on shaft, planet gears aligning with bottom carrier plate and pins, ring gear slides into housing
   - Planet gears
5. Top carrier plate
6. Ring gear locking feature
7. Lid top carrier bearing
8. Lid

## Design Notes
- Further analysis required about the effects of how the tendency of designing around the self-centering tendency of the floating carrier/planets affects the bearings which constrain the carrier concentrically, but also axially through friction (extra bearing wear, gear wear, etc)
- Hand calcs needed on the output of the carrier — for the torque output to be produced, what resultant force will the connection (e.g. heatserts) need to endure, crushing of material, ripping out of heatserts is a possibility. Can be mitigated through increased diameter of output shaft.
- For MVP: using identical top and bottom main bearings, output shaft constrained to the ID of the top main bearing. For simplicity and prevention of prototype scope creep.
