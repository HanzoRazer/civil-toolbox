"""Metric extraction from calculation results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from civil_toolbox.comparison.models import ComparisonMetric

if TYPE_CHECKING:
    from civil_toolbox.domain.calculation import CalculationResult
    from civil_toolbox.domain.scenario import Scenario


METRIC_UNITS: dict[ComparisonMetric, str] = {
    ComparisonMetric.PEAK_FLOW_CFS: "cfs",
    ComparisonMetric.RUNOFF_DEPTH_IN: "in",
    ComparisonMetric.RUNOFF_VOLUME_CUFT: "cf",
    ComparisonMetric.TIME_OF_CONCENTRATION_MIN: "min",
}


@dataclass
class ExtractedMetric:
    """A metric value extracted from a calculation result."""

    metric: ComparisonMetric
    value: float
    unit: str
    entity_id: str
    method: str


def extract_metric_from_result(
    result: CalculationResult,
    metric: ComparisonMetric,
) -> ExtractedMetric | None:
    """Extract a specific metric from a calculation result.

    Args:
        result: The calculation result to extract from.
        metric: The metric to extract.

    Returns:
        ExtractedMetric if found, None otherwise.
    """
    output_key = metric.value
    if output_key not in result.outputs:
        return None

    value = result.outputs[output_key]
    if value is None:
        return None

    unit = result.units.get(output_key, METRIC_UNITS.get(metric, ""))

    return ExtractedMetric(
        metric=metric,
        value=float(value),
        unit=unit,
        entity_id=result.entity_id or "",
        method=result.method,
    )


def extract_all_metrics_from_result(
    result: CalculationResult,
) -> dict[ComparisonMetric, ExtractedMetric]:
    """Extract all recognized metrics from a calculation result.

    Args:
        result: The calculation result to extract from.

    Returns:
        Dict mapping metric to extracted value.
    """
    extracted = {}
    for metric in ComparisonMetric:
        metric_value = extract_metric_from_result(result, metric)
        if metric_value is not None:
            extracted[metric] = metric_value
    return extracted


def get_metrics_for_entity(
    scenario: Scenario,
    entity_id: str,
    storm_event_name: str | None = None,
) -> dict[ComparisonMetric, ExtractedMetric]:
    """Get all recognized metrics for an entity from a scenario.

    Searches calculation results for the entity and extracts metrics.
    If storm_event_name is specified, only uses results where the
    storm event matches.

    Args:
        scenario: The scenario containing calculation results.
        entity_id: The entity ID to get metrics for.
        storm_event_name: Optional storm event filter.

    Returns:
        Dict mapping metric to extracted value.
    """
    metrics: dict[ComparisonMetric, ExtractedMetric] = {}

    for result in scenario.calculation_results:
        if result.entity_id != entity_id:
            continue

        if storm_event_name:
            result_storm = result.metadata.get("storm_event_name")
            if result_storm and result_storm != storm_event_name:
                continue

        for metric, extracted in extract_all_metrics_from_result(result).items():
            if metric not in metrics:
                metrics[metric] = extracted

    return metrics


def get_all_entity_metrics(
    scenario: Scenario,
    entity_type: str = "DrainageArea",
    storm_event_name: str | None = None,
) -> dict[str, dict[ComparisonMetric, ExtractedMetric]]:
    """Get metrics for all entities of a type in a scenario.

    Args:
        scenario: The scenario containing calculation results.
        entity_type: Type of entity to get metrics for.
        storm_event_name: Optional storm event filter.

    Returns:
        Dict mapping entity_id to its metrics.
    """
    entity_metrics: dict[str, dict[ComparisonMetric, ExtractedMetric]] = {}

    for result in scenario.calculation_results:
        if result.entity_type != entity_type:
            continue

        entity_id = result.entity_id
        if not entity_id:
            continue

        if storm_event_name:
            result_storm = result.metadata.get("storm_event_name")
            if result_storm and result_storm != storm_event_name:
                continue

        if entity_id not in entity_metrics:
            entity_metrics[entity_id] = {}

        for metric, extracted in extract_all_metrics_from_result(result).items():
            if metric not in entity_metrics[entity_id]:
                entity_metrics[entity_id][metric] = extracted

    return entity_metrics
