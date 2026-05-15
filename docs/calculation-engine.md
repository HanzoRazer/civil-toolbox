# Calculation Engine

The Civil Toolbox calculation engine provides hydrology calculators for drainage analysis. All calculators are stateless classes with static methods.

## Unit Conventions

**IMPORTANT**: Different calculators return time in different units:

| Calculator | Method | Returns |
|------------|--------|---------|
| `TimeOfConcentration` | `kirpich()`, `kerby()`, `nrcs_lag()` | **MINUTES** |
| `KinematicWave` | `sheet_flow_time()` | **HOURS** |

Primary units are US customary (feet, inches, acres, cfs). Metric convenience methods are available where applicable.

## Calculators

### RationalMethod

Estimates peak runoff rate for small drainage areas (< 200 acres).

**Formula**: `Q = C × i × A`

```python
from civil_toolbox.calculators import RationalMethod

result = RationalMethod.calculate(
    runoff_coefficient=0.45,      # dimensionless (0-1)
    rainfall_intensity_in_per_hr=5.5,  # inches/hour
    area_acres=25.0,              # acres
)
print(f"Peak runoff: {result.peak_runoff_cfs:.2f} cfs")
```

**Methods**:
- `calculate()` - US customary units, returns cfs
- `calculate_metric()` - SI units, returns m³/s
- `calculate_composite()` - area-weighted C for multiple land uses

### TR55

Calculates runoff depth using the NRCS curve number method.

**Formula**: `Q = (P - Ia)² / (P - Ia + S)` where `S = (1000/CN) - 10`

```python
from civil_toolbox.calculators import TR55

result = TR55.runoff_depth(
    rainfall_depth_in=5.0,    # inches
    curve_number=80,          # 0-100
)
print(f"Runoff depth: {result.runoff_depth_in:.2f} inches")
```

**Methods**:
- `potential_retention()` - calculate S from CN
- `initial_abstraction()` - calculate Ia from S
- `runoff_depth()` - full calculation with result dataclass
- `weighted_curve_number()` - area-weighted CN for composites
- `runoff_depth_metric()` - convenience method for mm units

### TimeOfConcentration

Calculates time of concentration using various empirical methods.

**All methods return time in MINUTES.**

```python
from civil_toolbox.calculators import TimeOfConcentration

# Kirpich method (rural watersheds)
result = TimeOfConcentration.kirpich(
    flow_length_ft=5000,
    elevation_diff_ft=100,
)
print(f"Tc: {result.tc_minutes:.1f} minutes")

# Kerby method (overland flow)
result = TimeOfConcentration.kerby(
    flow_length_ft=300,
    slope_percent=2.0,
    retardance_n=0.40,
)

# NRCS lag method
result = TimeOfConcentration.nrcs_lag(
    flow_length_ft=5000,
    slope_percent=3.0,
    curve_number=75,
)

# Composite (multiple segments)
tc_total = TimeOfConcentration.composite([
    ("kerby", {"flow_length_ft": 300, "slope_percent": 2.0, "retardance_n": 0.40}),
    ("kirpich", {"flow_length_ft": 2000, "elevation_diff_ft": 40}),
])
```

**Methods**:
- `kirpich()` - small rural watersheds (< 200 acres)
- `kerby()` - overland flow (< 10 acres, < 1% slope)
- `nrcs_lag()` - uses lag time with Tc = Tlag / 0.6
- `composite()` - sum travel times for multi-segment paths

### KinematicWave

Calculates sheet flow travel time using the kinematic wave equation.

**Returns time in HOURS** (not minutes).

```python
from civil_toolbox.calculators import KinematicWave

result = KinematicWave.sheet_flow_time(
    flow_length_ft=100,           # feet (recommend ≤ 300)
    slope_percent=2.0,            # %
    mannings_n=0.15,              # roughness coefficient
    rainfall_2yr_24hr_in=3.5,     # 2-year, 24-hour rainfall
)
print(f"Travel time: {result.travel_time_hours:.3f} hours")
print(f"Travel time: {result.travel_time_hours * 60:.1f} minutes")
```

**Methods**:
- `sheet_flow_time()` - returns hours
- `sheet_flow_time_minutes()` - convenience method returning minutes
- `is_length_recommended()` - check against 300 ft limit

## Validation

All calculators validate inputs and raise `CalculatorInputError` for invalid values:

```python
from civil_toolbox.calculators import RationalMethod, CalculatorInputError

try:
    result = RationalMethod.calculate(
        runoff_coefficient=1.5,  # Invalid: must be 0-1
        rainfall_intensity_in_per_hr=5.0,
        area_acres=10.0,
    )
except CalculatorInputError as e:
    print(f"Invalid input: {e}")
    print(f"Parameter: {e.parameter}")
```

**Validation functions**:
- `validate_positive()` - value > 0
- `validate_non_negative()` - value >= 0
- `validate_range()` - value within bounds
- `validate_runoff_coefficient()` - 0 < C <= 1
- `validate_curve_number()` - 0 < CN <= 100
- `validate_slope_percent()` - slope > 0
- `validate_mannings_n()` - n > 0, warning if > 1.0

## Result Dataclasses

All calculators return dataclasses that preserve input parameters for traceability:

```python
@dataclass
class RationalMethodResult:
    peak_runoff_cfs: float
    runoff_coefficient: float
    rainfall_intensity_in_per_hr: float
    area_acres: float
```

This allows downstream code to verify inputs and reproduce calculations.
