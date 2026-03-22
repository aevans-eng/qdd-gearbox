# 2026-01-15 - Initial Setup & First Gear Preview

## Objective
Get pygeartrain working again and display a gear preview.

## Environment
- Python 3.13.7
- Windows (MSYS)
- numpy 2.3.5 (already installed)
- matplotlib 3.10.8 (already installed)
- scipy 1.17.0 (already installed)

## Dependencies Installed

### From PyPI
- sympy 1.14.0
- shapely 2.1.2
- imageio 2.37.2
- einops 0.8.1
- numpy-indexed 0.3.7
- cached-property 2.0.1
- funcsigs 1.0.2
- fastcache 1.1.0
- pycosat 0.6.6
- mpmath 1.3.0
- future 1.0.0

### From GitHub (installed with --no-deps to avoid numpy version conflicts)
- numga 0.1.0 from https://github.com/eelcohoogendoorn/numga.git
- pycomplex 0.0.0 from https://github.com/eelcohoogendoorn/pycomplex.git

## Issues Encountered

### Issue 1: numga requires numpy < 2.0
The numga package specifies `numpy<2.0,>=1.22` in its dependencies, but we have numpy 2.3.5 installed.

**Solution:** Installed numga with `pip install --no-deps` to bypass the version check.

### Issue 2: numpy 2.x overflow error in numga
When running the gear code, got this error:
```
File "numga\subspace\factory.py", line 50, in order_blades
    blades * -1  # swap sorting order for higher order blades
    ~~~~~~~^~~~
OverflowError: Python integer -1 out of bounds for uint8
```

numpy 2.x has stricter overflow checking. Multiplying a uint8 array by -1 causes an overflow.

**Solution:** Patched `C:\Users\ruzzc\AppData\Local\Programs\Python\Python313\Lib\site-packages\numga\subspace\factory.py`

Changed line 46-51 from:
```python
order = np.where(
    (blades * 2 >= self.algebra.n_dimensions),
    blades,
    blades * -1  # swap sorting order for higher order blades
)
```

To:
```python
order = np.where(
    (blades * 2 >= self.algebra.n_dimensions),
    blades.astype(np.int16),
    blades.astype(np.int16) * -1  # swap sorting order for higher order blades
)
```

## Gear Preview Test

Ran the following test code:
```python
from pygeartrain.planetary import *

kinematics = Planetary('c', 'r', 's')
gear = PlanetaryGeometry.create(kinematics, (14,4,6), 5, b=0.8)
gear.animate()
```

### Parameters Used
- **Gear configuration:** (R=14, P=4, S=6)
  - Ring gear: 14 teeth
  - Planet gears: 4 teeth each
  - Sun gear: 6 teeth
- **Number of planets (N):** 5
- **Tooth profile ratio (b):** 0.8
  - b controls the ratio of epicycloid to hypocycloid in the tooth profile
  - b=0.5 is balanced, b=0.8 is more epicycloidal
- **Kinematic configuration:** ('c', 'r', 's')
  - Input: carrier
  - Output: ring
  - Fixed: sun

### Result
Animation displayed successfully in a matplotlib window. The planetary gear system animated showing the meshing of all gears as the carrier rotates.

### Observations
- matplotlib printed many "Ignoring fixed x limits to fulfill fixed data aspect with adjustable data limits." warnings during animation - these are harmless
- The gear profiles look correct with proper meshing
- 5 planet gears evenly distributed around the carrier

## Files Created
- `pngs/` - folder for saving PNG exports
- `design_log/` - folder for engineering process documentation

## Next Steps
- Experiment with different gear ratios
- Try different b values to see tooth profile changes
- Export static PNGs of interesting configurations
- Test other gear types (cycloid, compound planetary, etc.)
