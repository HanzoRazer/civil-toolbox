"""Storm sensitivity comparison.

Compare a single scenario across multiple storm events to analyze
how metrics change with storm severity.

Example:
    >>> from civil_toolbox.comparison.storm_sensitivity import (
    ...     compare_scenario_across_storms,
    ... )
    >>> result = compare_scenario_across_storms(scenario)
    >>> for row in result.metrics:
    ...     print(f"{row.entity_name} / {row.storm_name}: {row.value} {row.unit}")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

from civil_toolbox.comparison.models import (
    ComparisonMetric,
    PercentDeltaStatus,
)
from civil_toolbox.comparison.metrics import (
    extract_all_metrics_from_result,
    METRIC_UNITS,
)
from civil_toolbox.comparison.aggregation import (
    compute_delta,
    compute_percent_delta,
)

if TYPE_CHECKING:
    from civil_toolbox.domain.scenario import Scenario
    from civil_toolbox.domain.storm import StormEvent


class StormSensitivityStatus(Enum):
    """Status of a storm sensitivity metric row."""

    OK = "ok"
    MISSING_METRIC = "missing_metric"
    MISSING_BASELINE = "missing_baseline"


def _utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class StormSensitivityMetric:
    """A single metric row in storm sensitivity comparison.

    Each row represents one entity + storm event + metric combination.

    Attributes:
        entity_id: ID of the entity (e.g., DrainageArea).
        entity_name: Display name of the entity.
        entity_type: Type of entity.
        storm_event_id: ID of the storm event.
        storm_event_name: Name of the storm event.
        return_period_years: Return period of the storm.
        metric: The comparison metric.
        value: Metric value for this storm.
        unit: Unit of measurement.
        baseline_value: Value from the baseline storm.
        delta: Difference from baseline (value - baseline_value).
        percent_delta: Percentage change from baseline.
        status: Status of this row.
        percent_delta_status: Status of percent delta calculation.
    """

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
    status: StormSensitivityStatus = StormSensitivityStatus.OK
    percent_delta_status: PercentDeltaStatus = PercentDeltaStatus.OK

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "storm_event_id": self.storm_event_id,
            "storm_event_name": self.storm_event_name,
            "return_period_years": self.return_period_years,
            "metric": self.metric.value,
            "value": self.value,
            "unit": self.unit,
            "baseline_value": self.baseline_value,
            "delta": self.delta,
            "percent_delta": self.percent_delta,
            "status": self.status.value,
            "percent_delta_status": self.percent_delta_status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StormSensitivityMetric:
        """Deserialize from dictionary."""
        return cls(
            entity_id=data["entity_id"],
            entity_name=data["entity_name"],
            entity_type=data["entity_type"],
            storm_event_id=data["storm_event_id"],
            storm_event_name=data["storm_event_name"],
            return_period_years=data.get("return_period_years"),
            metric=ComparisonMetric(data["metric"]),
            value=data["value"],
            unit=data["unit"],
            baseline_value=data["baseline_value"],
            delta=data["delta"],
            percent_delta=data["percent_delta"],
            status=StormSensitivityStatus(data["status"]),
            percent_delta_status=PercentDeltaStatus(data["percent_delta_status"]),
        )


@dataclass
class StormSensitivityTotals:
    """Aggregated totals for a single storm event.

    Only additive metrics (peak_flow_cfs, runoff_volume_cuft) are summed.

    Attributes:
        storm_event_id: ID of the storm event.
        storm_event_name: Name of the storm event.
        return_period_years: Return period of the storm.
        metric: The additive metric.
        total: Sum of metric across all entities.
        unit: Unit of measurement.
        baseline_total: Total from the baseline storm.
        delta: Difference from baseline total.
        percent_delta: Percentage change from baseline.
        entity_count: Number of entities included.
        percent_delta_status: Status of percent delta calculation.
    """

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
    percent_delta_status: PercentDeltaStatus = PercentDeltaStatus.OK

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "storm_event_id": self.storm_event_id,
            "storm_event_name": self.storm_event_name,
            "return_period_years": self.return_period_years,
            "metric": self.metric.value,
            "total": self.total,
            "unit": self.unit,
            "baseline_total": self.baseline_total,
            "delta": self.delta,
            "percent_delta": self.percent_delta,
            "entity_count": self.entity_count,
            "percent_delta_status": self.percent_delta_status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StormSensitivityTotals:
        """Deserialize from dictionary."""
        return cls(
            storm_event_id=data["storm_event_id"],
            storm_event_name=data["storm_event_name"],
            return_period_years=data.get("return_period_years"),
            metric=ComparisonMetric(data["metric"]),
            total=data["total"],
            unit=data["unit"],
            baseline_total=data["baseline_total"],
            delta=data["delta"],
            percent_delta=data["percent_delta"],
            entity_count=data["entity_count"],
            percent_delta_status=PercentDeltaStatus(data["percent_delta_status"]),
        )


@dataclass
class StormSensitivityResult:
    """Complete result of storm sensitivity comparison.

    Contains per-entity per-storm metrics and per-storm totals.

    Attributes:
        scenario_id: ID of the scenario being analyzed.
        scenario_name: Name of the scenario.
        baseline_storm_id: ID of the baseline storm.
        baseline_storm_name: Name of the baseline storm.
        baseline_return_period: Return period of baseline storm.
        storm_events: List of storm events included.
        metrics: Flat list of metric rows.
        totals: Per-storm totals for additive metrics.
        entity_type: Type of entities compared.
        created_at: Timestamp of comparison.
    """

    scenario_id: str
    scenario_name: str
    baseline_storm_id: str
    baseline_storm_name: str
    baseline_return_period: int | None
    storm_events: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[StormSensitivityMetric] = field(default_factory=list)
    totals: list[StormSensitivityTotals] = field(default_factory=list)
    entity_type: str = "DrainageArea"
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "scenario_id": self.scenario_id,
            "scenario_name": self.scenario_name,
            "baseline_storm_id": self.baseline_storm_id,
            "baseline_storm_name": self.baseline_storm_name,
            "baseline_return_period": self.baseline_return_period,
            "storm_events": self.storm_events,
            "metrics": [m.to_dict() for m in self.metrics],
            "totals": [t.to_dict() for t in self.totals],
            "entity_type": self.entity_type,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StormSensitivityResult:
        """Deserialize from dictionary."""
        return cls(
            scenario_id=data["scenario_id"],
            scenario_name=data["scenario_name"],
            baseline_storm_id=data["baseline_storm_id"],
            baseline_storm_name=data["baseline_storm_name"],
            baseline_return_period=data.get("baseline_return_period"),
            storm_events=data.get("storm_events", []),
            metrics=[
                StormSensitivityMetric.from_dict(m)
                for m in data.get("metrics", [])
            ],
            totals=[
                StormSensitivityTotals.from_dict(t)
                for t in data.get("totals", [])
            ],
            entity_type=data.get("entity_type", "DrainageArea"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def get_metrics_for_entity(self, entity_id: str) -> list[StormSensitivityMetric]:
        """Get all metric rows for a specific entity."""
        return [m for m in self.metrics if m.entity_id == entity_id]

    def get_metrics_for_storm(self, storm_event_id: str) -> list[StormSensitivityMetric]:
        """Get all metric rows for a specific storm."""
        return [m for m in self.metrics if m.storm_event_id == storm_event_id]

    def get_totals_for_storm(self, storm_event_id: str) -> list[StormSensitivityTotals]:
        """Get totals for a specific storm."""
        return [t for t in self.totals if t.storm_event_id == storm_event_id]


def _get_storm_event_for_result(
    scenario: Scenario,
    result,
) -> StormEvent | None:
    """Find the storm event associated with a calculation result.

    Checks metadata for storm_event_id first, then storm_event_name.
    """
    storm_id = result.metadata.get("storm_event_id")
    storm_name = result.metadata.get("storm_event_name")

    for storm in scenario.storm_events:
        if storm_id and storm.id == storm_id:
            return storm
        if storm_name and storm.name == storm_name:
            return storm

    return None


def _get_entity_name(scenario: Scenario, entity_id: str, entity_type: str) -> str:
    """Get the display name for an entity."""
    if entity_type == "DrainageArea":
        for area in scenario.drainage_areas:
            if area.id == entity_id:
                return area.name
    elif entity_type == "FlowPath":
        for path in scenario.flow_paths:
            if path.id == entity_id:
                return path.name
    elif entity_type == "InfrastructureElement":
        for element in scenario.infrastructure:
            if element.id == entity_id:
                return element.name

    return entity_id


def _select_baseline_storm(
    storms: list[StormEvent],
    baseline_storm_id: str | None,
) -> StormEvent | None:
    """Select the baseline storm.

    If baseline_storm_id is provided, use that storm.
    Otherwise, select the storm with the lowest return period.
    """
    if not storms:
        return None

    if baseline_storm_id:
        for storm in storms:
            if storm.id == baseline_storm_id:
                return storm
        return None

    storms_with_period = [s for s in storms if s.return_period_years is not None]
    if storms_with_period:
        return min(storms_with_period, key=lambda s: s.return_period_years)

    return storms[0]


def compare_scenario_across_storms(
    scenario: Scenario,
    baseline_storm_id: str | None = None,
    entity_type: str = "DrainageArea",
) -> StormSensitivityResult:
    """Compare a scenario across multiple storm events.

    Analyzes how metrics change across different storm severities
    for the same scenario.

    Args:
        scenario: The scenario to analyze.
        baseline_storm_id: Optional ID of the baseline storm.
            If not provided, uses the storm with lowest return period.
        entity_type: Type of entities to compare.

    Returns:
        StormSensitivityResult with per-entity per-storm metrics
        and per-storm totals.

    Example:
        >>> result = compare_scenario_across_storms(scenario)
        >>> for row in result.metrics:
        ...     if row.metric == ComparisonMetric.PEAK_FLOW_CFS:
        ...         print(f"{row.entity_name} / {row.storm_name}: "
        ...               f"{row.value:.1f} cfs ({row.percent_delta:+.1f}%)")
    """
    storms_in_results: dict[str, StormEvent] = {}
    entity_storm_metrics: dict[str, dict[str, dict[ComparisonMetric, float]]] = {}

    for result in scenario.calculation_results:
        if result.entity_type != entity_type:
            continue

        entity_id = result.entity_id
        if not entity_id:
            continue

        storm = _get_storm_event_for_result(scenario, result)
        if not storm:
            continue

        storms_in_results[storm.id] = storm

        if entity_id not in entity_storm_metrics:
            entity_storm_metrics[entity_id] = {}

        if storm.id not in entity_storm_metrics[entity_id]:
            entity_storm_metrics[entity_id][storm.id] = {}

        extracted = extract_all_metrics_from_result(result)
        for metric, extracted_metric in extracted.items():
            if metric not in entity_storm_metrics[entity_id][storm.id]:
                entity_storm_metrics[entity_id][storm.id][metric] = extracted_metric.value

    storms = list(storms_in_results.values())
    baseline_storm = _select_baseline_storm(storms, baseline_storm_id)

    if not baseline_storm:
        return StormSensitivityResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            baseline_storm_id="",
            baseline_storm_name="",
            baseline_return_period=None,
            storm_events=[],
            metrics=[],
            totals=[],
            entity_type=entity_type,
        )

    storm_events_info = [
        {
            "id": s.id,
            "name": s.name,
            "return_period_years": s.return_period_years,
        }
        for s in sorted(
            storms,
            key=lambda x: (x.return_period_years or 0, x.name),
        )
    ]

    baseline_entity_metrics: dict[str, dict[ComparisonMetric, float]] = {}
    for entity_id, storm_data in entity_storm_metrics.items():
        if baseline_storm.id in storm_data:
            baseline_entity_metrics[entity_id] = storm_data[baseline_storm.id]

    metric_rows: list[StormSensitivityMetric] = []

    for entity_id, storm_data in entity_storm_metrics.items():
        entity_name = _get_entity_name(scenario, entity_id, entity_type)
        entity_baseline = baseline_entity_metrics.get(entity_id, {})

        for storm_id, metrics_data in storm_data.items():
            storm = storms_in_results[storm_id]

            for metric in ComparisonMetric:
                value = metrics_data.get(metric)
                baseline_value = entity_baseline.get(metric)

                if value is None:
                    row = StormSensitivityMetric(
                        entity_id=entity_id,
                        entity_name=entity_name,
                        entity_type=entity_type,
                        storm_event_id=storm.id,
                        storm_event_name=storm.name,
                        return_period_years=storm.return_period_years,
                        metric=metric,
                        value=None,
                        unit=METRIC_UNITS.get(metric, ""),
                        baseline_value=baseline_value,
                        delta=None,
                        percent_delta=None,
                        status=StormSensitivityStatus.MISSING_METRIC,
                        percent_delta_status=PercentDeltaStatus.NOT_APPLICABLE,
                    )
                elif baseline_value is None and storm.id != baseline_storm.id:
                    row = StormSensitivityMetric(
                        entity_id=entity_id,
                        entity_name=entity_name,
                        entity_type=entity_type,
                        storm_event_id=storm.id,
                        storm_event_name=storm.name,
                        return_period_years=storm.return_period_years,
                        metric=metric,
                        value=value,
                        unit=METRIC_UNITS.get(metric, ""),
                        baseline_value=None,
                        delta=None,
                        percent_delta=None,
                        status=StormSensitivityStatus.MISSING_BASELINE,
                        percent_delta_status=PercentDeltaStatus.NOT_APPLICABLE,
                    )
                else:
                    delta = compute_delta(baseline_value, value)
                    percent_delta, percent_status = compute_percent_delta(
                        baseline_value, value
                    )

                    row = StormSensitivityMetric(
                        entity_id=entity_id,
                        entity_name=entity_name,
                        entity_type=entity_type,
                        storm_event_id=storm.id,
                        storm_event_name=storm.name,
                        return_period_years=storm.return_period_years,
                        metric=metric,
                        value=value,
                        unit=METRIC_UNITS.get(metric, ""),
                        baseline_value=baseline_value,
                        delta=delta,
                        percent_delta=percent_delta,
                        status=StormSensitivityStatus.OK,
                        percent_delta_status=percent_status,
                    )

                metric_rows.append(row)

    additive_metrics = ComparisonMetric.additive_metrics()
    totals: list[StormSensitivityTotals] = []

    baseline_totals: dict[ComparisonMetric, float] = {}
    for metric in additive_metrics:
        total = 0.0
        for entity_id, metrics_data in baseline_entity_metrics.items():
            if metric in metrics_data:
                total += metrics_data[metric]
        baseline_totals[metric] = total

    for storm in storms:
        storm_entity_count = sum(
            1 for entity_id, storm_data in entity_storm_metrics.items()
            if storm.id in storm_data
        )

        for metric in additive_metrics:
            storm_total = 0.0
            for entity_id, storm_data in entity_storm_metrics.items():
                if storm.id in storm_data and metric in storm_data[storm.id]:
                    storm_total += storm_data[storm.id][metric]

            baseline_total = baseline_totals.get(metric, 0.0)
            delta = compute_delta(baseline_total, storm_total)
            percent_delta, percent_status = compute_percent_delta(
                baseline_total, storm_total
            )

            totals.append(StormSensitivityTotals(
                storm_event_id=storm.id,
                storm_event_name=storm.name,
                return_period_years=storm.return_period_years,
                metric=metric,
                total=storm_total,
                unit=METRIC_UNITS.get(metric, ""),
                baseline_total=baseline_total,
                delta=delta,
                percent_delta=percent_delta,
                entity_count=storm_entity_count,
                percent_delta_status=percent_status,
            ))

    return StormSensitivityResult(
        scenario_id=scenario.id,
        scenario_name=scenario.name,
        baseline_storm_id=baseline_storm.id,
        baseline_storm_name=baseline_storm.name,
        baseline_return_period=baseline_storm.return_period_years,
        storm_events=storm_events_info,
        metrics=metric_rows,
        totals=totals,
        entity_type=entity_type,
    )
