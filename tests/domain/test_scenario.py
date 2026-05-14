"""Tests for Scenario domain entity."""

import pytest
from datetime import datetime

from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.flow_path import FlowPath
from civil_toolbox.domain.infrastructure import InfrastructureElement
from civil_toolbox.domain.calculation import CalculationResult


class TestScenario:
    """Tests for Scenario."""

    def test_creates_with_name(self):
        scenario = Scenario(name="Existing Conditions")
        assert scenario.name == "Existing Conditions"
        assert scenario.id is not None

    def test_raises_on_missing_name(self):
        with pytest.raises(ValueError, match="requires a name"):
            Scenario(name="")

    def test_creates_with_description(self):
        scenario = Scenario(
            name="Proposed Development",
            description="Post-development conditions with detention",
        )
        assert scenario.description is not None

    def test_empty_collections_by_default(self):
        scenario = Scenario(name="Test")
        assert scenario.drainage_areas == []
        assert scenario.storm_events == []
        assert scenario.flow_paths == []
        assert scenario.infrastructure == []
        assert scenario.calculation_results == []

    def test_add_drainage_area(self):
        scenario = Scenario(name="Test")
        area = DrainageArea(name="Basin A", area_acres=10.0)
        scenario.add_drainage_area(area)
        assert len(scenario.drainage_areas) == 1
        assert scenario.drainage_areas[0].scenario_id == scenario.id

    def test_add_drainage_area_validates_type(self):
        scenario = Scenario(name="Test")
        with pytest.raises(TypeError, match="Expected a DrainageArea"):
            scenario.add_drainage_area("not an area")

    def test_add_storm_event(self):
        scenario = Scenario(name="Test")
        event = StormEvent(name="100-year", return_period_years=100)
        scenario.add_storm_event(event)
        assert len(scenario.storm_events) == 1
        assert scenario.storm_events[0].scenario_id == scenario.id

    def test_add_storm_event_validates_type(self):
        scenario = Scenario(name="Test")
        with pytest.raises(TypeError, match="Expected a StormEvent"):
            scenario.add_storm_event("not an event")

    def test_add_flow_path(self):
        scenario = Scenario(name="Test")
        path = FlowPath(name="Main Path")
        scenario.add_flow_path(path)
        assert len(scenario.flow_paths) == 1
        assert scenario.flow_paths[0].scenario_id == scenario.id

    def test_add_flow_path_validates_type(self):
        scenario = Scenario(name="Test")
        with pytest.raises(TypeError, match="Expected a FlowPath"):
            scenario.add_flow_path("not a path")

    def test_add_infrastructure(self):
        scenario = Scenario(name="Test")
        element = InfrastructureElement(name="Pipe 1", element_type="pipe")
        scenario.add_infrastructure(element)
        assert len(scenario.infrastructure) == 1
        assert scenario.infrastructure[0].scenario_id == scenario.id

    def test_add_infrastructure_validates_type(self):
        scenario = Scenario(name="Test")
        with pytest.raises(TypeError, match="Expected an InfrastructureElement"):
            scenario.add_infrastructure("not an element")

    def test_add_calculation_result(self):
        scenario = Scenario(name="Test")
        result = CalculationResult(method="Rational Method")
        scenario.add_calculation_result(result)
        assert len(scenario.calculation_results) == 1
        assert scenario.calculation_results[0].scenario_id == scenario.id

    def test_add_calculation_result_validates_type(self):
        scenario = Scenario(name="Test")
        with pytest.raises(TypeError, match="Expected a CalculationResult"):
            scenario.add_calculation_result("not a result")

    def test_to_dict_serialization(self):
        scenario = Scenario(
            name="Test Scenario",
            description="For serialization test",
        )
        area = DrainageArea(name="Area 1", area_acres=5.0)
        scenario.add_drainage_area(area)

        data = scenario.to_dict()
        assert data["name"] == "Test Scenario"
        assert len(data["drainage_areas"]) == 1

    def test_from_dict_deserialization(self):
        data = {
            "id": "scen-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "name": "Restored Scenario",
            "description": "Restored description",
            "project_id": "proj-456",
            "drainage_areas": [
                {
                    "id": "area-1",
                    "created_at": "2026-01-01T00:00:00",
                    "updated_at": "2026-01-01T00:00:00",
                    "name": "Basin A",
                    "area_acres": 15.0,
                }
            ],
            "storm_events": [],
            "flow_paths": [],
            "infrastructure": [],
            "calculation_results": [],
        }
        scenario = Scenario.from_dict(data)
        assert scenario.id == "scen-123"
        assert scenario.name == "Restored Scenario"
        assert len(scenario.drainage_areas) == 1
        assert scenario.drainage_areas[0].name == "Basin A"

    def test_round_trip_serialization(self):
        scenario = Scenario(name="Round Trip")
        area = DrainageArea(name="Test Area", area_acres=20.0)
        event = StormEvent(name="25-year", return_period_years=25)
        scenario.add_drainage_area(area)
        scenario.add_storm_event(event)

        data = scenario.to_dict()
        restored = Scenario.from_dict(data)

        assert restored.id == scenario.id
        assert restored.name == scenario.name
        assert len(restored.drainage_areas) == 1
        assert len(restored.storm_events) == 1
        assert restored.drainage_areas[0].area_acres == 20.0
