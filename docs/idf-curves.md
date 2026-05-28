# IDF Curves

Structured IDF (Intensity-Duration-Frequency) curve support for rainfall data lookup and storm event generation.

## Overview

IDF curves describe the relationship between rainfall intensity, storm duration, and return period (frequency). Civil Toolbox provides:

- Structured IDF curve data models
- Deterministic intensity and depth lookup
- Optional duration interpolation
- StormEvent generation from IDF data
- Serialization for storage and sharing

## Quick Start

```python
from civil_toolbox.rainfall import IDFCurve, IDFPoint

# Create an IDF curve
curve = IDFCurve(
    id="site-idf",
    name="Site IDF Curve",
    source="Local Rainfall Data",
    points=[
        IDFPoint(return_period_years=10, duration_minutes=15, rainfall_intensity_in_per_hr=4.5),
        IDFPoint(return_period_years=10, duration_minutes=60, rainfall_intensity_in_per_hr=2.0),
        IDFPoint(return_period_years=100, duration_minutes=15, rainfall_intensity_in_per_hr=7.0),
        IDFPoint(return_period_years=100, duration_minutes=60, rainfall_intensity_in_per_hr=3.0),
    ],
)

# Look up intensity
intensity = curve.lookup_intensity(return_period_years=100, duration_minutes=15)
print(f"100-year 15-min intensity: {intensity:.2f} in/hr")

# Generate a storm event
storm = curve.to_storm_event(return_period_years=100, duration_minutes=15)
print(f"{storm.name}: {storm.rainfall_intensity_in_per_hr:.2f} in/hr")
```

## Data Model

### IDFPoint

A single point in an IDF curve.

```python
@dataclass
class IDFPoint:
    return_period_years: int
    duration_minutes: float
    rainfall_intensity_in_per_hr: float
    rainfall_depth_in: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `return_period_years` | int | Yes | Return period in years (e.g., 10, 25, 100) |
| `duration_minutes` | float | Yes | Storm duration in minutes |
| `rainfall_intensity_in_per_hr` | float | Yes | Rainfall intensity in inches per hour |
| `rainfall_depth_in` | float | No | Rainfall depth in inches |
| `metadata` | dict | No | Additional metadata |

### IDFCurve

A collection of IDF points with lookup and generation methods.

```python
@dataclass
class IDFCurve:
    id: str
    name: str
    source: str | None = None
    location: str | None = None
    station_id: str | None = None
    units: dict[str, str] = field(default_factory=...)
    points: list[IDFPoint] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | Yes | Unique curve identifier |
| `name` | str | Yes | Human-readable name |
| `source` | str | No | Data source (e.g., "NOAA Atlas 14") |
| `location` | str | No | Location description |
| `station_id` | str | No | Rainfall station identifier |
| `units` | dict | No | Unit metadata (documentation only) |
| `points` | list | Yes | List of IDF data points |
| `metadata` | dict | No | Additional configuration |

## Durations and Return Periods

Get available durations and return periods:

```python
# Get all return periods (sorted)
periods = curve.get_return_periods()
# [10, 25, 100]

# Get all durations (sorted)
durations = curve.get_durations()
# [15.0, 30.0, 60.0]

# Get durations for a specific return period
durations_10yr = curve.get_durations(return_period_years=10)
```

## Intensity Lookup

Look up rainfall intensity with optional interpolation:

```python
# Exact lookup
intensity = curve.lookup_intensity(
    return_period_years=100,
    duration_minutes=15,
)

# With duration interpolation (default)
intensity = curve.lookup_intensity(
    return_period_years=100,
    duration_minutes=22.5,  # Interpolated between 15 and 30
    interpolate_duration=True,
)

# Without interpolation (requires exact match)
intensity = curve.lookup_intensity(
    return_period_years=100,
    duration_minutes=15,
    interpolate_duration=False,
)
```

### Interpolation Rules

| Parameter | Default | Behavior |
|-----------|---------|----------|
| `interpolate_duration` | True | Linear interpolation within duration range |
| `interpolate_return_period` | False | Not implemented (raises error if True) |

Duration interpolation:
- Uses linear interpolation between adjacent points
- No extrapolation beyond min/max duration
- Fails clearly if duration is outside range

Return period interpolation:
- Not implemented in this foundation series
- If enabled, raises `IDFInterpolationError`
- Future series may add this capability

## Depth Lookup

Look up or derive rainfall depth:

```python
# If depth values are stored, returns stored value
depth = curve.lookup_depth(return_period_years=100, duration_minutes=15)

# If depth not stored, derives from intensity:
# depth_in = intensity_in_per_hr * duration_minutes / 60
```

The function:
1. Returns stored depth if available
2. Interpolates stored depth if interpolation enabled
3. Falls back to deriving depth from intensity

## StormEvent Generation

Generate domain `StormEvent` objects from IDF data:

```python
from civil_toolbox.rainfall import IDFCurve

storm = curve.to_storm_event(
    return_period_years=100,
    duration_minutes=15,
)

# storm.name = "100-year 15-minute storm"
# storm.return_period_years = 100
# storm.duration_hours = 0.25
# storm.rainfall_intensity_in_per_hr = 7.0
# storm.rainfall_depth_in = 1.75
```

### Default Name Format

When `name` is not provided:

```text
{return_period}-year {duration}-minute storm
```

Examples:
- `100-year 15-minute storm`
- `10-year 60-minute storm`
- `25-year 7.5-minute storm` (fractional durations preserved)

### Custom Name

```python
storm = curve.to_storm_event(
    return_period_years=100,
    duration_minutes=15,
    name="Design Storm Q100",
)
```

## Example IDF Curve

Civil Toolbox includes a synthetic example curve for testing:

```python
from civil_toolbox.rainfall import create_example_idf_curve

curve = create_example_idf_curve()

# curve.id = "example-synthetic"
# curve.metadata["synthetic"] = True
# curve.metadata["for_testing_only"] = True
```

**Warning:** This is synthetic data for demonstration only. Do not use for engineering design or permitting.

## Serialization

IDF curves serialize for storage:

```python
# Serialize to dict
data = curve.to_dict()

# Deserialize from dict
restored = IDFCurve.from_dict(data)
```

Example serialized structure:

```json
{
  "id": "site-idf",
  "name": "Site IDF Curve",
  "source": "Local Data",
  "location": null,
  "station_id": null,
  "units": {
    "duration": "minutes",
    "rainfall_intensity": "in/hr",
    "rainfall_depth": "in"
  },
  "points": [
    {
      "return_period_years": 100,
      "duration_minutes": 15.0,
      "rainfall_intensity_in_per_hr": 7.0,
      "rainfall_depth_in": null,
      "metadata": {}
    }
  ],
  "metadata": {}
}
```

## Error Handling

All rainfall errors inherit from `RainfallDataError`:

```python
from civil_toolbox.rainfall import (
    RainfallDataError,
    InvalidIDFDataError,
    IDFLookupError,
    IDFInterpolationError,
)

try:
    intensity = curve.lookup_intensity(100, 200)
except IDFInterpolationError as e:
    print(f"Duration out of range: {e}")
except IDFLookupError as e:
    print(f"Lookup failed: {e}")
except RainfallDataError as e:
    print(f"Rainfall error: {e}")
```

| Error | Description |
|-------|-------------|
| `RainfallDataError` | Base class for all rainfall errors |
| `InvalidIDFDataError` | Invalid IDF data (negative values, duplicates) |
| `IDFLookupError` | Lookup failed (missing return period) |
| `IDFInterpolationError` | Interpolation failed (out of range) |

## Limitations

This foundation series does not include:

- NOAA Atlas 14 API integration
- Live web downloads
- GIS rainfall raster lookup
- Automatic jurisdiction selection
- Temporal rainfall distributions
- Hyetograph generation
- Climate change adjustment factors
- IDF curve fitting from raw data
- Return period interpolation
- Unit conversion

## Future Work

Planned enhancements:

- NOAA Atlas 14 integration
- Jurisdiction-specific design criteria libraries
- Return period interpolation
- Multiple interpolation methods (log-linear, etc.)
- Rainfall distribution curves
- Climate change factors
