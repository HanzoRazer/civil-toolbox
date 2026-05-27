"""Tests for storm sensitivity comparison."""

import pytest
from datetime import datetime, timezone

from civil_toolbox.comparison.storm_sensitivity import (
    StormSensitivityStatus,
    StormSensitivityMetric,
    StormSensitivityTotals,
    StormSensitivityResult,
    compare_scenario_across_storms,
)
from civil_toolbox.comparison.models import (
    ComparisonMetric,
    PercentDeltaStatus,
)
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.calculation import CalculationResult


def make_scenario_with_storms(
    name: str,
    storms: list[tuple[str, str, int | None]],
    areas: list[tuple[str, str]],
    results: list[tuple[str, str, dict[str, float]]],
) -> Scenario:
    """Create a scenario with storm events and calculation results.

    Args:
        name: Scenario name.
        storms: List of (storm_id, storm_name, return_period_years) tuples.
        areas: List of (area_id, area_name) tuples.
        results: List of (area_id, storm_id, {metric: value}) tuples.

    Returns:
        Scenario with storms, areas, and results.
    """
    scenario = Scenario(name=name)

    for storm_id, storm_name, return_period in storms:
        storm = StormEvent(id=storm_id, name=storm_name, return_period_years=return_period)
        scenario.storm_events.append(storm)

    for area_id, area_name in areas:
        area = DrainageArea(id=area_id, name=area_name)
        scenario.add_drainage_area(area)

    for area_id, storm_id, outputs in results:
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id=area_id,
                entity_type="DrainageArea",
                outputs=outputs,
                units={k: "cfs" if "flow" in k else "in" for k in outputs},
                metadata={"storm_event_id": storm_id},
            )
        )

    return scenario


class TestStormSensitivityStatus:
    """Tests for StormSensitivityStatus enum."""

    def test_ok_value(self):
        """OK status has correct value."""
        assert StormSensitivityStatus.OK.value == "ok"

    def test_missing_metric_value(self):
        """MISSING_METRIC status has correct value."""
        assert StormSensitivityStatus.MISSING_METRIC.value == "missing_metric"

    def test_missing_baseline_value(self):
        """MISSING_BASELINE status has correct value."""
        assert StormSensitivityStatus.MISSING_BASELINE.value == "missing_baseline"


class TestStormSensitivityMetric:
    """Tests for StormSensitivityMetric dataclass."""

    def test_creates_metric_row(self):
        """Creates metric row with all fields."""
        row = StormSensitivityMetric(
            entity_id="area-1",
            entity_name="Area A",
            entity_type="DrainageArea",
            storm_event_id="storm-100",
            storm_event_name="100-year",
            return_period_years=100,
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            value=150.0,
            unit="cfs",
            baseline_value=100.0,
            delta=50.0,
            percent_delta=50.0,
            status=StormSensitivityStatus.OK,
            percent_delta_status=PercentDeltaStatus.OK,
        )

        assert row.entity_id == "area-1"
        assert row.storm_event_name == "100-year"
        assert row.value == 150.0
        assert row.delta == 50.0

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        row = StormSensitivityMetric(
            entity_id="area-1",
            entity_name="Area A",
            entity_type="DrainageArea",
            storm_event_id="storm-100",
            storm_event_name="100-year",
            return_period_years=100,
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            value=150.0,
            unit="cfs",
            baseline_value=100.0,
            delta=50.0,
            percent_delta=50.0,
        )

        data = row.to_dict()

        assert data["entity_id"] == "area-1"
        assert data["metric"] == "peak_flow_cfs"
        assert data["status"] == "ok"

    def test_deserializes_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "entity_id": "area-1",
            "entity_name": "Area A",
            "entity_type": "DrainageArea",
            "storm_event_id": "storm-100",
            "storm_event_name": "100-year",
            "return_period_years": 100,
            "metric": "peak_flow_cfs",
            "value": 150.0,
            "unit": "cfs",
            "baseline_value": 100.0,
            "delta": 50.0,
            "percent_delta": 50.0,
            "status": "ok",
            "percent_delta_status": "ok",
        }

        row = StormSensitivityMetric.from_dict(data)

        assert row.entity_id == "area-1"
        assert row.metric == ComparisonMetric.PEAK_FLOW_CFS
        assert row.status == StormSensitivityStatus.OK


class TestStormSensitivityTotals:
    """Tests for StormSensitivityTotals dataclass."""

    def test_creates_totals(self):
        """Creates totals with all fields."""
        totals = StormSensitivityTotals(
            storm_event_id="storm-100",
            storm_event_name="100-year",
            return_period_years=100,
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            total=500.0,
            unit="cfs",
            baseline_total=300.0,
            delta=200.0,
            percent_delta=66.67,
            entity_count=3,
        )

        assert totals.total == 500.0
        assert totals.entity_count == 3

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        totals = StormSensitivityTotals(
            storm_event_id="storm-100",
            storm_event_name="100-year",
            return_period_years=100,
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            total=500.0,
            unit="cfs",
            baseline_total=300.0,
            delta=200.0,
            percent_delta=66.67,
            entity_count=3,
        )

        data = totals.to_dict()

        assert data["total"] == 500.0
        assert data["metric"] == "peak_flow_cfs"

    def test_deserializes_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "storm_event_id": "storm-100",
            "storm_event_name": "100-year",
            "return_period_years": 100,
            "metric": "peak_flow_cfs",
            "total": 500.0,
            "unit": "cfs",
            "baseline_total": 300.0,
            "delta": 200.0,
            "percent_delta": 66.67,
            "entity_count": 3,
            "percent_delta_status": "ok",
        }

        totals = StormSensitivityTotals.from_dict(data)

        assert totals.total == 500.0
        assert totals.metric == ComparisonMetric.PEAK_FLOW_CFS


class TestStormSensitivityResult:
    """Tests for StormSensitivityResult dataclass."""

    def test_creates_result(self):
        """Creates result with all fields."""
        result = StormSensitivityResult(
            scenario_id="s-1",
            scenario_name="Proposed",
            baseline_storm_id="storm-10",
            baseline_storm_name="10-year",
            baseline_return_period=10,
            storm_events=[],
            metrics=[],
            totals=[],
            entity_type="DrainageArea",
        )

        assert result.scenario_name == "Proposed"
        assert result.baseline_storm_name == "10-year"

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        result = StormSensitivityResult(
            scenario_id="s-1",
            scenario_name="Proposed",
            baseline_storm_id="storm-10",
            baseline_storm_name="10-year",
            baseline_return_period=10,
        )

        data = result.to_dict()

        assert data["scenario_name"] == "Proposed"
        assert "created_at" in data

    def test_deserializes_from_dict(self):
        """Deserializes from dictionary."""
        data = {
            "scenario_id": "s-1",
            "scenario_name": "Proposed",
            "baseline_storm_id": "storm-10",
            "baseline_storm_name": "10-year",
            "baseline_return_period": 10,
            "storm_events": [],
            "metrics": [],
            "totals": [],
            "entity_type": "DrainageArea",
            "created_at": "2026-05-21T00:00:00+00:00",
        }

        result = StormSensitivityResult.from_dict(data)

        assert result.scenario_name == "Proposed"
        assert result.baseline_return_period == 10

    def test_round_trip_serialization(self):
        """Result round-trips through serialization."""
        metric_row = StormSensitivityMetric(
            entity_id="area-1",
            entity_name="Area A",
            entity_type="DrainageArea",
            storm_event_id="storm-100",
            storm_event_name="100-year",
            return_period_years=100,
            metric=ComparisonMetric.PEAK_FLOW_CFS,
            value=150.0,
            unit="cfs",
            baseline_value=100.0,
            delta=50.0,
            percent_delta=50.0,
        )

        original = StormSensitivityResult(
            scenario_id="s-1",
            scenario_name="Proposed",
            baseline_storm_id="storm-10",
            baseline_storm_name="10-year",
            baseline_return_period=10,
            metrics=[metric_row],
        )

        restored = StormSensitivityResult.from_dict(original.to_dict())

        assert restored.scenario_name == original.scenario_name
        assert len(restored.metrics) == 1
        assert restored.metrics[0].delta == 50.0

    def test_get_metrics_for_entity(self):
        """Gets metrics filtered by entity."""
        result = StormSensitivityResult(
            scenario_id="s-1",
            scenario_name="Test",
            baseline_storm_id="storm-10",
            baseline_storm_name="10-year",
            baseline_return_period=10,
            metrics=[
                StormSensitivityMetric(
                    entity_id="area-1",
                    entity_name="Area A",
                    entity_type="DrainageArea",
                    storm_event_id="storm-10",
                    storm_event_name="10-year",
                    return_period_years=10,
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    value=100.0,
                    unit="cfs",
                    baseline_value=100.0,
                    delta=0.0,
                    percent_delta=0.0,
                ),
                StormSensitivityMetric(
                    entity_id="area-2",
                    entity_name="Area B",
                    entity_type="DrainageArea",
                    storm_event_id="storm-10",
                    storm_event_name="10-year",
                    return_period_years=10,
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    value=200.0,
                    unit="cfs",
                    baseline_value=200.0,
                    delta=0.0,
                    percent_delta=0.0,
                ),
            ],
        )

        area_1_metrics = result.get_metrics_for_entity("area-1")

        assert len(area_1_metrics) == 1
        assert area_1_metrics[0].entity_name == "Area A"

    def test_get_metrics_for_storm(self):
        """Gets metrics filtered by storm."""
        result = StormSensitivityResult(
            scenario_id="s-1",
            scenario_name="Test",
            baseline_storm_id="storm-10",
            baseline_storm_name="10-year",
            baseline_return_period=10,
            metrics=[
                StormSensitivityMetric(
                    entity_id="area-1",
                    entity_name="Area A",
                    entity_type="DrainageArea",
                    storm_event_id="storm-10",
                    storm_event_name="10-year",
                    return_period_years=10,
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    value=100.0,
                    unit="cfs",
                    baseline_value=100.0,
                    delta=0.0,
                    percent_delta=0.0,
                ),
                StormSensitivityMetric(
                    entity_id="area-1",
                    entity_name="Area A",
                    entity_type="DrainageArea",
                    storm_event_id="storm-100",
                    storm_event_name="100-year",
                    return_period_years=100,
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    value=200.0,
                    unit="cfs",
                    baseline_value=100.0,
                    delta=100.0,
                    percent_delta=100.0,
                ),
            ],
        )

        storm_100_metrics = result.get_metrics_for_storm("storm-100")

        assert len(storm_100_metrics) == 1
        assert storm_100_metrics[0].storm_event_name == "100-year"

    def test_get_totals_for_storm(self):
        """Gets totals filtered by storm."""
        result = StormSensitivityResult(
            scenario_id="s-1",
            scenario_name="Test",
            baseline_storm_id="storm-10",
            baseline_storm_name="10-year",
            baseline_return_period=10,
            totals=[
                StormSensitivityTotals(
                    storm_event_id="storm-10",
                    storm_event_name="10-year",
                    return_period_years=10,
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    total=300.0,
                    unit="cfs",
                    baseline_total=300.0,
                    delta=0.0,
                    percent_delta=0.0,
                    entity_count=3,
                ),
                StormSensitivityTotals(
                    storm_event_id="storm-100",
                    storm_event_name="100-year",
                    return_period_years=100,
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    total=600.0,
                    unit="cfs",
                    baseline_total=300.0,
                    delta=300.0,
                    percent_delta=100.0,
                    entity_count=3,
                ),
            ],
        )

        storm_100_totals = result.get_totals_for_storm("storm-100")

        assert len(storm_100_totals) == 1
        assert storm_100_totals[0].total == 600.0


class TestCompareScenarioAcrossStorms:
    """Tests for compare_scenario_across_storms function."""

    def test_compares_across_storms(self):
        """Compares a scenario across multiple storm events."""
        scenario = make_scenario_with_storms(
            name="Proposed",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 200.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        assert result.scenario_name == "Proposed"
        assert result.baseline_storm_name == "10-year"
        assert len(result.storm_events) == 2

    def test_selects_lowest_return_period_as_baseline(self):
        """Selects storm with lowest return period as baseline."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-100", "100-year", 100),
                ("storm-10", "10-year", 10),
                ("storm-25", "25-year", 25),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-25", {"peak_flow_cfs": 150.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 200.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        assert result.baseline_storm_id == "storm-10"
        assert result.baseline_return_period == 10

    def test_uses_explicit_baseline_storm(self):
        """Uses explicitly specified baseline storm."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-25", "25-year", 25),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-25", {"peak_flow_cfs": 150.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario, baseline_storm_id="storm-25")

        assert result.baseline_storm_id == "storm-25"
        assert result.baseline_storm_name == "25-year"

    def test_computes_deltas_from_baseline(self):
        """Computes deltas relative to baseline storm."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 150.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        storm_100_metrics = result.get_metrics_for_storm("storm-100")
        peak_flow_row = next(
            m for m in storm_100_metrics
            if m.metric == ComparisonMetric.PEAK_FLOW_CFS
        )

        assert peak_flow_row.baseline_value == 100.0
        assert peak_flow_row.value == 150.0
        assert peak_flow_row.delta == 50.0
        assert peak_flow_row.percent_delta == 50.0

    def test_baseline_storm_has_zero_delta(self):
        """Baseline storm shows zero delta."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 150.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        baseline_metrics = result.get_metrics_for_storm("storm-10")
        peak_flow_row = next(
            m for m in baseline_metrics
            if m.metric == ComparisonMetric.PEAK_FLOW_CFS
        )

        assert peak_flow_row.delta == 0.0
        assert peak_flow_row.percent_delta == 0.0

    def test_includes_multiple_entities(self):
        """Includes metrics for multiple entities."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[
                ("area-1", "Area A"),
                ("area-2", "Area B"),
            ],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 200.0}),
                ("area-2", "storm-10", {"peak_flow_cfs": 150.0}),
                ("area-2", "storm-100", {"peak_flow_cfs": 300.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        area_1_metrics = result.get_metrics_for_entity("area-1")
        area_2_metrics = result.get_metrics_for_entity("area-2")

        assert len(area_1_metrics) > 0
        assert len(area_2_metrics) > 0

    def test_computes_additive_totals(self):
        """Computes scenario totals for additive metrics."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[
                ("area-1", "Area A"),
                ("area-2", "Area B"),
            ],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 200.0}),
                ("area-2", "storm-10", {"peak_flow_cfs": 150.0}),
                ("area-2", "storm-100", {"peak_flow_cfs": 300.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        storm_100_totals = result.get_totals_for_storm("storm-100")
        peak_total = next(
            t for t in storm_100_totals
            if t.metric == ComparisonMetric.PEAK_FLOW_CFS
        )

        assert peak_total.total == 500.0
        assert peak_total.baseline_total == 250.0
        assert peak_total.delta == 250.0
        assert peak_total.entity_count == 2

    def test_handles_missing_metric(self):
        """Handles missing metric for a storm event."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        assert len(result.metrics) > 0
        assert result.baseline_storm_id == "storm-10"

    def test_handles_missing_baseline_metric(self):
        """Handles entity missing from baseline storm."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[
                ("area-1", "Area A"),
                ("area-2", "Area B"),
            ],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 200.0}),
                ("area-2", "storm-100", {"peak_flow_cfs": 300.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        area_2_storm_100_metrics = [
            m for m in result.metrics
            if m.entity_id == "area-2"
            and m.storm_event_id == "storm-100"
            and m.metric == ComparisonMetric.PEAK_FLOW_CFS
        ]

        assert len(area_2_storm_100_metrics) == 1
        row = area_2_storm_100_metrics[0]
        assert row.status == StormSensitivityStatus.MISSING_BASELINE
        assert row.baseline_value is None
        assert row.delta is None

    def test_handles_zero_baseline(self):
        """Handles zero baseline value."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-10", "10-year", 10),
                ("storm-100", "100-year", 100),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 0.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 100.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        storm_100_metrics = result.get_metrics_for_storm("storm-100")
        peak_flow_row = next(
            m for m in storm_100_metrics
            if m.metric == ComparisonMetric.PEAK_FLOW_CFS
        )

        assert peak_flow_row.delta == 100.0
        assert peak_flow_row.percent_delta is None
        assert peak_flow_row.percent_delta_status == PercentDeltaStatus.UNDEFINED_ZERO_BASELINE

    def test_handles_no_storms(self):
        """Returns empty result when no storms have results."""
        scenario = Scenario(name="Empty")

        result = compare_scenario_across_storms(scenario)

        assert result.baseline_storm_id == ""
        assert len(result.metrics) == 0
        assert len(result.totals) == 0

    def test_sorts_storm_events_by_return_period(self):
        """Storm events are sorted by return period."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-100", "100-year", 100),
                ("storm-10", "10-year", 10),
                ("storm-25", "25-year", 25),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-25", {"peak_flow_cfs": 150.0}),
                ("area-1", "storm-100", {"peak_flow_cfs": 200.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        return_periods = [s["return_period_years"] for s in result.storm_events]
        assert return_periods == [10, 25, 100]

    def test_uses_storm_event_name_fallback(self):
        """Falls back to storm_event_name if storm_event_id not in metadata."""
        scenario = Scenario(name="Test")
        storm = StormEvent(id="storm-10", name="10-year", return_period_years=10)
        scenario.storm_events.append(storm)
        area = DrainageArea(id="area-1", name="Area A")
        scenario.add_drainage_area(area)
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
                metadata={"storm_event_name": "10-year"},
            )
        )

        result = compare_scenario_across_storms(scenario)

        assert result.baseline_storm_id == "storm-10"
        assert len(result.metrics) > 0

    def test_filters_by_entity_type(self):
        """Only compares entities of specified type."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[("storm-10", "10-year", 10)],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-10", {"peak_flow_cfs": 100.0}),
            ],
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="time_of_concentration",
                entity_id="path-1",
                entity_type="FlowPath",
                outputs={"time_of_concentration_min": 15.0},
                metadata={"storm_event_id": "storm-10"},
            )
        )

        result = compare_scenario_across_storms(scenario, entity_type="DrainageArea")

        entity_types = {m.entity_type for m in result.metrics}
        assert entity_types == {"DrainageArea"}

    def test_handles_storms_without_return_period(self):
        """Handles storms without return period."""
        scenario = make_scenario_with_storms(
            name="Test",
            storms=[
                ("storm-a", "Storm A", None),
                ("storm-b", "Storm B", None),
            ],
            areas=[("area-1", "Area A")],
            results=[
                ("area-1", "storm-a", {"peak_flow_cfs": 100.0}),
                ("area-1", "storm-b", {"peak_flow_cfs": 150.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        assert result.baseline_return_period is None
        assert len(result.metrics) > 0


class TestStormSensitivityIntegration:
    """Integration tests for storm sensitivity comparison."""

    def test_full_comparison_workflow(self):
        """Complete workflow from scenario to sensitivity result."""
        scenario = make_scenario_with_storms(
            name="Development Site",
            storms=[
                ("storm-2", "2-year", 2),
                ("storm-10", "10-year", 10),
                ("storm-25", "25-year", 25),
                ("storm-100", "100-year", 100),
            ],
            areas=[
                ("basin-a", "Basin A"),
                ("basin-b", "Basin B"),
            ],
            results=[
                ("basin-a", "storm-2", {"peak_flow_cfs": 50.0, "runoff_volume_cuft": 10000.0}),
                ("basin-a", "storm-10", {"peak_flow_cfs": 100.0, "runoff_volume_cuft": 20000.0}),
                ("basin-a", "storm-25", {"peak_flow_cfs": 150.0, "runoff_volume_cuft": 30000.0}),
                ("basin-a", "storm-100", {"peak_flow_cfs": 200.0, "runoff_volume_cuft": 40000.0}),
                ("basin-b", "storm-2", {"peak_flow_cfs": 75.0, "runoff_volume_cuft": 15000.0}),
                ("basin-b", "storm-10", {"peak_flow_cfs": 150.0, "runoff_volume_cuft": 30000.0}),
                ("basin-b", "storm-25", {"peak_flow_cfs": 225.0, "runoff_volume_cuft": 45000.0}),
                ("basin-b", "storm-100", {"peak_flow_cfs": 300.0, "runoff_volume_cuft": 60000.0}),
            ],
        )

        result = compare_scenario_across_storms(scenario)

        assert result.baseline_storm_name == "2-year"
        assert len(result.storm_events) == 4

        storm_100_totals = result.get_totals_for_storm("storm-100")
        peak_total = next(
            t for t in storm_100_totals
            if t.metric == ComparisonMetric.PEAK_FLOW_CFS
        )
        assert peak_total.total == 500.0
        assert peak_total.baseline_total == 125.0
        assert peak_total.delta == 375.0

        data = result.to_dict()
        restored = StormSensitivityResult.from_dict(data)
        assert restored.scenario_name == result.scenario_name
        assert len(restored.metrics) == len(result.metrics)
