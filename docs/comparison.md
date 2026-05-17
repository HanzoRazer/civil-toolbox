# Scenario Comparison

Compare drainage analysis results between any scenario pair.

## Use Cases

- Existing vs Proposed
- Proposed vs Alternative
- Alternative A vs Alternative B
- Phase 1 vs Phase 2

## Quick Start

```python
from civil_toolbox.comparison import compare_scenarios, ComparisonMetric

result = compare_scenarios(
    existing_scenario,
    proposed_scenario,
    storm_event_name="100-year",
)

# Per-entity results
for entity in result.entity_comparisons:
    peak = entity.metrics.get(ComparisonMetric.PEAK_FLOW_CFS)
    if peak and peak.delta:
        print(f"{entity.entity_name}: {peak.delta:+.1f} cfs ({peak.percent_delta:+.1f}%)")

# Scenario totals
total = result.totals.get(ComparisonMetric.PEAK_FLOW_CFS)
if total:
    print(f"Total change: {total.delta:+.1f} cfs")
```

## Recognized Metrics

| Metric | Key | Unit | Aggregation |
|--------|-----|------|-------------|
| Peak Flow | `peak_flow_cfs` | cfs | Sum at scenario level |
| Runoff Volume | `runoff_volume_cuft` | cf | Sum at scenario level |
| Runoff Depth | `runoff_depth_in` | in | Per-entity only |
| Time of Concentration | `time_of_concentration_min` | min | Per-entity only |

Only additive metrics (peak flow, volume) are summed at the scenario level.

## Match Strategies

Entities are matched between scenarios using one of four strategies:

| Strategy | Behavior |
|----------|----------|
| `auto` (default) | Try explicit map → ID → normalized name |
| `id` | Match by entity ID only |
| `name` | Match by normalized name (case-insensitive, stripped) |
| `explicit` | Use explicit ID mapping only |

### Explicit Mapping

Map baseline entity IDs to comparison entity IDs:

```python
result = compare_scenarios(
    existing,
    proposed,
    match_strategy="explicit",
    explicit_map={
        "area-existing-A": "area-proposed-A",
        "area-existing-B": "area-redesigned-B",
    },
)
```

## Handling Missing Data

When a metric exists in one scenario but not the other:

```python
# Missing comparison value
{
    "baseline_value": 100.0,
    "comparison_value": None,
    "delta": None,
    "percent_delta": None,
    "status": "missing_comparison"
}

# Missing baseline value
{
    "baseline_value": None,
    "comparison_value": 120.0,
    "delta": None,
    "percent_delta": None,
    "status": "missing_baseline"
}
```

## Zero Baseline Handling

When the baseline value is zero, percent delta is undefined:

```python
{
    "baseline_value": 0.0,
    "comparison_value": 50.0,
    "delta": 50.0,
    "percent_delta": None,
    "percent_delta_status": "undefined_zero_baseline"
}
```

## Storm Event Filtering

Compare results for the same storm event across scenarios:

```python
result = compare_scenarios(
    existing,
    proposed,
    storm_event_name="100-year",
)
```

This filters calculation results to only include those with matching storm event metadata.

## Unmatched Entities

Entities that could not be matched are tracked separately:

```python
result = compare_scenarios(existing, proposed)

# Entities in baseline with no match in comparison
print(result.unmatched_baseline_ids)

# Entities in comparison with no match in baseline
print(result.unmatched_comparison_ids)
```

## Serialization

Results are fully serializable for storage or transmission:

```python
# To JSON-compatible dict
data = result.to_dict()

# From dict
from civil_toolbox.comparison import ScenarioComparisonResult
restored = ScenarioComparisonResult.from_dict(data)
```

Results are ephemeral (computed on demand) and not automatically attached to projects.

## API Reference

### Main Functions

- `compare_scenarios(baseline, comparison, ...)` — Compare two scenarios
- `ScenarioComparison(baseline, comparison, ...)` — Comparison engine class

### Models

- `ComparisonMetric` — Enum of recognized metrics
- `MetricComparisonResult` — Single metric comparison
- `EntityComparisonResult` — All metrics for one entity pair
- `ScenarioTotals` — Aggregated totals for additive metrics
- `ScenarioComparisonResult` — Complete comparison result

### Validation Errors

- `SameScenarioError` — Comparing scenario to itself
- `EmptyScenarioError` — Scenario has no entities
- `InvalidExplicitMapError` — Explicit map contains invalid IDs
