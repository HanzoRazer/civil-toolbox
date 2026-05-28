# Design Criteria Libraries

Design criteria libraries provide structured storage for jurisdiction-specific or project-specific design standards including runoff coefficients, curve numbers, design storms, and IDF curves.

## Overview

The design criteria module provides:

- **RunoffCoefficientTable**: Lookup tables with min/max/typical values by land use
- **CurveNumberTable**: Nested lookup by land use and hydrologic soil group (A/B/C/D)
- **DesignStormDefinition**: Named design storms (e.g., "100-year 24-hour")
- **DesignCriteria**: Complete criteria set for a jurisdiction/project
- **DesignCriteriaLibrary**: Registry for managing multiple criteria sets

## Core Data Models

### RunoffCoefficientEntry

A single entry in a runoff coefficient table:

```python
from civil_toolbox.design_criteria import RunoffCoefficientEntry

entry = RunoffCoefficientEntry(
    land_use="asphalt",
    min=0.70,
    max=0.95,
    typical=0.85,
    description="Asphalt or concrete pavement",
)
```

### RunoffCoefficientTable

Collection of runoff coefficient entries with lookup:

```python
from civil_toolbox.design_criteria import (
    RunoffCoefficientTable,
    RunoffCoefficientEntry,
)

table = RunoffCoefficientTable(
    entries=[
        RunoffCoefficientEntry("asphalt", 0.70, 0.95, 0.85),
        RunoffCoefficientEntry("lawn_sandy", 0.05, 0.20, 0.10),
    ],
    source="County Design Manual 2024",
)

# Get typical coefficient (case-insensitive)
c = table.lookup("asphalt")  # Returns 0.85
c = table.lookup("ASPHALT")  # Also works
c = table.lookup("  Asphalt  ")  # Whitespace stripped

# Get full entry with min/max/typical
entry = table.lookup_entry("lawn_sandy")
print(f"Range: {entry.min} to {entry.max}")
```

### CurveNumberEntry

A single curve number entry with values for each soil group:

```python
from civil_toolbox.design_criteria import CurveNumberEntry

entry = CurveNumberEntry(
    land_use="open_space_good",
    soil_groups={"A": 39, "B": 61, "C": 74, "D": 80},
    description="Open space, good condition",
)

cn = entry.get_cn("B")  # Returns 61
```

### CurveNumberTable

Collection of curve number entries with nested lookup:

```python
from civil_toolbox.design_criteria import (
    CurveNumberTable,
    CurveNumberEntry,
)

table = CurveNumberTable(
    entries=[
        CurveNumberEntry(
            "impervious",
            {"A": 98, "B": 98, "C": 98, "D": 98},
        ),
        CurveNumberEntry(
            "woods_good",
            {"A": 30, "B": 55, "C": 70, "D": 77},
        ),
    ],
    source="TR-55 (Synthetic)",
)

# Two-level lookup: land use + soil group
cn = table.lookup("woods_good", "B")  # Returns 55
```

### DesignStormDefinition

Defines a design storm without storing precomputed values:

```python
from civil_toolbox.design_criteria import DesignStormDefinition

storm = DesignStormDefinition(
    name="100-year 24-hour",
    return_period_years=100,
    duration_minutes=1440,
    description="Major flood event",
)
```

Intensity and depth are derived from the IDF curve when generating storm events.

### DesignCriteria

Complete criteria set combining all components:

```python
from civil_toolbox.design_criteria import (
    DesignCriteria,
    RunoffCoefficientTable,
    CurveNumberTable,
    DesignStormDefinition,
)
from civil_toolbox.rainfall import IDFCurve

criteria = DesignCriteria(
    id="example-county-2024",
    name="Example County Design Standards",
    jurisdiction="Example County",
    source="Design Manual Rev. 2024",
    idf_curve=my_idf_curve,  # Optional embedded IDF curve
    runoff_coefficients=my_coeff_table,
    curve_numbers=my_cn_table,
    design_storms=[
        DesignStormDefinition("10-year 24-hour", 10, 1440),
        DesignStormDefinition("100-year 24-hour", 100, 1440),
    ],
)

# Lookups (case-insensitive)
c = criteria.lookup_runoff_coefficient("asphalt")
cn = criteria.lookup_curve_number("woods_good", "B")

# Get coefficient range (min, max)
min_c, max_c = criteria.lookup_runoff_coefficient_range("asphalt")

# Generate storm event from definition
event = criteria.generate_storm_event("100-year 24-hour")

# Generate all storm events at once
all_events = criteria.generate_all_storm_events()
```

Generated storm events include metadata for audit trails:

```python
event = criteria.generate_storm_event("100-year 24-hour")
print(event.metadata)
# {
#     "idf_curve_id": "example-idf",
#     "idf_curve_name": "Example IDF Curve",
#     "design_criteria_id": "example-county-2024",
#     "design_criteria_name": "Example County Design Standards",
#     "design_storm_name": "100-year 24-hour",
# }
```

### DesignCriteriaLibrary

Registry for managing multiple criteria sets:

```python
from civil_toolbox.design_criteria import (
    DesignCriteriaLibrary,
    DesignCriteria,
)

library = DesignCriteriaLibrary(name="Regional Standards")

# Register criteria
library.register(harris_county_criteria)
library.register(travis_county_criteria)

# Retrieve by ID
criteria = library.get("harris-county-2024")

# Search by jurisdiction
matches = library.find_by_jurisdiction("Harris")

# List all
for criteria_id in library.list_ids():
    print(criteria_id)
```

## IDF Curve Integration

DesignCriteria can reference IDF curves in two ways:

1. **Embedded curve**: Set `idf_curve` directly
2. **Reference by ID**: Set `idf_curve_id` for external lookup

When generating storm events, the embedded curve is used. For referenced curves, resolve via a registry before calling `generate_storm_event()`.

```python
# Embedded curve
criteria = DesignCriteria(
    id="example",
    name="Example",
    idf_curve=my_idf_curve,  # Embedded
)
event = criteria.generate_storm_event("10-year 24-hour")  # Works

# Reference only (requires external resolution)
criteria = DesignCriteria(
    id="example",
    name="Example",
    idf_curve_id="external-idf-123",  # Reference
)
# Must resolve idf_curve_id and set idf_curve before generating events
```

## Land Use Normalization

Land use lookups are case-insensitive and normalize whitespace:

```python
from civil_toolbox.design_criteria import normalize_land_use_key

# Normalization examples
normalize_land_use_key("  Asphalt  ")  # Returns "asphalt"
normalize_land_use_key("Open Space")   # Returns "open_space"

# Lookups work with various formats
table.lookup("ASPHALT")      # Same as "asphalt"
table.lookup("  asphalt ")   # Same as "asphalt"
table.lookup("open space")   # Same as "open_space"
```

## Validation

All values are validated on construction:

- Runoff coefficients: 0 to 1
- Curve numbers: 1 to 100 (integers, must be > 0)
- Soil groups: A, B, C, or D only
- Return periods: Positive integers
- Durations: Positive numbers

```python
from civil_toolbox.design_criteria import (
    validate_runoff_coefficient,
    validate_curve_number,
    validate_soil_group,
    normalize_land_use_key,
    VALID_SOIL_GROUPS,
)

# Manual validation
c = validate_runoff_coefficient(0.85, "my_coefficient")
cn = validate_curve_number(75, "my_cn")
sg = validate_soil_group("b", "soil_group")  # Returns "B" (normalized)
key = normalize_land_use_key("Open Space")   # Returns "open_space"
```

## Error Handling

```python
from civil_toolbox.design_criteria import (
    DesignCriteriaError,       # Base error
    InvalidDesignCriteriaError,  # Invalid data
    DesignCriteriaLookupError,   # Lookup failures
    CriteriaNotFoundError,       # Registry lookup failures
)

try:
    coeff = criteria.lookup_runoff_coefficient("unknown_land_use")
except DesignCriteriaLookupError as e:
    print(f"Lookup failed: {e}")

try:
    criteria = library.get("nonexistent-id")
except CriteriaNotFoundError as e:
    print(f"Criteria not found: {e}")
```

## Serialization

All models support `to_dict()` and `from_dict()` for JSON serialization:

```python
# Serialize
data = criteria.to_dict()
json_str = json.dumps(data)

# Deserialize
data = json.loads(json_str)
criteria = DesignCriteria.from_dict(data)

# Library serialization
library_data = library.to_dict()
restored = DesignCriteriaLibrary.from_dict(library_data)
```

## Example Data

Synthetic example data is available for testing:

```python
from civil_toolbox.design_criteria import (
    create_example_runoff_coefficient_table,
    create_example_curve_number_table,
    create_example_design_criteria,
    create_example_design_criteria_library,
)

# Complete example criteria with IDF curve, coefficients, CNs, and storms
criteria = create_example_design_criteria()

# Just the tables
coeff_table = create_example_runoff_coefficient_table()
cn_table = create_example_curve_number_table()

# Pre-populated library with example criteria
library = create_example_design_criteria_library()
criteria = library.get("example-synthetic")
```

Note: Example data is synthetic and marked with metadata flags indicating it should not be used for engineering design or permitting.
