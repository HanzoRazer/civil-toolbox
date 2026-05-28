# Storm Sensitivity Comparison

Compare a single scenario across multiple storm events to analyze how metrics change with storm severity.

## Overview

Storm sensitivity comparison evaluates how a drainage system responds to different storm intensities. Unlike scenario comparison (which compares different scenarios under the same storm), storm sensitivity compares the same scenario across multiple storms.

Use cases:
- Analyze how peak flows scale from 10-year to 100-year events
- Identify which drainage areas are most sensitive to storm intensity
- Generate sensitivity tables for engineering reports

## Quick Start

```python
from civil_toolbox.comparison import (
    compare_scenario_across_storms,
    StormSensitivityResult,
)

# Compare scenario across all storms
result = compare_scenario_across_storms(scenario)

# View metrics for a specific storm
for row in result.get_metrics_for_storm("storm-100"):
    if row.metric.value == "peak_flow_cfs":
        print(f"{row.entity_name}: {row.value:.1f} cfs ({row.percent_delta:+.1f}%)")

# View totals
for total in result.get_totals_for_storm("storm-100"):
    print(f"{total.metric.value}: {total.total:.1f} {total.unit}")
```

## API Reference

### compare_scenario_across_storms

```python
def compare_scenario_across_storms(
    scenario: Scenario,
    baseline_storm_id: str | None = None,
    entity_type: str = "DrainageArea",
) -> StormSensitivityResult:
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `scenario` | Scenario | The scenario to analyze |
| `baseline_storm_id` | str \| None | ID of baseline storm. If None, uses lowest return period |
| `entity_type` | str | Entity type to compare (default: "DrainageArea") |

**Returns:** `StormSensitivityResult`

### StormSensitivityResult

Contains the complete storm sensitivity analysis.

```python
@dataclass
class StormSensitivityResult:
    scenario_id: str
    scenario_name: str
    baseline_storm_id: str
    baseline_storm_name: str
    baseline_return_period: int | None
    storm_events: list[dict[str, Any]]
    metrics: list[StormSensitivityMetric]
    totals: list[StormSensitivityTotals]
    entity_type: str
    created_at: datetime
```

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `get_metrics_for_entity(entity_id)` | list | Metrics filtered by entity |
| `get_metrics_for_storm(storm_event_id)` | list | Metrics filtered by storm |
| `get_totals_for_storm(storm_event_id)` | list | Totals filtered by storm |
| `to_dict()` | dict | Serialize to dictionary |
| `from_dict(data)` | StormSensitivityResult | Deserialize from dictionary |

### StormSensitivityMetric

A single row in the metrics table (entity + storm + metric combination).

```python
@dataclass
class StormSensitivityMetric:
    entity_id: str
    entity_name: str
    entity_type: str
    storm_event_id: str
    storm_event_name: str
    return_period_years: int | None
    metric: ComparisonMetric
    value: float | None
    unit: str
    baseline_value: float | None
    delta: float | None
    percent_delta: float | None
    status: StormSensitivityStatus
    percent_delta_status: PercentDeltaStatus
```

### StormSensitivityTotals

Per-storm totals for additive metrics.

```python
@dataclass
class StormSensitivityTotals:
    storm_event_id: str
    storm_event_name: str
    return_period_years: int | None
    metric: ComparisonMetric
    total: float | None
    unit: str
    baseline_total: float | None
    delta: float | None
    percent_delta: float | None
    entity_count: int
    percent_delta_status: PercentDeltaStatus
```

### StormSensitivityStatus

Status of a metric row.

| Status | Description |
|--------|-------------|
| `OK` | Metric calculated successfully |
| `MISSING_METRIC` | No metric value for this storm |
| `MISSING_BASELINE` | No baseline value for this entity |

## Storm Event Linking

Calculation results link to storms via metadata fields:

1. **storm_event_id** (priority): Exact match by storm ID
2. **storm_event_name** (fallback): Match by storm name

```python
result = CalculationResult(
    method="rational_method",
    entity_id="area-1",
    outputs={"peak_flow_cfs": 150.0},
    metadata={"storm_event_id": "storm-100"},  # Links to storm
)
```

## Baseline Selection

By default, the storm with the lowest return period becomes the baseline:

```python
# Automatic: 10-year storm selected as baseline
result = compare_scenario_across_storms(scenario)

# Explicit: Use 25-year storm as baseline
result = compare_scenario_across_storms(scenario, baseline_storm_id="storm-25")
```

If no storms have return periods, the first storm in the list becomes the baseline.

## Additive vs Non-Additive Metrics

Only additive metrics are summed at the scenario level:

| Metric | Additive | In Totals |
|--------|----------|-----------|
| `peak_flow_cfs` | Yes | Yes |
| `runoff_volume_cuft` | Yes | Yes |
| `runoff_depth_in` | No | No |
| `time_of_concentration_min` | No | No |

## Report Integration

Use with report templates via `storm_sensitivity_table` section type:

```python
from civil_toolbox.reporting import (
    ReportTemplate,
    SectionTemplate,
    ReportTemplateContext,
    build_report_from_template,
)

template = ReportTemplate(
    id="sensitivity_report",
    name="Storm Sensitivity Report",
    version="1.0",
    sections=[
        SectionTemplate(
            id="sensitivity",
            title="Storm Sensitivity Analysis",
            section_type="storm_sensitivity_table",
        ),
    ],
)

context = ReportTemplateContext(
    storm_sensitivity=result,
)

report = build_report_from_template(template, context)
```

## Serialization

Results serialize for storage or transmission:

```python
# Serialize
data = result.to_dict()

# Deserialize
restored = StormSensitivityResult.from_dict(data)
```

## Example: Full Workflow

```python
from civil_toolbox.domain import Scenario, DrainageArea, StormEvent
from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.comparison import compare_scenario_across_storms

# Create scenario with multiple storms
scenario = Scenario(name="Development Site")

# Add storm events
for period in [2, 10, 25, 100]:
    scenario.storm_events.append(
        StormEvent(id=f"storm-{period}", name=f"{period}-year", return_period_years=period)
    )

# Add drainage areas
for name in ["Basin A", "Basin B"]:
    area = DrainageArea(name=name)
    scenario.add_drainage_area(area)

# Add calculation results (one per area per storm)
# ... (populate from adapter calculations)

# Compare across storms
result = compare_scenario_across_storms(scenario)

# Analyze scaling from 2-year to 100-year
baseline_metrics = result.get_metrics_for_storm(result.baseline_storm_id)
storm_100_metrics = result.get_metrics_for_storm("storm-100")

print(f"Baseline: {result.baseline_storm_name}")
print(f"Peak flow scaling to 100-year:")

for m100 in storm_100_metrics:
    if m100.metric.value == "peak_flow_cfs" and m100.percent_delta:
        print(f"  {m100.entity_name}: +{m100.percent_delta:.1f}%")
```

## Comparison with Scenario Comparison

| Feature | Scenario Comparison | Storm Sensitivity |
|---------|---------------------|-------------------|
| Purpose | Compare different scenarios | Compare storm intensities |
| Input | Two scenarios, optional storm filter | One scenario, all storms |
| Baseline | Baseline scenario | Lowest return period storm |
| Entity matching | ID/name/explicit mapping | Same entities across storms |
| Use case | Existing vs Proposed | 10-year vs 100-year response |
