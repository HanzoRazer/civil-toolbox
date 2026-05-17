"""Data models for scenario comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ComparisonMetric(Enum):
    """Recognized metrics for scenario comparison.

    These are the only metrics that can be compared between scenarios.
    Each maps to an output key in CalculationResult.outputs.
    """

    PEAK_FLOW_CFS = "peak_flow_cfs"
    RUNOFF_DEPTH_IN = "runoff_depth_in"
    RUNOFF_VOLUME_CUFT = "runoff_volume_cuft"
    TIME_OF_CONCENTRATION_MIN = "time_of_concentration_min"

    @classmethod
    def additive_metrics(cls) -> set[ComparisonMetric]:
        """Return metrics that can be summed at scenario level."""
        return {cls.PEAK_FLOW_CFS, cls.RUNOFF_VOLUME_CUFT}

    @classmethod
    def from_output_key(cls, key: str) -> ComparisonMetric | None:
        """Get metric from output key, or None if not recognized."""
        for metric in cls:
            if metric.value == key:
                return metric
        return None


class ComparisonStatus(Enum):
    """Status of a metric comparison."""

    OK = "ok"
    MISSING_BASELINE = "missing_baseline"
    MISSING_COMPARISON = "missing_comparison"


class PercentDeltaStatus(Enum):
    """Status of percent delta calculation."""

    OK = "ok"
    UNDEFINED_ZERO_BASELINE = "undefined_zero_baseline"
    NOT_APPLICABLE = "not_applicable"


class MatchStrategy(Enum):
    """Strategy for matching entities between scenarios."""

    AUTO = "auto"
    ID = "id"
    NAME = "name"
    EXPLICIT = "explicit"


@dataclass
class MetricComparisonResult:
    """Result of comparing a single metric between two entities.

    Attributes:
        metric: The metric being compared.
        baseline_value: Value from the baseline scenario.
        comparison_value: Value from the comparison scenario.
        delta: Absolute difference (comparison - baseline).
        percent_delta: Percentage change from baseline.
        unit: Unit of measurement.
        status: Whether both values were present.
        percent_delta_status: Status of percent delta calculation.
    """

    metric: ComparisonMetric
    baseline_value: float | None
    comparison_value: float | None
    delta: float | None
    percent_delta: float | None
    unit: str
    status: ComparisonStatus = ComparisonStatus.OK
    percent_delta_status: PercentDeltaStatus = PercentDeltaStatus.OK

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "metric": self.metric.value,
            "baseline_value": self.baseline_value,
            "comparison_value": self.comparison_value,
            "delta": self.delta,
            "percent_delta": self.percent_delta,
            "unit": self.unit,
            "status": self.status.value,
            "percent_delta_status": self.percent_delta_status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MetricComparisonResult:
        """Deserialize from dictionary."""
        return cls(
            metric=ComparisonMetric(data["metric"]),
            baseline_value=data["baseline_value"],
            comparison_value=data["comparison_value"],
            delta=data["delta"],
            percent_delta=data["percent_delta"],
            unit=data["unit"],
            status=ComparisonStatus(data["status"]),
            percent_delta_status=PercentDeltaStatus(data["percent_delta_status"]),
        )


@dataclass
class EntityComparisonResult:
    """Result of comparing all metrics for a single entity pair.

    Attributes:
        baseline_entity_id: ID of the entity in the baseline scenario.
        comparison_entity_id: ID of the entity in the comparison scenario.
        entity_name: Display name for the entity (from baseline).
        entity_type: Type of entity (e.g., "DrainageArea").
        metrics: Comparison results for each recognized metric.
    """

    baseline_entity_id: str
    comparison_entity_id: str
    entity_name: str
    entity_type: str
    metrics: dict[ComparisonMetric, MetricComparisonResult] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "baseline_entity_id": self.baseline_entity_id,
            "comparison_entity_id": self.comparison_entity_id,
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "metrics": {k.value: v.to_dict() for k, v in self.metrics.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EntityComparisonResult:
        """Deserialize from dictionary."""
        return cls(
            baseline_entity_id=data["baseline_entity_id"],
            comparison_entity_id=data["comparison_entity_id"],
            entity_name=data["entity_name"],
            entity_type=data["entity_type"],
            metrics={
                ComparisonMetric(k): MetricComparisonResult.from_dict(v)
                for k, v in data.get("metrics", {}).items()
            },
        )


@dataclass
class ScenarioTotals:
    """Aggregated totals for additive metrics at scenario level.

    Only additive metrics (peak_flow_cfs, runoff_volume_cuft) are summed.
    """

    metric: ComparisonMetric
    baseline_total: float | None
    comparison_total: float | None
    delta: float | None
    percent_delta: float | None
    unit: str
    entity_count: int
    percent_delta_status: PercentDeltaStatus = PercentDeltaStatus.OK

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "metric": self.metric.value,
            "baseline_total": self.baseline_total,
            "comparison_total": self.comparison_total,
            "delta": self.delta,
            "percent_delta": self.percent_delta,
            "unit": self.unit,
            "entity_count": self.entity_count,
            "percent_delta_status": self.percent_delta_status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScenarioTotals:
        """Deserialize from dictionary."""
        return cls(
            metric=ComparisonMetric(data["metric"]),
            baseline_total=data["baseline_total"],
            comparison_total=data["comparison_total"],
            delta=data["delta"],
            percent_delta=data["percent_delta"],
            unit=data["unit"],
            entity_count=data["entity_count"],
            percent_delta_status=PercentDeltaStatus(data["percent_delta_status"]),
        )


def _utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass
class ScenarioComparisonResult:
    """Complete result of comparing two scenarios.

    Contains per-entity comparisons and scenario-level totals.
    Ephemeral — not persisted to project files.
    """

    baseline_scenario_id: str
    baseline_scenario_name: str
    comparison_scenario_id: str
    comparison_scenario_name: str
    storm_event_name: str | None
    match_strategy: MatchStrategy
    entity_comparisons: list[EntityComparisonResult] = field(default_factory=list)
    totals: dict[ComparisonMetric, ScenarioTotals] = field(default_factory=dict)
    unmatched_baseline_ids: list[str] = field(default_factory=list)
    unmatched_comparison_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "baseline_scenario_id": self.baseline_scenario_id,
            "baseline_scenario_name": self.baseline_scenario_name,
            "comparison_scenario_id": self.comparison_scenario_id,
            "comparison_scenario_name": self.comparison_scenario_name,
            "storm_event_name": self.storm_event_name,
            "match_strategy": self.match_strategy.value,
            "entity_comparisons": [e.to_dict() for e in self.entity_comparisons],
            "totals": {k.value: v.to_dict() for k, v in self.totals.items()},
            "unmatched_baseline_ids": self.unmatched_baseline_ids,
            "unmatched_comparison_ids": self.unmatched_comparison_ids,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScenarioComparisonResult:
        """Deserialize from dictionary."""
        return cls(
            baseline_scenario_id=data["baseline_scenario_id"],
            baseline_scenario_name=data["baseline_scenario_name"],
            comparison_scenario_id=data["comparison_scenario_id"],
            comparison_scenario_name=data["comparison_scenario_name"],
            storm_event_name=data.get("storm_event_name"),
            match_strategy=MatchStrategy(data["match_strategy"]),
            entity_comparisons=[
                EntityComparisonResult.from_dict(e)
                for e in data.get("entity_comparisons", [])
            ],
            totals={
                ComparisonMetric(k): ScenarioTotals.from_dict(v)
                for k, v in data.get("totals", {}).items()
            },
            unmatched_baseline_ids=data.get("unmatched_baseline_ids", []),
            unmatched_comparison_ids=data.get("unmatched_comparison_ids", []),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
