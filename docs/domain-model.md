# Domain Model Foundation

Civil Toolbox uses a typed domain model to represent drainage analysis projects, scenarios, and calculations.

---

## Overview

The domain model provides:

- **Typed entities** with validation
- **Unit-explicit field names** (e.g., `area_acres`, `rainfall_depth_in`)
- **Serialization** to and from JSON
- **Auditable calculation results** with assumptions, references, and warnings

---

## Core Entities

### Project

A drainage analysis project containing metadata, design criteria, and scenarios.

```python
from civil_toolbox.domain.project import Project, DesignCriteria

project = Project(
    name="Example Site Drainage",
    client="ABC Development",
    jurisdiction="harris_county",
    design_criteria=DesignCriteria(
        design_storm_years=100,
        rainfall_distribution="Type III",
    ),
)
```

### Scenario

A scenario within a project representing different conditions (existing, proposed, with/without detention).

```python
from civil_toolbox.domain.scenario import Scenario

existing = Scenario(name="Existing Conditions")
proposed = Scenario(name="Proposed Development")

project.add_scenario(existing)
project.add_scenario(proposed)
```

### DrainageArea

A contributing watershed or subbasin with hydrologic properties.

```python
from civil_toolbox.domain.drainage import DrainageArea

area = DrainageArea(
    name="Basin A",
    area_acres=50.0,
    runoff_coefficient=0.65,
    curve_number=80,
    soil_group="B",
    land_use="residential",
)
scenario.add_drainage_area(area)
```

**Validation:**
- `area_acres` must be positive
- `runoff_coefficient` must be between 0 and 1
- `curve_number` must be between 0 and 100

### StormEvent

Rainfall characteristics for a design storm or historical event.

```python
from civil_toolbox.domain.storm import StormEvent

storm = StormEvent(
    name="100-year Design Storm",
    return_period_years=100,
    duration_hours=24.0,
    rainfall_depth_in=9.0,
    rainfall_intensity_in_per_hr=0.375,
    distribution="Type III",
)
scenario.add_storm_event(storm)
```

**Validation:**
- `return_period_years` must be positive
- `duration_hours` must be positive
- `rainfall_depth_in` cannot be negative
- `rainfall_intensity_in_per_hr` cannot be negative

### FlowPath and FlowPathSegment

The path water travels from the hydraulically most distant point to the outlet.

```python
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment

path = FlowPath(name="Main Flow Path")
path.add_segment(FlowPathSegment(
    segment_type="sheet",
    length_ft=100.0,
    slope_ft_per_ft=0.02,
    roughness_n=0.15,
))
path.add_segment(FlowPathSegment(
    segment_type="shallow_concentrated",
    length_ft=500.0,
    slope_ft_per_ft=0.01,
))
path.add_segment(FlowPathSegment(
    segment_type="channel",
    length_ft=1500.0,
    slope_ft_per_ft=0.005,
    roughness_n=0.035,
))
scenario.add_flow_path(path)

print(path.total_length_ft)  # 2100.0
```

**Segment types:**
- `sheet` — overland sheet flow
- `shallow_concentrated` — shallow concentrated flow
- `channel` — open channel flow

### InfrastructureElement

Drainage infrastructure such as pipes, culverts, channels, and detention facilities.

```python
from civil_toolbox.domain.infrastructure import InfrastructureElement

pipe = InfrastructureElement(
    name="Storm Sewer Main",
    element_type="pipe",
    length_ft=800.0,
    slope_ft_per_ft=0.005,
    diameter_in=36.0,
    material="RCP",
    mannings_n=0.013,
    capacity_cfs=85.0,
)
scenario.add_infrastructure(pipe)
```

**Element types:**
- `pipe` — storm sewer pipe
- `culvert` — roadway culvert
- `channel` — open channel
- `inlet` — stormwater inlet
- `detention` — detention facility
- `outlet` — outlet structure

### CalculationResult

An auditable record of a calculation with inputs, outputs, units, assumptions, and references.

```python
from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.base import EngineeringAssumption, EngineeringReference

result = CalculationResult(
    method="Rational Method",
    entity_id=area.id,
    entity_type="DrainageArea",
    inputs={
        "runoff_coefficient": 0.65,
        "rainfall_intensity_in_per_hr": 4.5,
        "area_acres": 50.0,
    },
    outputs={
        "peak_flow_cfs": 146.25,
    },
    units={
        "runoff_coefficient": "dimensionless",
        "rainfall_intensity_in_per_hr": "in/hr",
        "area_acres": "acre",
        "peak_flow_cfs": "cfs",
    },
)

result.add_assumption(EngineeringAssumption(
    description="Peak discharge occurs when entire area is contributing",
    category="hydrology",
))

result.add_reference(EngineeringReference(
    title="Urban Drainage Design Manual",
    source="FHWA HEC-22",
    year=2009,
))

scenario.add_calculation_result(result)
```

---

## Supporting Types

### EngineeringReference

A citation to an authoritative engineering source.

```python
from civil_toolbox.domain.base import EngineeringReference

ref = EngineeringReference(
    title="Urban Hydrology for Small Watersheds",
    source="NRCS TR-55",
    year=1986,
    section="Chapter 2",
)
```

### EngineeringAssumption

An explicit assumption made during a calculation.

```python
from civil_toolbox.domain.base import EngineeringAssumption

assumption = EngineeringAssumption(
    description="Steady-state flow conditions",
    category="hydraulics",
)
```

### ValidationWarning

A warning generated during validation or calculation.

```python
from civil_toolbox.domain.base import ValidationWarning

warning = ValidationWarning(
    message="Curve number exceeds typical range for this soil group",
    field="curve_number",
    severity="warning",  # "info", "warning", or "error"
)
```

---

## Serialization

All domain entities support `to_dict()` and `from_dict()` for JSON serialization.

```python
import json

# Serialize
project_data = project.to_dict()
json_str = json.dumps(project_data, indent=2)

# Deserialize
parsed = json.loads(json_str)
restored_project = Project.from_dict(parsed)
```

---

## Field Naming Convention

Fields use unit-explicit names to avoid ambiguity:

| Field | Unit |
|-------|------|
| `area_acres` | acres |
| `length_ft` | feet |
| `slope_ft_per_ft` | ft/ft |
| `diameter_in` | inches |
| `rainfall_depth_in` | inches |
| `rainfall_intensity_in_per_hr` | in/hr |
| `duration_hours` | hours |
| `peak_flow_cfs` | cfs |
| `capacity_cfs` | cfs |

---

## Validation

Domain entities validate inputs on construction:

```python
# Raises ValueError: area_acres must be positive
DrainageArea(name="Bad", area_acres=-10)

# Raises ValueError: runoff_coefficient must be between 0 and 1
DrainageArea(name="Bad", runoff_coefficient=1.5)

# Raises ValueError: element_type must be one of (pipe, culvert, ...)
InfrastructureElement(name="Bad", element_type="invalid")
```

---

## Entity Relationships

```
Project
├── DesignCriteria
└── Scenario[]
    ├── DrainageArea[]
    ├── StormEvent[]
    ├── FlowPath[]
    │   └── FlowPathSegment[]
    ├── InfrastructureElement[]
    └── CalculationResult[]
        ├── EngineeringAssumption[]
        ├── EngineeringReference[]
        └── ValidationWarning[]
```

---

## Next Steps

The domain model foundation enables:

1. **Calculator adapters** — connect domain entities to hydrologic calculators
2. **Project persistence** — save/load projects to JSON files
3. **Scenario comparison** — compare existing vs proposed conditions
4. **Reporting** — generate engineering reports from domain data
