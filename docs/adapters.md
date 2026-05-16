# Calculator Domain Adapters

Adapters connect the calculation engine to domain entities, producing auditable `CalculationResult` objects that preserve inputs, outputs, units, assumptions, and engineering references.

## Design Principles

1. **No silent inference**: Adapters never guess missing values. If a required field is `None`, they raise `MissingFieldError`.

2. **Call calculators only**: Adapters do not duplicate formulas. They extract data from domain entities and delegate to the calculation engine.

3. **Auditable results**: Every calculation produces a `CalculationResult` with full traceability.

4. **Scenario integration**: Helper functions attach results to scenarios for project persistence.

## Adapters

### RationalMethodAdapter

Connects `DrainageArea` + `StormEvent` to the Rational Method calculator.

```python
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.adapters import RationalMethodAdapter

area = DrainageArea(
    name="Commercial Lot",
    area_acres=25.0,
    runoff_coefficient=0.85,
)
storm = StormEvent(
    name="10-year",
    rainfall_intensity_in_per_hr=5.5,
)

result = RationalMethodAdapter.calculate(area, storm)
print(f"Peak runoff: {result.outputs['peak_runoff_cfs']:.1f} cfs")
```

**Required fields**:
- `DrainageArea.area_acres`
- `DrainageArea.runoff_coefficient`
- `StormEvent.rainfall_intensity_in_per_hr`

**Warnings**: Area > 200 acres triggers a warning (optional via `warn_on_large_area=False`).

### TR55Adapter

Connects `DrainageArea` + `StormEvent` to the TR-55 curve number method.

```python
from civil_toolbox.adapters import TR55Adapter

area = DrainageArea(name="Residential", curve_number=75)
storm = StormEvent(name="25-year", rainfall_depth_in=6.0)

result = TR55Adapter.calculate_runoff_depth(area, storm)
print(f"Runoff depth: {result.outputs['runoff_depth_in']:.2f} inches")
```

**Methods**:
- `calculate_runoff_depth()`: Requires `curve_number` and `rainfall_depth_in`
- `calculate_weighted_cn()`: Computes area-weighted CN from multiple areas
- `calculate_runoff_volume()`: Adds volume in cf and ac-ft

### TimeOfConcentrationAdapter

Connects `FlowPath` to Kirpich, Kerby, and composite Tc methods.

```python
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.adapters import TimeOfConcentrationAdapter

path = FlowPath(name="Main Channel")
path.add_segment(FlowPathSegment(
    segment_type="channel",
    length_ft=3000,
    slope_ft_per_ft=0.02,
))

result = TimeOfConcentrationAdapter.calculate_kirpich(path)
print(f"Tc: {result.outputs['tc_minutes']:.1f} minutes")
```

**Methods**:
- `calculate_kirpich()`: Uses total length and elevation drop
- `calculate_kerby()`: Uses length-weighted roughness
- `calculate_composite()`: Per-segment method selection (sheet → kinematic wave, channel → Kirpich)

**Note**: All Tc methods return time in **minutes**.

### KinematicWave (Intentionally Indirect)

The `KinematicWave` calculator is accessed through `TimeOfConcentrationAdapter.calculate_composite()` for sheet flow segments. A dedicated `KinematicWaveAdapter` is not provided because:

1. Sheet flow Tc is rarely computed in isolation — it's part of a composite flow path
2. The composite method auto-selects kinematic wave for `segment_type="sheet"`
3. Direct domain workflows requiring standalone kinematic wave do not yet exist

If a direct adapter is needed in the future, add `KinematicWaveAdapter` without modifying the existing composite workflow.

## Scenario Helpers

Convenience functions that run calculations and attach results to scenarios.

```python
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.adapters import run_rational_method, run_all_drainage_areas

scenario = Scenario(name="Existing Conditions")
scenario.add_drainage_area(area)

# Run single calculation
result = run_rational_method(scenario, area, storm)
# Result is now in scenario.calculation_results

# Run for all areas
results = run_all_drainage_areas(scenario, storm, method="rational")
```

**Available helpers**:
- `run_rational_method(scenario, area, storm)`
- `run_rational_method_composite(scenario, areas, storm)`
- `run_tr55_runoff_depth(scenario, area, storm)`
- `run_tr55_runoff_volume(scenario, area, storm)`
- `run_tc_kirpich(scenario, flow_path)`
- `run_tc_composite(scenario, flow_path, rainfall_2yr_24hr_in)`
- `run_all_drainage_areas(scenario, storm, method)`

All helpers accept `attach=False` to skip modifying the scenario.

## Error Handling

```python
from civil_toolbox.adapters import RationalMethodAdapter, MissingFieldError

area = DrainageArea(name="Incomplete")  # Missing area_acres and coefficient
storm = StormEvent(name="Storm", rainfall_intensity_in_per_hr=5.0)

try:
    result = RationalMethodAdapter.calculate(area, storm)
except MissingFieldError as e:
    print(f"Missing {e.field_name} on {e.entity_type}")
    # Output: Missing area_acres on DrainageArea
```

**Error types**:
- `MissingFieldError`: Required field is `None`
- `IncompatibleEntityError`: Entities cannot be used together
- `CalculationNotApplicableError`: Method limits exceeded

## Result Builder

For custom adapters, use `ResultBuilder` to construct results:

```python
from civil_toolbox.adapters import ResultBuilder

result = (
    ResultBuilder("my_method")
    .for_entity(entity.id, "DrainageArea")
    .with_input("area_acres", 25.0, "acres")
    .with_output("flow_rate", 100.0, "cfs")
    .with_assumption("Steady-state flow conditions")
    .with_reference("HEC-22", "FHWA", year=2009)
    .build()
)
```
