"""Aggregation utilities for scenario comparison."""

from __future__ import annotations

from civil_toolbox.comparison.models import (
    ComparisonMetric,
    ComparisonStatus,
    PercentDeltaStatus,
    EntityComparisonResult,
    ScenarioTotals,
)
from civil_toolbox.comparison.metrics import METRIC_UNITS


def compute_delta(
    baseline: float | None,
    comparison: float | None,
) -> float | None:
    """Compute absolute delta between two values.

    Returns comparison - baseline, or None if either is None.
    """
    if baseline is None or comparison is None:
        return None
    return comparison - baseline


def compute_percent_delta(
    baseline: float | None,
    comparison: float | None,
) -> tuple[float | None, PercentDeltaStatus]:
    """Compute percent delta between two values.

    Returns (percent_delta, status) where:
    - percent_delta is ((comparison - baseline) / baseline) * 100
    - status indicates if calculation was successful

    If baseline is zero, returns (None, UNDEFINED_ZERO_BASELINE).
    If either value is None, returns (None, NOT_APPLICABLE).
    """
    if baseline is None or comparison is None:
        return None, PercentDeltaStatus.NOT_APPLICABLE

    if baseline == 0:
        return None, PercentDeltaStatus.UNDEFINED_ZERO_BASELINE

    percent = ((comparison - baseline) / baseline) * 100
    return percent, PercentDeltaStatus.OK


def aggregate_totals(
    entity_comparisons: list[EntityComparisonResult],
) -> dict[ComparisonMetric, ScenarioTotals]:
    """Compute scenario-level totals for additive metrics.

    Only additive metrics (peak_flow_cfs, runoff_volume_cuft) are summed.
    Non-additive metrics (runoff_depth_in, time_of_concentration_min) are
    not aggregated.

    Args:
        entity_comparisons: List of per-entity comparison results.

    Returns:
        Dict mapping additive metric to ScenarioTotals.
    """
    additive = ComparisonMetric.additive_metrics()
    totals: dict[ComparisonMetric, ScenarioTotals] = {}

    for metric in additive:
        baseline_sum = 0.0
        comparison_sum = 0.0
        baseline_count = 0
        comparison_count = 0
        has_baseline = False
        has_comparison = False

        for entity in entity_comparisons:
            if metric not in entity.metrics:
                continue

            result = entity.metrics[metric]

            if result.baseline_value is not None:
                baseline_sum += result.baseline_value
                baseline_count += 1
                has_baseline = True

            if result.comparison_value is not None:
                comparison_sum += result.comparison_value
                comparison_count += 1
                has_comparison = True

        if not has_baseline and not has_comparison:
            continue

        baseline_total = baseline_sum if has_baseline else None
        comparison_total = comparison_sum if has_comparison else None

        delta = compute_delta(baseline_total, comparison_total)
        percent_delta, percent_status = compute_percent_delta(
            baseline_total, comparison_total
        )

        entity_count = max(baseline_count, comparison_count)

        totals[metric] = ScenarioTotals(
            metric=metric,
            baseline_total=baseline_total,
            comparison_total=comparison_total,
            delta=delta,
            percent_delta=percent_delta,
            unit=METRIC_UNITS.get(metric, ""),
            entity_count=entity_count,
            percent_delta_status=percent_status,
        )

    return totals
