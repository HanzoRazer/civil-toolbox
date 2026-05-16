"""Tests for scenario attachment helpers."""

import pytest

from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment

from civil_toolbox.adapters.scenario_helpers import (
    run_rational_method,
    run_rational_method_composite,
    run_tr55_runoff_depth,
    run_tr55_runoff_volume,
    run_tc_kirpich,
    run_tc_composite,
    run_all_drainage_areas,
)


class TestRunRationalMethod:
    """Tests for run_rational_method."""

    def test_calculates_and_attaches(self):
        scenario = Scenario(name="Test")
        area = DrainageArea(name="Basin", area_acres=25.0, runoff_coefficient=0.65)
        storm = StormEvent(name="10-year", rainfall_intensity_in_per_hr=5.0)

        result = run_rational_method(scenario, area, storm)

        assert result.outputs["peak_runoff_cfs"] == pytest.approx(81.25)
        assert len(scenario.calculation_results) == 1
        assert scenario.calculation_results[0] is result

    def test_attach_false_does_not_modify_scenario(self):
        scenario = Scenario(name="Test")
        area = DrainageArea(name="Basin", area_acres=10.0, runoff_coefficient=0.5)
        storm = StormEvent(name="Storm", rainfall_intensity_in_per_hr=4.0)

        result = run_rational_method(scenario, area, storm, attach=False)

        assert result.outputs["peak_runoff_cfs"] > 0
        assert len(scenario.calculation_results) == 0


class TestRunRationalMethodComposite:
    """Tests for run_rational_method_composite."""

    def test_calculates_composite(self):
        scenario = Scenario(name="Test")
        areas = [
            DrainageArea(name="A", area_acres=10.0, runoff_coefficient=0.3),
            DrainageArea(name="B", area_acres=10.0, runoff_coefficient=0.7),
        ]
        storm = StormEvent(name="Storm", rainfall_intensity_in_per_hr=5.0)

        result = run_rational_method_composite(scenario, areas, storm)

        assert result.method == "rational_method_composite"
        assert len(scenario.calculation_results) == 1


class TestRunTR55RunoffDepth:
    """Tests for run_tr55_runoff_depth."""

    def test_calculates_and_attaches(self):
        scenario = Scenario(name="Test")
        area = DrainageArea(name="Basin", curve_number=80)
        storm = StormEvent(name="10-year", rainfall_depth_in=5.0)

        result = run_tr55_runoff_depth(scenario, area, storm)

        assert result.outputs["runoff_depth_in"] > 0
        assert len(scenario.calculation_results) == 1


class TestRunTR55RunoffVolume:
    """Tests for run_tr55_runoff_volume."""

    def test_calculates_volume(self):
        scenario = Scenario(name="Test")
        area = DrainageArea(name="Basin", curve_number=80, area_acres=50.0)
        storm = StormEvent(name="10-year", rainfall_depth_in=5.0)

        result = run_tr55_runoff_volume(scenario, area, storm)

        assert result.outputs["runoff_volume_cf"] > 0
        assert result.outputs["runoff_volume_ac_ft"] > 0
        assert len(scenario.calculation_results) == 1


class TestRunTcKirpich:
    """Tests for run_tc_kirpich."""

    def test_calculates_and_attaches(self):
        scenario = Scenario(name="Test")
        path = FlowPath(name="Main Channel")
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=3000,
            slope_ft_per_ft=0.02,
        ))

        result = run_tc_kirpich(scenario, path)

        assert result.outputs["tc_minutes"] > 0
        assert len(scenario.calculation_results) == 1


class TestRunTcComposite:
    """Tests for run_tc_composite."""

    def test_calculates_composite(self):
        scenario = Scenario(name="Test")
        path = FlowPath(name="Mixed Path")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100,
            slope_ft_per_ft=0.02,
            roughness_n=0.15,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=2000,
            slope_ft_per_ft=0.01,
        ))

        result = run_tc_composite(scenario, path, rainfall_2yr_24hr_in=3.5)

        assert result.outputs["tc_minutes"] > 0
        assert len(scenario.calculation_results) == 1


class TestRunAllDrainageAreas:
    """Tests for run_all_drainage_areas."""

    def test_runs_rational_for_all_areas(self):
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(
            name="A", area_acres=10.0, runoff_coefficient=0.5
        ))
        scenario.add_drainage_area(DrainageArea(
            name="B", area_acres=15.0, runoff_coefficient=0.6
        ))
        storm = StormEvent(name="Storm", rainfall_intensity_in_per_hr=4.0)

        results = run_all_drainage_areas(scenario, storm, method="rational")

        assert len(results) == 2
        assert len(scenario.calculation_results) == 2
        assert all(r.method == "rational_method" for r in results)

    def test_runs_tr55_for_all_areas(self):
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(name="A", curve_number=70))
        scenario.add_drainage_area(DrainageArea(name="B", curve_number=80))
        storm = StormEvent(name="Storm", rainfall_depth_in=5.0)

        results = run_all_drainage_areas(scenario, storm, method="tr55")

        assert len(results) == 2
        assert all(r.method == "tr55_runoff_depth" for r in results)

    def test_unknown_method_raises(self):
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(
            name="A", area_acres=10.0, runoff_coefficient=0.5
        ))
        storm = StormEvent(name="Storm", rainfall_intensity_in_per_hr=4.0)

        with pytest.raises(ValueError) as exc_info:
            run_all_drainage_areas(scenario, storm, method="unknown")

        assert "unknown" in str(exc_info.value).lower()

    def test_attach_false(self):
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(
            name="A", area_acres=10.0, runoff_coefficient=0.5
        ))
        storm = StormEvent(name="Storm", rainfall_intensity_in_per_hr=4.0)

        results = run_all_drainage_areas(scenario, storm, attach=False)

        assert len(results) == 1
        assert len(scenario.calculation_results) == 0
