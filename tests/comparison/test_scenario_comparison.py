"""Tests for scenario comparison engine."""

import pytest

from civil_toolbox.comparison.scenario_comparison import (
    ScenarioComparison,
    compare_scenarios,
)
from civil_toolbox.comparison.models import (
    ComparisonMetric,
    ComparisonStatus,
    PercentDeltaStatus,
    MatchStrategy,
)
from civil_toolbox.comparison.validation import (
    SameScenarioError,
    EmptyScenarioError,
)
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.calculation import CalculationResult


def make_scenario_with_results(
    name: str,
    areas: list[tuple[str, str, float]],
    scenario_id: str | None = None,
) -> Scenario:
    """Create a scenario with drainage areas and calculation results.

    Args:
        name: Scenario name.
        areas: List of (area_id, area_name, peak_flow) tuples.
        scenario_id: Optional scenario ID.

    Returns:
        Scenario with areas and results.
    """
    scenario = Scenario(name=name)
    if scenario_id:
        scenario.id = scenario_id

    for area_id, area_name, peak_flow in areas:
        area = DrainageArea(id=area_id, name=area_name)
        scenario.add_drainage_area(area)
        scenario.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id=area_id,
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": peak_flow},
                units={"peak_flow_cfs": "cfs"},
            )
        )

    return scenario


class TestScenarioComparison:
    """Tests for ScenarioComparison class."""

    def test_compares_matching_areas_by_id(self):
        """Compares areas with matching IDs."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        assert len(result.entity_comparisons) == 1
        entity = result.entity_comparisons[0]
        assert entity.baseline_entity_id == "area-1"
        assert ComparisonMetric.PEAK_FLOW_CFS in entity.metrics

        peak = entity.metrics[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak.baseline_value == 100.0
        assert peak.comparison_value == 120.0
        assert peak.delta == 20.0
        assert peak.percent_delta == 20.0

    def test_compares_multiple_areas(self):
        """Compares multiple matched areas."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0), ("area-2", "Area B", 200.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0), ("area-2", "Area B", 180.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        assert len(result.entity_comparisons) == 2

    def test_includes_scenario_info(self):
        """Includes scenario identification in result."""
        baseline = make_scenario_with_results(
            "Existing Conditions",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-baseline",
        )
        comparison = make_scenario_with_results(
            "Proposed Development",
            [("area-1", "Area A", 120.0)],
            scenario_id="s-proposed",
        )

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        assert result.baseline_scenario_id == "s-baseline"
        assert result.baseline_scenario_name == "Existing Conditions"
        assert result.comparison_scenario_id == "s-proposed"
        assert result.comparison_scenario_name == "Proposed Development"

    def test_tracks_unmatched_entities(self):
        """Tracks entities that could not be matched."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0), ("area-orphan", "Orphan", 50.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0), ("area-new", "New Area", 75.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(baseline, comparison, match_strategy=MatchStrategy.ID)
        result = engine.compare()

        assert "area-orphan" in result.unmatched_baseline_ids
        assert "area-new" in result.unmatched_comparison_ids

    def test_uses_explicit_map(self):
        """Uses explicit mapping when provided."""
        baseline = make_scenario_with_results(
            "Existing",
            [("b-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("c-1", "Area A Redesigned", 150.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(
            baseline,
            comparison,
            match_strategy=MatchStrategy.EXPLICIT,
            explicit_map={"b-1": "c-1"},
        )
        result = engine.compare()

        assert len(result.entity_comparisons) == 1
        assert result.entity_comparisons[0].comparison_entity_id == "c-1"

    def test_handles_missing_comparison_metric(self):
        """Handles when comparison scenario lacks metric."""
        baseline = Scenario(name="Existing")
        baseline.id = "s-1"
        area = DrainageArea(id="area-1", name="Area A")
        baseline.add_drainage_area(area)
        baseline.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
            )
        )

        comparison = Scenario(name="Proposed")
        comparison.id = "s-2"
        comparison.add_drainage_area(DrainageArea(id="area-1", name="Area A"))

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        entity = result.entity_comparisons[0]
        peak = entity.metrics[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak.baseline_value == 100.0
        assert peak.comparison_value is None
        assert peak.status == ComparisonStatus.MISSING_COMPARISON
        assert peak.delta is None

    def test_handles_missing_baseline_metric(self):
        """Handles when baseline scenario lacks metric."""
        baseline = Scenario(name="Existing")
        baseline.id = "s-1"
        baseline.add_drainage_area(DrainageArea(id="area-1", name="Area A"))

        comparison = Scenario(name="Proposed")
        comparison.id = "s-2"
        area = DrainageArea(id="area-1", name="Area A")
        comparison.add_drainage_area(area)
        comparison.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 120.0},
            )
        )

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        entity = result.entity_comparisons[0]
        peak = entity.metrics[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak.baseline_value is None
        assert peak.comparison_value == 120.0
        assert peak.status == ComparisonStatus.MISSING_BASELINE

    def test_computes_scenario_totals(self):
        """Computes scenario-level totals for additive metrics."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0), ("area-2", "Area B", 200.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0), ("area-2", "Area B", 250.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        assert ComparisonMetric.PEAK_FLOW_CFS in result.totals
        total = result.totals[ComparisonMetric.PEAK_FLOW_CFS]
        assert total.baseline_total == 300.0
        assert total.comparison_total == 370.0
        assert total.delta == 70.0
        assert total.entity_count == 2

    def test_handles_zero_baseline(self):
        """Handles zero baseline value correctly."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 0.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 50.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(baseline, comparison)
        result = engine.compare()

        entity = result.entity_comparisons[0]
        peak = entity.metrics[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak.baseline_value == 0.0
        assert peak.comparison_value == 50.0
        assert peak.delta == 50.0
        assert peak.percent_delta is None
        assert peak.percent_delta_status == PercentDeltaStatus.UNDEFINED_ZERO_BASELINE

    def test_raises_for_same_scenario(self):
        """Raises when comparing scenario to itself."""
        scenario = make_scenario_with_results(
            "Test",
            [("area-1", "Area A", 100.0)],
        )

        with pytest.raises(SameScenarioError):
            ScenarioComparison(scenario, scenario)

    def test_raises_for_empty_baseline(self):
        """Raises when baseline has no entities."""
        baseline = Scenario(name="Empty")
        baseline.id = "s-1"
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-2",
        )

        with pytest.raises(EmptyScenarioError):
            ScenarioComparison(baseline, comparison)

    def test_filters_by_storm_event(self):
        """Filters calculation results by storm event name."""
        baseline = Scenario(name="Existing")
        baseline.id = "s-1"
        area = DrainageArea(id="area-1", name="Area A")
        baseline.add_drainage_area(area)
        baseline.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 100.0},
                metadata={"storm_event_name": "10-year"},
            )
        )
        baseline.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 200.0},
                metadata={"storm_event_name": "100-year"},
            )
        )

        comparison = Scenario(name="Proposed")
        comparison.id = "s-2"
        comparison.add_drainage_area(DrainageArea(id="area-1", name="Area A"))
        comparison.calculation_results.append(
            CalculationResult(
                method="rational_method",
                entity_id="area-1",
                entity_type="DrainageArea",
                outputs={"peak_flow_cfs": 250.0},
                metadata={"storm_event_name": "100-year"},
            )
        )

        engine = ScenarioComparison(
            baseline, comparison, storm_event_name="100-year"
        )
        result = engine.compare()

        entity = result.entity_comparisons[0]
        peak = entity.metrics[ComparisonMetric.PEAK_FLOW_CFS]
        assert peak.baseline_value == 200.0
        assert peak.comparison_value == 250.0

    def test_includes_storm_event_in_result(self):
        """Includes storm event name in result."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0)],
            scenario_id="s-2",
        )

        engine = ScenarioComparison(
            baseline, comparison, storm_event_name="100-year"
        )
        result = engine.compare()

        assert result.storm_event_name == "100-year"


class TestCompareScenarios:
    """Tests for compare_scenarios convenience function."""

    def test_compares_scenarios(self):
        """Compares two scenarios."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0)],
            scenario_id="s-2",
        )

        result = compare_scenarios(baseline, comparison)

        assert len(result.entity_comparisons) == 1

    def test_accepts_string_strategy(self):
        """Accepts string match strategy."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0)],
            scenario_id="s-2",
        )

        result = compare_scenarios(baseline, comparison, match_strategy="id")

        assert result.match_strategy == MatchStrategy.ID

    def test_passes_all_options(self):
        """Passes all options to engine."""
        baseline = make_scenario_with_results(
            "Existing",
            [("b-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("c-1", "Area A", 120.0)],
            scenario_id="s-2",
        )

        result = compare_scenarios(
            baseline,
            comparison,
            match_strategy=MatchStrategy.EXPLICIT,
            explicit_map={"b-1": "c-1"},
            storm_event_name="100-year",
        )

        assert result.match_strategy == MatchStrategy.EXPLICIT
        assert result.storm_event_name == "100-year"
        assert len(result.entity_comparisons) == 1


class TestSerializationRoundTrip:
    """Tests for serialization of comparison results."""

    def test_result_serializes(self):
        """Comparison result can be serialized to dict."""
        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0), ("area-2", "Area B", 200.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0), ("area-2", "Area B", 250.0)],
            scenario_id="s-2",
        )

        result = compare_scenarios(baseline, comparison)
        data = result.to_dict()

        assert data["baseline_scenario_name"] == "Existing"
        assert data["comparison_scenario_name"] == "Proposed"
        assert len(data["entity_comparisons"]) == 2
        assert "peak_flow_cfs" in data["totals"]

    def test_result_round_trips(self):
        """Comparison result round-trips through serialization."""
        from civil_toolbox.comparison.models import ScenarioComparisonResult

        baseline = make_scenario_with_results(
            "Existing",
            [("area-1", "Area A", 100.0)],
            scenario_id="s-1",
        )
        comparison = make_scenario_with_results(
            "Proposed",
            [("area-1", "Area A", 120.0)],
            scenario_id="s-2",
        )

        original = compare_scenarios(baseline, comparison)
        restored = ScenarioComparisonResult.from_dict(original.to_dict())

        assert restored.baseline_scenario_name == original.baseline_scenario_name
        assert len(restored.entity_comparisons) == len(original.entity_comparisons)
        assert (
            restored.entity_comparisons[0].metrics[ComparisonMetric.PEAK_FLOW_CFS].delta
            == original.entity_comparisons[0].metrics[ComparisonMetric.PEAK_FLOW_CFS].delta
        )
