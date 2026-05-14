"""Tests for Project domain entity."""

import pytest
from datetime import datetime

from civil_toolbox.domain.project import Project, DesignCriteria
from civil_toolbox.domain.scenario import Scenario


class TestDesignCriteria:
    """Tests for DesignCriteria."""

    def test_creates_with_defaults(self):
        criteria = DesignCriteria()
        assert criteria.design_storm_years is None
        assert criteria.allowed_methods == []

    def test_creates_with_values(self):
        criteria = DesignCriteria(
            design_storm_years=100,
            rainfall_distribution="Type III",
            jurisdiction="harris_county",
            allowed_methods=["Rational", "TR-55"],
        )
        assert criteria.design_storm_years == 100
        assert criteria.jurisdiction == "harris_county"
        assert len(criteria.allowed_methods) == 2

    def test_round_trip_serialization(self):
        criteria = DesignCriteria(
            design_storm_years=25,
            jurisdiction="generic",
        )
        data = criteria.to_dict()
        restored = DesignCriteria.from_dict(data)
        assert restored.design_storm_years == 25
        assert restored.jurisdiction == "generic"


class TestProject:
    """Tests for Project."""

    def test_creates_with_name(self):
        project = Project(name="Test Site")
        assert project.name == "Test Site"
        assert project.id is not None

    def test_raises_on_missing_name(self):
        with pytest.raises(ValueError, match="requires a name"):
            Project(name="")

    def test_creates_with_metadata(self):
        project = Project(
            name="Example Development",
            client="ABC Corp",
            jurisdiction="harris_county",
            description="Drainage analysis for proposed development",
        )
        assert project.client == "ABC Corp"
        assert project.jurisdiction == "harris_county"

    def test_creates_with_design_criteria(self):
        criteria = DesignCriteria(design_storm_years=100)
        project = Project(
            name="Test",
            design_criteria=criteria,
        )
        assert project.design_criteria.design_storm_years == 100

    def test_add_scenario(self):
        project = Project(name="Test Project")
        scenario = Scenario(name="Existing Conditions")
        project.add_scenario(scenario)
        assert len(project.scenarios) == 1
        assert project.scenarios[0].project_id == project.id

    def test_add_scenario_validates_type(self):
        project = Project(name="Test")
        with pytest.raises(TypeError, match="Expected a Scenario instance"):
            project.add_scenario("not a scenario")

    def test_remove_scenario(self):
        project = Project(name="Test")
        scenario = Scenario(name="To Remove")
        project.add_scenario(scenario)
        assert len(project.scenarios) == 1
        removed = project.remove_scenario(scenario.id)
        assert removed is True
        assert len(project.scenarios) == 0

    def test_remove_nonexistent_scenario(self):
        project = Project(name="Test")
        removed = project.remove_scenario("nonexistent-id")
        assert removed is False

    def test_get_scenario(self):
        project = Project(name="Test")
        scenario = Scenario(name="Find Me")
        project.add_scenario(scenario)
        found = project.get_scenario(scenario.id)
        assert found is not None
        assert found.name == "Find Me"

    def test_get_nonexistent_scenario(self):
        project = Project(name="Test")
        found = project.get_scenario("nonexistent")
        assert found is None

    def test_to_dict_serialization(self):
        project = Project(
            name="Serialization Test",
            client="Test Client",
        )
        scenario = Scenario(name="Scenario 1")
        project.add_scenario(scenario)

        data = project.to_dict()
        assert data["name"] == "Serialization Test"
        assert data["client"] == "Test Client"
        assert len(data["scenarios"]) == 1

    def test_from_dict_deserialization(self):
        data = {
            "id": "proj-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "name": "Restored Project",
            "client": "Restored Client",
            "description": None,
            "jurisdiction": "generic",
            "design_criteria": {"design_storm_years": 50},
            "scenarios": [
                {
                    "id": "scen-456",
                    "created_at": "2026-01-01T00:00:00",
                    "updated_at": "2026-01-01T00:00:00",
                    "name": "Restored Scenario",
                    "description": None,
                    "project_id": "proj-123",
                    "drainage_areas": [],
                    "storm_events": [],
                    "flow_paths": [],
                    "infrastructure": [],
                    "calculation_results": [],
                }
            ],
        }
        project = Project.from_dict(data)
        assert project.id == "proj-123"
        assert project.name == "Restored Project"
        assert project.design_criteria.design_storm_years == 50
        assert len(project.scenarios) == 1
        assert project.scenarios[0].name == "Restored Scenario"

    def test_round_trip_serialization(self):
        project = Project(
            name="Round Trip Test",
            client="Test",
            design_criteria=DesignCriteria(design_storm_years=25),
        )
        scenario = Scenario(name="Test Scenario")
        project.add_scenario(scenario)

        data = project.to_dict()
        restored = Project.from_dict(data)

        assert restored.id == project.id
        assert restored.name == project.name
        assert restored.design_criteria.design_storm_years == 25
        assert len(restored.scenarios) == 1
        assert restored.scenarios[0].id == scenario.id
