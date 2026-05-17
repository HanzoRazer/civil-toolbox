"""Tests for comparison data models."""

import pytest
from datetime import datetime, timezone

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


class TestComparisonMetric:
    """Tests for ComparisonMetric enum."""

    def test_all_metrics_defined(self):
        """All four recognized metrics exist."""
        assert ComparisonMetric.PEAK_FLOW_CFS.value == "peak_flow_cfs"
        assert ComparisonMetric.RUNOFF_DEPTH_IN.value == "runoff_depth_in"
        assert ComparisonMetric.RUNOFF_VOLUME_CUFT.value == "runoff_volume_cuft"
        assert ComparisonMetric.TIME_OF_CONCENTRATION_MIN.value == "time_of_concentration_min"

    def test_additive_metrics(self):
        """Additive metrics are peak flow and runoff volume only."""
        additive = ComparisonMetric.additive_metrics()
        assert ComparisonMetric.PEAK_FLOW_CFS in additive
        assert ComparisonMetric.RUNOFF_VOLUME_CUFT in additive
        assert ComparisonMetric.RUNOFF_DEPTH_IN not in additive
        assert ComparisonMetric.TIME_OF_CONCENTRATION_MIN not in additive

    def test_from_output_key_recognized(self):
        """from_output_key returns metric for recognized keys."""
        assert ComparisonMetric.from_output_key("peak_flow_cfs") == ComparisonMetric.PEAK_FLOW_CFS
        assert ComparisonMetric.from_output_key("runoff_depth_in") == ComparisonMetric.RUNOFF_DEPTH_IN

    def test_from_output_key_unrecognized(self):
        """from_output_key returns None for unrecognized keys."""
        assert ComparisonMetric.from_output_key("unknown_metric") is None
        assert ComparisonMetric.from_output_key("") is None


class TestComparisonStatus:
    """Tests for ComparisonStatus enum."""

    def test_all_statuses_defined(self):
        """All status values exist."""
        assert ComparisonStatus.OK.value == "ok"
        assert ComparisonStatus.MISSING_BASELINE.value == "missing_baseline"
        assert ComparisonStatus.MISSING_COMPARISON.value == "missing_comparison"


class TestPercentDeltaStatus:
    """Tests for PercentDeltaStatus enum."""

    def test_all_statuses_defined(self):
        """All percent delta status values exist."""
        assert PercentDeltaStatus.OK.value == "ok"
        assert PercentDeltaStatus.UNDEFINED_ZERO_BASELINE.value == "undefined_zero_baseline"
        assert PercentDeltaStatus.NOT_APPLICABLE.value == "not_applicable"


class TestMatchStrategy:
    """Tests for MatchStrategy enum."""

    def test_all_strategies_defined(self):
        """All match strategies exist."""
        assert MatchStrategy.AUTO.value == "auto"
        assert MatchStrategy.ID.value == "id"
        assert MatchStrategy.NAME.value == "name"
        assert MatchStrategy.EXPLICIT.value == "explicit"


class TestMetricComparisonResult:
    """Tests for MetricComparisonResult."""

    def test_creates_with_values(self):
        """Creates result with baseline and comparison values."""
        result = MetricComparisonResult(
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            baseline_value=100.0,
            comparison_value=120.0,
            delta=20.0,
            percent_delta=20.0,
            unit="cfs",
        )
        assert result.metric == ComparisonMetric.PEAK_FLOW_CFS
        assert result.baseline_value == 100.0
        assert result.comparison_value == 120.0
        assert result.delta == 20.0
        assert result.percent_delta == 20.0
        assert result.unit == "cfs"
        assert result.status == ComparisonStatus.OK
        assert result.percent_delta_status == PercentDeltaStatus.OK

    def test_creates_with_missing_comparison(self):
        """Creates result with missing comparison value."""
        result = MetricComparisonResult(
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            baseline_value=100.0,
            comparison_value=None,
            delta=None,
            percent_delta=None,
            unit="cfs",
            status=ComparisonStatus.MISSING_COMPARISON,
            percent_delta_status=PercentDeltaStatus.NOT_APPLICABLE,
        )
        assert result.baseline_value == 100.0
        assert result.comparison_value is None
        assert result.delta is None
        assert result.status == ComparisonStatus.MISSING_COMPARISON

    def test_creates_with_zero_baseline(self):
        """Creates result with zero baseline."""
        result = MetricComparisonResult(
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            baseline_value=0.0,
            comparison_value=50.0,
            delta=50.0,
            percent_delta=None,
            unit="cfs",
            percent_delta_status=PercentDeltaStatus.UNDEFINED_ZERO_BASELINE,
        )
        assert result.baseline_value == 0.0
        assert result.delta == 50.0
        assert result.percent_delta is None
        assert result.percent_delta_status == PercentDeltaStatus.UNDEFINED_ZERO_BASELINE

    def test_to_dict(self):
        """Serializes to dictionary."""
        result = MetricComparisonResult(
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            baseline_value=100.0,
            comparison_value=120.0,
            delta=20.0,
            percent_delta=20.0,
            unit="cfs",
        )
        data = result.to_dict()
        assert data["metric"] == "peak_flow_cfs"
        assert data["baseline_value"] == 100.0
        assert data["comparison_value"] == 120.0
        assert data["delta"] == 20.0
        assert data["percent_delta"] == 20.0
        assert data["unit"] == "cfs"
        assert data["status"] == "ok"
        assert data["percent_delta_status"] == "ok"

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "metric": "runoff_depth_in",
            "baseline_value": 2.5,
            "comparison_value": 3.0,
            "delta": 0.5,
            "percent_delta": 20.0,
            "unit": "in",
            "status": "ok",
            "percent_delta_status": "ok",
        }
        result = MetricComparisonResult.from_dict(data)
        assert result.metric == ComparisonMetric.RUNOFF_DEPTH_IN
        assert result.baseline_value == 2.5
        assert result.comparison_value == 3.0

    def test_round_trip_serialization(self):
        """Round-trip serialization preserves data."""
        original = MetricComparisonResult(
            metric=ComparisonMetric.RUNOFF_VOLUME_CUFT,
            baseline_value=50000.0,
            comparison_value=None,
            delta=None,
            percent_delta=None,
            unit="cf",
            status=ComparisonStatus.MISSING_COMPARISON,
            percent_delta_status=PercentDeltaStatus.NOT_APPLICABLE,
        )
        restored = MetricComparisonResult.from_dict(original.to_dict())
        assert restored.metric == original.metric
        assert restored.baseline_value == original.baseline_value
        assert restored.comparison_value == original.comparison_value
        assert restored.status == original.status


class TestEntityComparisonResult:
    """Tests for EntityComparisonResult."""

    def test_creates_with_entity_info(self):
        """Creates result with entity identification."""
        result = EntityComparisonResult(
            baseline_entity_id="area-1",
            comparison_entity_id="area-1-proposed",
            entity_name="Drainage Area A",
            entity_type="DrainageArea",
        )
        assert result.baseline_entity_id == "area-1"
        assert result.comparison_entity_id == "area-1-proposed"
        assert result.entity_name == "Drainage Area A"
        assert result.entity_type == "DrainageArea"
        assert result.metrics == {}

    def test_adds_metric_results(self):
        """Adds metric comparison results."""
        result = EntityComparisonResult(
            baseline_entity_id="area-1",
            comparison_entity_id="area-1-proposed",
            entity_name="Area A",
            entity_type="DrainageArea",
        )
        metric_result = MetricComparisonResult(
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            baseline_value=100.0,
            comparison_value=120.0,
            delta=20.0,
            percent_delta=20.0,
            unit="cfs",
        )
        result.metrics[ComparisonMetric.PEAK_FLOW_CFS] = metric_result
        assert ComparisonMetric.PEAK_FLOW_CFS in result.metrics
        assert result.metrics[ComparisonMetric.PEAK_FLOW_CFS].baseline_value == 100.0

    def test_to_dict(self):
        """Serializes to dictionary."""
        result = EntityComparisonResult(
            baseline_entity_id="area-1",
            comparison_entity_id="area-1-proposed",
            entity_name="Area A",
            entity_type="DrainageArea",
            metrics={
                ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    baseline_value=100.0,
                    comparison_value=120.0,
                    delta=20.0,
                    percent_delta=20.0,
                    unit="cfs",
                )
            },
        )
        data = result.to_dict()
        assert data["baseline_entity_id"] == "area-1"
        assert "peak_flow_cfs" in data["metrics"]
        assert data["metrics"]["peak_flow_cfs"]["baseline_value"] == 100.0

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "baseline_entity_id": "area-1",
            "comparison_entity_id": "area-2",
            "entity_name": "Area A",
            "entity_type": "DrainageArea",
            "metrics": {
                "peak_flow_cfs": {
                    "metric": "peak_flow_cfs",
                    "baseline_value": 100.0,
                    "comparison_value": 120.0,
                    "delta": 20.0,
                    "percent_delta": 20.0,
                    "unit": "cfs",
                    "status": "ok",
                    "percent_delta_status": "ok",
                }
            },
        }
        result = EntityComparisonResult.from_dict(data)
        assert result.baseline_entity_id == "area-1"
        assert ComparisonMetric.PEAK_FLOW_CFS in result.metrics


class TestScenarioTotals:
    """Tests for ScenarioTotals."""

    def test_creates_with_totals(self):
        """Creates totals with aggregated values."""
        totals = ScenarioTotals(
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            baseline_total=500.0,
            comparison_total=600.0,
            delta=100.0,
            percent_delta=20.0,
            unit="cfs",
            entity_count=5,
        )
        assert totals.metric == ComparisonMetric.PEAK_FLOW_CFS
        assert totals.baseline_total == 500.0
        assert totals.comparison_total == 600.0
        assert totals.delta == 100.0
        assert totals.entity_count == 5

    def test_to_dict(self):
        """Serializes to dictionary."""
        totals = ScenarioTotals(
            metric=ComparisonMetric.RUNOFF_VOLUME_CUFT,
            baseline_total=100000.0,
            comparison_total=120000.0,
            delta=20000.0,
            percent_delta=20.0,
            unit="cf",
            entity_count=3,
        )
        data = totals.to_dict()
        assert data["metric"] == "runoff_volume_cuft"
        assert data["baseline_total"] == 100000.0
        assert data["entity_count"] == 3

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "metric": "peak_flow_cfs",
            "baseline_total": 500.0,
            "comparison_total": 600.0,
            "delta": 100.0,
            "percent_delta": 20.0,
            "unit": "cfs",
            "entity_count": 5,
            "percent_delta_status": "ok",
        }
        totals = ScenarioTotals.from_dict(data)
        assert totals.metric == ComparisonMetric.PEAK_FLOW_CFS
        assert totals.baseline_total == 500.0


class TestScenarioComparisonResult:
    """Tests for ScenarioComparisonResult."""

    def test_creates_with_scenario_info(self):
        """Creates result with scenario identification."""
        result = ScenarioComparisonResult(
            baseline_scenario_id="scenario-1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="scenario-2",
            comparison_scenario_name="Proposed",
            storm_event_name="100-year",
            match_strategy=MatchStrategy.AUTO,
        )
        assert result.baseline_scenario_id == "scenario-1"
        assert result.baseline_scenario_name == "Existing"
        assert result.comparison_scenario_id == "scenario-2"
        assert result.comparison_scenario_name == "Proposed"
        assert result.storm_event_name == "100-year"
        assert result.match_strategy == MatchStrategy.AUTO
        assert result.entity_comparisons == []
        assert result.totals == {}
        assert isinstance(result.created_at, datetime)

    def test_tracks_unmatched_entities(self):
        """Tracks entities that could not be matched."""
        result = ScenarioComparisonResult(
            baseline_scenario_id="scenario-1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="scenario-2",
            comparison_scenario_name="Proposed",
            storm_event_name="100-year",
            match_strategy=MatchStrategy.NAME,
            unmatched_baseline_ids=["area-orphan-1"],
            unmatched_comparison_ids=["area-new-1", "area-new-2"],
        )
        assert result.unmatched_baseline_ids == ["area-orphan-1"]
        assert result.unmatched_comparison_ids == ["area-new-1", "area-new-2"]

    def test_to_dict(self):
        """Serializes to dictionary."""
        result = ScenarioComparisonResult(
            baseline_scenario_id="scenario-1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="scenario-2",
            comparison_scenario_name="Proposed",
            storm_event_name="100-year",
            match_strategy=MatchStrategy.EXPLICIT,
        )
        data = result.to_dict()
        assert data["baseline_scenario_id"] == "scenario-1"
        assert data["baseline_scenario_name"] == "Existing"
        assert data["storm_event_name"] == "100-year"
        assert data["match_strategy"] == "explicit"
        assert "created_at" in data

    def test_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "baseline_scenario_id": "scenario-1",
            "baseline_scenario_name": "Existing",
            "comparison_scenario_id": "scenario-2",
            "comparison_scenario_name": "Proposed",
            "storm_event_name": "100-year",
            "match_strategy": "auto",
            "entity_comparisons": [],
            "totals": {},
            "unmatched_baseline_ids": [],
            "unmatched_comparison_ids": [],
            "created_at": "2026-05-16T00:00:00+00:00",
        }
        result = ScenarioComparisonResult.from_dict(data)
        assert result.baseline_scenario_id == "scenario-1"
        assert result.match_strategy == MatchStrategy.AUTO
        assert result.created_at.year == 2026

    def test_round_trip_serialization(self):
        """Round-trip serialization preserves data."""
        original = ScenarioComparisonResult(
            baseline_scenario_id="scenario-1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="scenario-2",
            comparison_scenario_name="Proposed",
            storm_event_name="100-year",
            match_strategy=MatchStrategy.AUTO,
            entity_comparisons=[
                EntityComparisonResult(
                    baseline_entity_id="area-1",
                    comparison_entity_id="area-1",
                    entity_name="Area A",
                    entity_type="DrainageArea",
                    metrics={
                        ComparisonMetric.PEAK_FLOW_CFS: MetricComparisonResult(
                            metric=ComparisonMetric.PEAK_FLOW_CFS,
                            baseline_value=100.0,
                            comparison_value=120.0,
                            delta=20.0,
                            percent_delta=20.0,
                            unit="cfs",
                        )
                    },
                )
            ],
            totals={
                ComparisonMetric.PEAK_FLOW_CFS: ScenarioTotals(
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    baseline_total=100.0,
                    comparison_total=120.0,
                    delta=20.0,
                    percent_delta=20.0,
                    unit="cfs",
                    entity_count=1,
                )
            },
            unmatched_baseline_ids=["orphan-1"],
            unmatched_comparison_ids=[],
        )
        restored = ScenarioComparisonResult.from_dict(original.to_dict())
        assert restored.baseline_scenario_id == original.baseline_scenario_id
        assert len(restored.entity_comparisons) == 1
        assert ComparisonMetric.PEAK_FLOW_CFS in restored.totals
        assert restored.unmatched_baseline_ids == ["orphan-1"]
