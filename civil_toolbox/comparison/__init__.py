"""Comparison module for Civil Toolbox.

Two comparison modes:

1. **Scenario Comparison** — Compare different scenarios under the same storm:
   - Existing vs Proposed
   - Alternative A vs Alternative B
   - Phase 1 vs Phase 2

2. **Storm Sensitivity** — Compare a single scenario across multiple storms:
   - 10-year vs 100-year response
   - Analyze how metrics scale with storm intensity

Recognized metrics:
- peak_flow_cfs — additive, summed at scenario level
- runoff_volume_cuft — additive, summed at scenario level
- runoff_depth_in — per-entity only
- time_of_concentration_min — per-entity only

Example (scenario comparison):
    >>> from civil_toolbox.comparison import compare_scenarios, ComparisonMetric
    >>> result = compare_scenarios(
    ...     existing_scenario,
    ...     proposed_scenario,
    ...     storm_event_name="100-year",
    ... )
    >>> for entity in result.entity_comparisons:
    ...     peak = entity.metrics.get(ComparisonMetric.PEAK_FLOW_CFS)
    ...     if peak and peak.delta:
    ...         print(f"{entity.entity_name}: {peak.delta:+.1f} cfs")

Example (storm sensitivity):
    >>> from civil_toolbox.comparison import compare_scenario_across_storms
    >>> result = compare_scenario_across_storms(scenario)
    >>> for row in result.metrics:
    ...     if row.metric.value == "peak_flow_cfs":
    ...         print(f"{row.entity_name} / {row.storm_event_name}: {row.value:.1f} cfs")
"""

from civil_toolbox.comparison.models import (
    ComparisonMetric,
    ComparisonStatus,
    PercentDeltaStatus,
    MatchStrategy,
    MetricComparisonResult,
    EntityComparisonResult,
    ScenarioTotals,
    ScenarioComparisonResult,
)

from civil_toolbox.comparison.matching import (
    EntityMatch,
    MatchResult,
    match_entities,
)

from civil_toolbox.comparison.metrics import (
    METRIC_UNITS,
    ExtractedMetric,
    extract_metric_from_result,
    get_metrics_for_entity,
    get_all_entity_metrics,
)

from civil_toolbox.comparison.aggregation import (
    compute_delta,
    compute_percent_delta,
    aggregate_totals,
)

from civil_toolbox.comparison.validation import (
    ComparisonValidationError,
    SameScenarioError,
    EmptyScenarioError,
    NoMatchesError,
    InvalidExplicitMapError,
    validate_comparison_inputs,
)

from civil_toolbox.comparison.scenario_comparison import (
    ScenarioComparison,
    compare_scenarios,
)

from civil_toolbox.comparison.storm_sensitivity import (
    StormSensitivityStatus,
    StormSensitivityMetric,
    StormSensitivityTotals,
    StormSensitivityResult,
    compare_scenario_across_storms,
)

__all__ = [
    # Models
    "ComparisonMetric",
    "ComparisonStatus",
    "PercentDeltaStatus",
    "MatchStrategy",
    "MetricComparisonResult",
    "EntityComparisonResult",
    "ScenarioTotals",
    "ScenarioComparisonResult",
    # Matching
    "EntityMatch",
    "MatchResult",
    "match_entities",
    # Metrics
    "METRIC_UNITS",
    "ExtractedMetric",
    "extract_metric_from_result",
    "get_metrics_for_entity",
    "get_all_entity_metrics",
    # Aggregation
    "compute_delta",
    "compute_percent_delta",
    "aggregate_totals",
    # Validation
    "ComparisonValidationError",
    "SameScenarioError",
    "EmptyScenarioError",
    "NoMatchesError",
    "InvalidExplicitMapError",
    "validate_comparison_inputs",
    # Main API
    "ScenarioComparison",
    "compare_scenarios",
    # Storm Sensitivity
    "StormSensitivityStatus",
    "StormSensitivityMetric",
    "StormSensitivityTotals",
    "StormSensitivityResult",
    "compare_scenario_across_storms",
]
