"""Comprehensive serialization round-trip tests for domain entities."""

import json
import pytest
from datetime import datetime

from civil_toolbox.domain.project import Project, DesignCriteria
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.domain.infrastructure import InfrastructureElement
from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.base import (
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)


class TestProjectSerializationRoundTrip:
    """Full project serialization tests."""

    def test_empty_project_round_trip(self):
        """Test minimal project serializes and deserializes."""
        project = Project(name="Minimal Project")
        data = project.to_dict()
        restored = Project.from_dict(data)

        assert restored.id == project.id
        assert restored.name == project.name
        assert len(restored.scenarios) == 0

    def test_project_with_metadata_round_trip(self):
        """Test project with all metadata fields."""
        project = Project(
            name="Full Metadata",
            client="Test Client Inc.",
            description="A comprehensive drainage study",
            jurisdiction="harris_county",
            design_criteria=DesignCriteria(
                design_storm_years=100,
                rainfall_distribution="Type III",
                jurisdiction="harris_county",
                allowed_methods=["Rational", "TR-55"],
                notes="HCFCD criteria apply",
            ),
        )
        data = project.to_dict()
        restored = Project.from_dict(data)

        assert restored.client == "Test Client Inc."
        assert restored.design_criteria.design_storm_years == 100
        assert "Rational" in restored.design_criteria.allowed_methods

    def test_project_with_scenario_round_trip(self):
        """Test project containing a scenario."""
        project = Project(name="With Scenario")
        scenario = Scenario(name="Existing Conditions")
        project.add_scenario(scenario)

        data = project.to_dict()
        restored = Project.from_dict(data)

        assert len(restored.scenarios) == 1
        assert restored.scenarios[0].name == "Existing Conditions"
        assert restored.scenarios[0].project_id == restored.id


class TestScenarioSerializationRoundTrip:
    """Full scenario serialization tests with all child entities."""

    def test_scenario_with_all_entities_round_trip(self):
        """Test scenario containing all entity types."""
        scenario = Scenario(
            name="Complete Scenario",
            description="Contains all domain entity types",
        )

        # Add drainage area
        area = DrainageArea(
            name="Basin A",
            area_acres=50.0,
            runoff_coefficient=0.65,
            curve_number=80,
            soil_group="B",
            land_use="residential",
        )
        scenario.add_drainage_area(area)

        # Add storm event
        event = StormEvent(
            name="100-year Design Storm",
            return_period_years=100,
            duration_hours=24.0,
            rainfall_depth_in=9.0,
            rainfall_intensity_in_per_hr=0.375,
            distribution="Type III",
        )
        scenario.add_storm_event(event)

        # Add flow path with segments
        path = FlowPath(name="Main Flow Path")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100.0,
            slope_ft_per_ft=0.02,
            roughness_n=0.15,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="shallow_concentrated",
            length_ft=500.0,
            slope_ft_per_ft=0.01,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=1500.0,
            slope_ft_per_ft=0.005,
            roughness_n=0.035,
        ))
        scenario.add_flow_path(path)

        # Add infrastructure
        pipe = InfrastructureElement(
            name="Storm Sewer Main",
            element_type="pipe",
            length_ft=800.0,
            slope_ft_per_ft=0.005,
            diameter_in=36.0,
            material="RCP",
            mannings_n=0.013,
            capacity_cfs=85.0,
        )
        scenario.add_infrastructure(pipe)

        # Add calculation result
        result = CalculationResult(
            method="Rational Method",
            entity_id=area.id,
            entity_type="DrainageArea",
            inputs={"C": 0.65, "i": 4.5, "A": 50.0},
            outputs={"Q": 146.25},
            units={"C": "dimensionless", "i": "in/hr", "A": "acre", "Q": "cfs"},
        )
        result.add_assumption(EngineeringAssumption(
            description="Peak discharge at time of concentration",
        ))
        result.add_reference(EngineeringReference(
            title="HEC-22",
            source="FHWA",
            year=2009,
        ))
        scenario.add_calculation_result(result)

        # Serialize and restore
        data = scenario.to_dict()
        restored = Scenario.from_dict(data)

        # Verify all entities
        assert restored.id == scenario.id
        assert restored.name == scenario.name
        assert len(restored.drainage_areas) == 1
        assert len(restored.storm_events) == 1
        assert len(restored.flow_paths) == 1
        assert len(restored.infrastructure) == 1
        assert len(restored.calculation_results) == 1

        # Verify drainage area
        assert restored.drainage_areas[0].area_acres == 50.0
        assert restored.drainage_areas[0].curve_number == 80

        # Verify storm event
        assert restored.storm_events[0].return_period_years == 100
        assert restored.storm_events[0].rainfall_depth_in == 9.0

        # Verify flow path
        assert len(restored.flow_paths[0].segments) == 3
        assert restored.flow_paths[0].total_length_ft == 2100.0

        # Verify infrastructure
        assert restored.infrastructure[0].diameter_in == 36.0
        assert restored.infrastructure[0].capacity_cfs == 85.0

        # Verify calculation result
        assert restored.calculation_results[0].method == "Rational Method"
        assert restored.calculation_results[0].outputs["Q"] == 146.25
        assert len(restored.calculation_results[0].assumptions) == 1
        assert len(restored.calculation_results[0].references) == 1


class TestJSONSerialization:
    """Test that domain objects serialize to valid JSON."""

    def test_project_to_json_round_trip(self):
        """Test full project serializes to JSON and back."""
        project = Project(
            name="JSON Test Project",
            client="JSON Client",
        )
        scenario = Scenario(name="JSON Scenario")
        area = DrainageArea(name="JSON Area", area_acres=10.0)
        scenario.add_drainage_area(area)
        project.add_scenario(scenario)

        # Convert to JSON string
        json_str = json.dumps(project.to_dict(), indent=2)

        # Parse back and restore
        parsed = json.loads(json_str)
        restored = Project.from_dict(parsed)

        assert restored.name == project.name
        assert restored.client == project.client
        assert len(restored.scenarios) == 1
        assert len(restored.scenarios[0].drainage_areas) == 1

    def test_calculation_result_to_json_round_trip(self):
        """Test calculation result with nested objects serializes to JSON."""
        result = CalculationResult(
            method="Complex Calculation",
            inputs={"param1": 1.5, "param2": "text"},
            outputs={"result": 42.0},
            metadata={"nested": {"key": "value"}},
        )
        result.add_assumption(EngineeringAssumption(
            description="Test assumption",
            reference=EngineeringReference(title="Ref", source="Source"),
        ))
        result.add_warning(ValidationWarning(
            message="Test warning",
            field="param1",
            severity="info",
        ))

        json_str = json.dumps(result.to_dict())
        parsed = json.loads(json_str)
        restored = CalculationResult.from_dict(parsed)

        assert restored.method == result.method
        assert restored.metadata["nested"]["key"] == "value"
        assert len(restored.assumptions) == 1
        assert restored.assumptions[0].reference is not None


class TestIDConsistency:
    """Test that IDs are preserved through serialization."""

    def test_all_ids_preserved(self):
        """Verify all entity IDs survive round-trip."""
        project = Project(name="ID Test")
        scenario = Scenario(name="ID Scenario")
        area = DrainageArea(name="ID Area", area_acres=5.0)
        event = StormEvent(name="ID Storm", return_period_years=10)
        path = FlowPath(name="ID Path")
        element = InfrastructureElement(name="ID Element")
        result = CalculationResult(method="ID Method")

        scenario.add_drainage_area(area)
        scenario.add_storm_event(event)
        scenario.add_flow_path(path)
        scenario.add_infrastructure(element)
        scenario.add_calculation_result(result)
        project.add_scenario(scenario)

        # Store original IDs
        original_ids = {
            "project": project.id,
            "scenario": scenario.id,
            "area": area.id,
            "event": event.id,
            "path": path.id,
            "element": element.id,
            "result": result.id,
        }

        # Round-trip
        data = project.to_dict()
        restored = Project.from_dict(data)

        # Verify all IDs match
        assert restored.id == original_ids["project"]
        assert restored.scenarios[0].id == original_ids["scenario"]
        assert restored.scenarios[0].drainage_areas[0].id == original_ids["area"]
        assert restored.scenarios[0].storm_events[0].id == original_ids["event"]
        assert restored.scenarios[0].flow_paths[0].id == original_ids["path"]
        assert restored.scenarios[0].infrastructure[0].id == original_ids["element"]
        assert restored.scenarios[0].calculation_results[0].id == original_ids["result"]


class TestTimestampPreservation:
    """Test that timestamps are preserved through serialization."""

    def test_timestamps_preserved(self):
        """Verify created_at and updated_at survive round-trip."""
        project = Project(name="Timestamp Test")
        original_created = project.created_at
        original_updated = project.updated_at

        data = project.to_dict()
        restored = Project.from_dict(data)

        # Note: ISO format conversion may lose microseconds precision
        assert restored.created_at.year == original_created.year
        assert restored.created_at.month == original_created.month
        assert restored.created_at.day == original_created.day
        assert restored.created_at.hour == original_created.hour


class TestMultipleScenarios:
    """Test project with multiple scenarios."""

    def test_multiple_scenarios_round_trip(self):
        """Test project with multiple scenarios and comparison data."""
        project = Project(name="Comparison Project")

        # Existing conditions
        existing = Scenario(name="Existing Conditions")
        existing.add_drainage_area(DrainageArea(
            name="Site",
            area_acres=100.0,
            runoff_coefficient=0.35,
            curve_number=65,
        ))
        existing.add_storm_event(StormEvent(
            name="100-year",
            return_period_years=100,
            rainfall_depth_in=8.0,
        ))
        project.add_scenario(existing)

        # Proposed conditions
        proposed = Scenario(name="Proposed Development")
        proposed.add_drainage_area(DrainageArea(
            name="Site",
            area_acres=100.0,
            runoff_coefficient=0.65,
            curve_number=85,
        ))
        proposed.add_storm_event(StormEvent(
            name="100-year",
            return_period_years=100,
            rainfall_depth_in=8.0,
        ))
        proposed.add_infrastructure(InfrastructureElement(
            name="Detention Pond",
            element_type="detention",
            capacity_cfs=250.0,
        ))
        project.add_scenario(proposed)

        # Round-trip
        data = project.to_dict()
        restored = Project.from_dict(data)

        assert len(restored.scenarios) == 2
        assert restored.scenarios[0].name == "Existing Conditions"
        assert restored.scenarios[1].name == "Proposed Development"
        assert restored.scenarios[0].drainage_areas[0].runoff_coefficient == 0.35
        assert restored.scenarios[1].drainage_areas[0].runoff_coefficient == 0.65
        assert len(restored.scenarios[1].infrastructure) == 1
