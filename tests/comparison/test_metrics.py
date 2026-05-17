"""Tests for metric extraction."""

import pytest

from civil_toolbox.comparison.metrics import (
    METRIC_UNITS,
    extract_metric_from_result,
    extract_all_metrics_from_result,
    get_metrics_for_entity,
    get_all_entity_metrics,
    ExtractedMetric,
)
from civil_toolbox.comparison.models import ComparisonMetric
from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.scenario import Scenario


class TestMetricUnits:
    """Tests for default metric units."""

    def test_all_metrics_have_units(self):
        """All comparison metrics have default units."""
        for metric in ComparisonMetric:
            assert metric in METRIC_UNITS


class TestExtractMetricFromResult:
    """Tests for extracting single metric from result."""

    def test_extracts_peak_flow(self):
        """Extracts peak flow metric."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            outputs={"peak_flow_cfs": 125.5},
            units={"peak_flow_cfs": "cfs"},
        )

        extracted = extract_metric_from_result(result, ComparisonMetric.PEAK_FLOW_CFS)

        assert extracted is not None
        assert extracted.metric == ComparisonMetric.PEAK_FLOW_CFS
        assert extracted.value == 125.5
        assert extracted.unit == "cfs"
        assert extracted.entity_id == "area-1"
        assert extracted.method == "rational_method"

    def test_extracts_runoff_depth(self):
        """Extracts runoff depth metric."""
        result = CalculationResult(
            method="tr55",
            entity_id="area-1",
            outputs={"runoff_depth_in": 3.2},
            units={"runoff_depth_in": "in"},
        )

        extracted = extract_metric_from_result(result, ComparisonMetric.RUNOFF_DEPTH_IN)

        assert extracted is not None
        assert extracted.value == 3.2

    def test_returns_none_for_missing_metric(self):
        """Returns None when metric not in outputs."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            outputs={"peak_flow_cfs": 100.0},
        )

        extracted = extract_metric_from_result(result, ComparisonMetric.RUNOFF_DEPTH_IN)

        assert extracted is None

    def test_returns_none_for_null_value(self):
        """Returns None when metric value is None."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            outputs={"peak_flow_cfs": None},
        )

        extracted = extract_metric_from_result(result, ComparisonMetric.PEAK_FLOW_CFS)

        assert extracted is None

    def test_uses_default_unit_if_not_specified(self):
        """Uses default unit when not in result.units."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            outputs={"peak_flow_cfs": 100.0},
            units={},
        )

        extracted = extract_metric_from_result(result, ComparisonMetric.PEAK_FLOW_CFS)

        assert extracted.unit == "cfs"

    def test_converts_value_to_float(self):
        """Converts integer value to float."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            outputs={"peak_flow_cfs": 100},
        )

        extracted = extract_metric_from_result(result, ComparisonMetric.PEAK_FLOW_CFS)

        assert isinstance(extracted.value, float)
        assert extracted.value == 100.0


class TestExtractAllMetricsFromResult:
    """Tests for extracting all metrics from result."""

    def test_extracts_all_present_metrics(self):
        """Extracts all recognized metrics present in outputs."""
        result = CalculationResult(
            method="combined",
            entity_id="area-1",
            outputs={
                "peak_flow_cfs": 100.0,
                "runoff_depth_in": 2.5,
                "runoff_volume_cuft": 50000.0,
            },
        )

        extracted = extract_all_metrics_from_result(result)

        assert len(extracted) == 3
        assert ComparisonMetric.PEAK_FLOW_CFS in extracted
        assert ComparisonMetric.RUNOFF_DEPTH_IN in extracted
        assert ComparisonMetric.RUNOFF_VOLUME_CUFT in extracted
        assert ComparisonMetric.TIME_OF_CONCENTRATION_MIN not in extracted

    def test_ignores_unrecognized_outputs(self):
        """Ignores output keys that are not recognized metrics."""
        result = CalculationResult(
            method="rational_method",
            entity_id="area-1",
            outputs={
                "peak_flow_cfs": 100.0,
                "intermediate_value": 42.0,
                "other_output": "text",
            },
        )

        extracted = extract_all_metrics_from_result(result)

        assert len(extracted) == 1
        assert ComparisonMetric.PEAK_FLOW_CFS in extracted

    def test_empty_outputs(self):
        """Returns empty dict for empty outputs."""
        result = CalculationResult(
            method="empty",
            entity_id="area-1",
            outputs={},
        )

        extracted = extract_all_metrics_from_result(result)

        assert extracted == {}


class TestGetMetricsForEntity:
    """Tests for getting metrics for an entity from scenario."""

    def test_gets_metrics_from_calculation_results(self):
        """Gets metrics from scenario's calculation results."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
            )
        )

        metrics = get_metrics_for_entity(scenario, "area-1")

        assert ComparisonMetric.PEAK_FLOW_CFS in metrics
        assert metrics[ComparisonMetric.PEAK_FLOW_CFS].value == 100.0

    def test_filters_by_entity_id(self):
        """Only returns metrics for specified entity."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                outputs={"peak_flow_cfs": 100.0},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-2",
                outputs={"peak_flow_cfs": 200.0},
            )
        )

        metrics = get_metrics_for_entity(scenario, "area-1")

        assert metrics[ComparisonMetric.PEAK_FLOW_CFS].value == 100.0

    def test_filters_by_storm_event(self):
        """Filters by storm event name when specified."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                outputs={"peak_flow_cfs": 100.0},
                metadata={"storm_event_name": "10-year"},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                outputs={"peak_flow_cfs": 200.0},
                metadata={"storm_event_name": "100-year"},
            )
        )

        metrics = get_metrics_for_entity(scenario, "area-1", storm_event_name="100-year")

        assert metrics[ComparisonMetric.PEAK_FLOW_CFS].value == 200.0

    def test_first_result_wins_for_metric(self):
        """First result with metric wins when multiple exist."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                outputs={"peak_flow_cfs": 100.0},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method_v2",
                entity_id="area-1",
                outputs={"peak_flow_cfs": 150.0},
            )
        )

        metrics = get_metrics_for_entity(scenario, "area-1")

        assert metrics[ComparisonMetric.PEAK_FLOW_CFS].value == 100.0

    def test_combines_metrics_from_multiple_results(self):
        """Combines metrics from different calculation results."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                outputs={"peak_flow_cfs": 100.0},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="tr55",
                entity_id="area-1",
                outputs={"runoff_depth_in": 2.5},
            )
        )

        metrics = get_metrics_for_entity(scenario, "area-1")

        assert ComparisonMetric.PEAK_FLOW_CFS in metrics
        assert ComparisonMetric.RUNOFF_DEPTH_IN in metrics

    def test_empty_for_no_results(self):
        """Returns empty dict when no results for entity."""
        scenario = Scenario(name="Test")

        metrics = get_metrics_for_entity(scenario, "area-1")

        assert metrics == {}


class TestGetAllEntityMetrics:
    """Tests for getting metrics for all entities."""

    def test_gets_metrics_for_all_entities(self):
        """Gets metrics for all entities of type."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-2",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 200.0},
            )
        )

        all_metrics = get_all_entity_metrics(scenario)

        assert "area-1" in all_metrics
        assert "area-2" in all_metrics
        assert all_metrics["area-1"][ComparisonMetric.PEAK_FLOW_CFS].value == 100.0
        assert all_metrics["area-2"][ComparisonMetric.PEAK_FLOW_CFS].value == 200.0

    def test_filters_by_entity_type(self):
        """Only returns metrics for specified entity type."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="kirpich",
                entity_id="flow-1",
                entity_type="FlowPath",
                outputs={"time_of_concentration_min": 15.0},
            )
        )

        all_metrics = get_all_entity_metrics(scenario, entity_type="DrainageArea")

        assert "area-1" in all_metrics
        assert "flow-1" not in all_metrics

    def test_filters_by_storm_event(self):
        """Filters by storm event name."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
                metadata={"storm_event_name": "10-year"},
            )
        )
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 200.0},
                metadata={"storm_event_name": "100-year"},
            )
        )

        all_metrics = get_all_entity_metrics(
            scenario, storm_event_name="100-year"
        )

        assert all_metrics["area-1"][ComparisonMetric.PEAK_FLOW_CFS].value == 200.0

    def test_skips_results_without_entity_id(self):
        """Skips results without entity_id."""
        scenario = Scenario(name="Test")
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id=None,
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
            )
        )

        all_metrics = get_all_entity_metrics(scenario)

        assert all_metrics == {}

    def test_empty_scenario(self):
        """Returns empty dict for scenario with no results."""
        scenario = Scenario(name="Test")

        all_metrics = get_all_entity_metrics(scenario)

        assert all_metrics == {}
