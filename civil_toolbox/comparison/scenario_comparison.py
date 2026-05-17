"""Scenario comparison engine."""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.comparison.models import (
    ComparisonMetric,
    ComparisonStatus,
    PercentDeltaStatus,
    MatchStrategy,
    MetricComparisonResult,
    EntityComparisonResult,
    ScenarioComparisonResult,
)
from civil_toolbox.comparison.matching import match_entities, EntityMatch
from civil_toolbox.comparison.metrics import (
    get_metrics_for_entity,
    METRIC_UNITS,
)
from civil_toolbox.comparison.aggregation import (
    compute_delta,
    compute_percent_delta,
    aggregate_totals,
)
from civil_toolbox.comparison.validation import validate_comparison_inputs

if TYPE_CHECKING:
    from civil_toolbox.domain.scenario import Scenario


class ScenarioComparison:
    """Engine for comparing two scenarios.

    Compares matched entities between a baseline and comparison scenario,
    computing deltas for recognized metrics. Supports multiple matching
    strategies and optional storm event filtering.

    Example:
        >>> comparison = ScenarioComparison(
        ...     baseline=existing_scenario,
        ...     comparison=proposed_scenario,
        ... )
        >>> result = comparison.compare()
        >>> print(f"Matched {len(result.entity_comparisons)} entities")
    """

    def __init__(
        self,
        baseline: Scenario,
        comparison: Scenario,
        match_strategy: MatchStrategy = MatchStrategy.AUTO,
        explicit_map: dict[str, str] | None = None,
        storm_event_name: str | None = None,
        entity_type: str = "DrainageArea",
    ):
        """Initialize a scenario comparison.

        Args:
            baseline: The baseline scenario.
            comparison: The comparison scenario.
            match_strategy: Strategy for matching entities.
            explicit_map: Explicit ID mapping (baseline_id -> comparison_id).
            storm_event_name: Optional storm event filter.
            entity_type: Type of entity to compare.

        Raises:
            SameScenarioError: If comparing a scenario to itself.
            EmptyScenarioError: If a scenario has no entities.
            InvalidExplicitMapError: If explicit map is invalid.
        """
        validate_comparison_inputs(
            baseline,
            comparison,
            explicit_map=explicit_map,
            entity_type=entity_type,
        )

        self.baseline = baseline
        self.comparison = comparison
        self.match_strategy = match_strategy
        self.explicit_map = explicit_map
        self.storm_event_name = storm_event_name
        self.entity_type = entity_type

    def compare(self) -> ScenarioComparisonResult:
        """Execute the comparison and return results.

        Returns:
            ScenarioComparisonResult with per-entity comparisons and totals.
        """
        match_result = match_entities(
            self.baseline,
            self.comparison,
            strategy=self.match_strategy,
            explicit_map=self.explicit_map,
            entity_type=self.entity_type,
        )

        entity_comparisons = []
        for match in match_result.matches:
            entity_result = self._compare_entity_pair(match)
            entity_comparisons.append(entity_result)

        totals = aggregate_totals(entity_comparisons)

        return ScenarioComparisonResult(
            baseline_scenario_id=self.baseline.id,
            baseline_scenario_name=self.baseline.name,
            comparison_scenario_id=self.comparison.id,
            comparison_scenario_name=self.comparison.name,
            storm_event_name=self.storm_event_name,
            match_strategy=self.match_strategy,
            entity_comparisons=entity_comparisons,
            totals=totals,
            unmatched_baseline_ids=match_result.unmatched_baseline_ids,
            unmatched_comparison_ids=match_result.unmatched_comparison_ids,
        )

    def _compare_entity_pair(self, match: EntityMatch) -> EntityComparisonResult:
        """Compare metrics for a matched entity pair."""
        baseline_metrics = get_metrics_for_entity(
            self.baseline,
            match.baseline_id,
            self.storm_event_name,
        )
        comparison_metrics = get_metrics_for_entity(
            self.comparison,
            match.comparison_id,
            self.storm_event_name,
        )

        all_metrics = set(baseline_metrics.keys()) | set(comparison_metrics.keys())

        metric_results: dict[ComparisonMetric, MetricComparisonResult] = {}

        for metric in all_metrics:
            baseline_extracted = baseline_metrics.get(metric)
            comparison_extracted = comparison_metrics.get(metric)

            baseline_value = baseline_extracted.value if baseline_extracted else None
            comparison_value = (
                comparison_extracted.value if comparison_extracted else None
            )

            if baseline_value is None:
                status = ComparisonStatus.MISSING_BASELINE
            elif comparison_value is None:
                status = ComparisonStatus.MISSING_COMPARISON
            else:
                status = ComparisonStatus.OK

            delta = compute_delta(baseline_value, comparison_value)
            percent_delta, percent_status = compute_percent_delta(
                baseline_value, comparison_value
            )

            unit = METRIC_UNITS.get(metric, "")
            if baseline_extracted and baseline_extracted.unit:
                unit = baseline_extracted.unit
            elif comparison_extracted and comparison_extracted.unit:
                unit = comparison_extracted.unit

            metric_results[metric] = MetricComparisonResult(
                metric=metric,
                baseline_value=baseline_value,
                comparison_value=comparison_value,
                delta=delta,
                percent_delta=percent_delta,
                unit=unit,
                status=status,
                percent_delta_status=percent_status,
            )

        return EntityComparisonResult(
            baseline_entity_id=match.baseline_id,
            comparison_entity_id=match.comparison_id,
            entity_name=match.baseline_name,
            entity_type=match.entity_type,
            metrics=metric_results,
        )


def compare_scenarios(
    baseline: Scenario,
    comparison: Scenario,
    match_strategy: MatchStrategy | str = MatchStrategy.AUTO,
    explicit_map: dict[str, str] | None = None,
    storm_event_name: str | None = None,
    entity_type: str = "DrainageArea",
) -> ScenarioComparisonResult:
    """Convenience function to compare two scenarios.

    Args:
        baseline: The baseline scenario.
        comparison: The comparison scenario.
        match_strategy: Strategy for matching entities (or string value).
        explicit_map: Explicit ID mapping (baseline_id -> comparison_id).
        storm_event_name: Optional storm event filter.
        entity_type: Type of entity to compare.

    Returns:
        ScenarioComparisonResult with per-entity comparisons and totals.

    Example:
        >>> result = compare_scenarios(
        ...     existing_scenario,
        ...     proposed_scenario,
        ...     storm_event_name="100-year",
        ... )
        >>> for entity in result.entity_comparisons:
        ...     peak = entity.metrics.get(ComparisonMetric.PEAK_FLOW_CFS)
        ...     if peak:
        ...         print(f"{entity.entity_name}: {peak.delta:+.1f} cfs")
    """
    if isinstance(match_strategy, str):
        match_strategy = MatchStrategy(match_strategy)

    engine = ScenarioComparison(
        baseline=baseline,
        comparison=comparison,
        match_strategy=match_strategy,
        explicit_map=explicit_map,
        storm_event_name=storm_event_name,
        entity_type=entity_type,
    )
    return engine.compare()
