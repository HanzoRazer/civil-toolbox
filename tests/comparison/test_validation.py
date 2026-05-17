"""Tests for comparison validation."""

import pytest

from civil_toolbox.comparison.validation import (
    ComparisonValidationError,
    SameScenarioError,
    EmptyScenarioError,
    NoMatchesError,
    InvalidExplicitMapError,
    validate_scenarios_different,
    validate_scenario_has_entities,
    validate_explicit_map,
    validate_comparison_inputs,
)
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.flow_path import FlowPath


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    def test_same_scenario_error_inherits(self):
        """SameScenarioError inherits from ComparisonValidationError."""
        error = SameScenarioError("scenario-1")
        assert isinstance(error, ComparisonValidationError)

    def test_empty_scenario_error_inherits(self):
        """EmptyScenarioError inherits from ComparisonValidationError."""
        error = EmptyScenarioError("Test", "DrainageArea")
        assert isinstance(error, ComparisonValidationError)

    def test_no_matches_error_inherits(self):
        """NoMatchesError inherits from ComparisonValidationError."""
        error = NoMatchesError("Existing", "Proposed")
        assert isinstance(error, ComparisonValidationError)

    def test_invalid_explicit_map_error_inherits(self):
        """InvalidExplicitMapError inherits from ComparisonValidationError."""
        error = InvalidExplicitMapError("Invalid map")
        assert isinstance(error, ComparisonValidationError)


class TestSameScenarioError:
    """Tests for SameScenarioError."""

    def test_stores_scenario_id(self):
        """Stores the scenario ID."""
        error = SameScenarioError("scenario-1")
        assert error.scenario_id == "scenario-1"

    def test_message_includes_id(self):
        """Error message includes scenario ID."""
        error = SameScenarioError("scenario-1")
        assert "scenario-1" in str(error)


class TestEmptyScenarioError:
    """Tests for EmptyScenarioError."""

    def test_stores_scenario_name(self):
        """Stores the scenario name."""
        error = EmptyScenarioError("Test Scenario", "DrainageArea")
        assert error.scenario_name == "Test Scenario"

    def test_stores_entity_type(self):
        """Stores the entity type."""
        error = EmptyScenarioError("Test", "FlowPath")
        assert error.entity_type == "FlowPath"

    def test_message_includes_details(self):
        """Error message includes scenario name and entity type."""
        error = EmptyScenarioError("Test Scenario", "DrainageArea")
        assert "Test Scenario" in str(error)
        assert "DrainageArea" in str(error)


class TestInvalidExplicitMapError:
    """Tests for InvalidExplicitMapError."""

    def test_stores_invalid_keys(self):
        """Stores the invalid keys."""
        error = InvalidExplicitMapError("Invalid", invalid_keys=["key1", "key2"])
        assert error.invalid_keys == ["key1", "key2"]

    def test_defaults_to_empty_list(self):
        """Defaults to empty list when no keys provided."""
        error = InvalidExplicitMapError("Invalid")
        assert error.invalid_keys == []


class TestValidateScenariosDifferent:
    """Tests for validate_scenarios_different."""

    def test_passes_for_different_scenarios(self):
        """Passes when scenarios have different IDs."""
        baseline = Scenario(id="scenario-1", name="Existing")
        comparison = Scenario(id="scenario-2", name="Proposed")

        validate_scenarios_different(baseline, comparison)

    def test_raises_for_same_scenario(self):
        """Raises when scenarios have same ID."""
        scenario = Scenario(id="scenario-1", name="Test")

        with pytest.raises(SameScenarioError) as exc_info:
            validate_scenarios_different(scenario, scenario)

        assert exc_info.value.scenario_id == "scenario-1"


class TestValidateScenarioHasEntities:
    """Tests for validate_scenario_has_entities."""

    def test_passes_with_drainage_areas(self):
        """Passes when scenario has drainage areas."""
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(name="Area A"))

        validate_scenario_has_entities(scenario, "DrainageArea")

    def test_raises_without_drainage_areas(self):
        """Raises when scenario has no drainage areas."""
        scenario = Scenario(name="Test")

        with pytest.raises(EmptyScenarioError) as exc_info:
            validate_scenario_has_entities(scenario, "DrainageArea")

        assert exc_info.value.scenario_name == "Test"
        assert exc_info.value.entity_type == "DrainageArea"

    def test_passes_with_flow_paths(self):
        """Passes when scenario has flow paths."""
        scenario = Scenario(name="Test")
        scenario.add_flow_path(FlowPath(name="Path A"))

        validate_scenario_has_entities(scenario, "FlowPath")

    def test_raises_without_flow_paths(self):
        """Raises when scenario has no flow paths."""
        scenario = Scenario(name="Test")

        with pytest.raises(EmptyScenarioError) as exc_info:
            validate_scenario_has_entities(scenario, "FlowPath")

        assert exc_info.value.entity_type == "FlowPath"

    def test_raises_for_unsupported_entity_type(self):
        """Raises ValueError for unsupported entity type."""
        scenario = Scenario(name="Test")

        with pytest.raises(ValueError, match="Unsupported entity type"):
            validate_scenario_has_entities(scenario, "Unknown")


class TestValidateExplicitMap:
    """Tests for validate_explicit_map."""

    def test_passes_with_valid_map(self):
        """Passes when all IDs in map exist."""
        baseline = Scenario(name="Existing")
        baseline.add_drainage_area(DrainageArea(id="area-1", name="Area A"))

        comparison = Scenario(name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="area-2", name="Area A"))

        explicit_map = {"area-1": "area-2"}

        validate_explicit_map(explicit_map, baseline, comparison)

    def test_raises_for_invalid_baseline_id(self):
        """Raises when baseline ID not found."""
        baseline = Scenario(name="Existing")
        baseline.add_drainage_area(DrainageArea(id="area-1", name="Area A"))

        comparison = Scenario(name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="area-2", name="Area A"))

        explicit_map = {"invalid-id": "area-2"}

        with pytest.raises(InvalidExplicitMapError) as exc_info:
            validate_explicit_map(explicit_map, baseline, comparison)

        assert "invalid-id" in exc_info.value.invalid_keys

    def test_raises_for_invalid_comparison_id(self):
        """Raises when comparison ID not found."""
        baseline = Scenario(name="Existing")
        baseline.add_drainage_area(DrainageArea(id="area-1", name="Area A"))

        comparison = Scenario(name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="area-2", name="Area A"))

        explicit_map = {"area-1": "invalid-id"}

        with pytest.raises(InvalidExplicitMapError) as exc_info:
            validate_explicit_map(explicit_map, baseline, comparison)

        assert "invalid-id" in exc_info.value.invalid_keys

    def test_raises_for_unsupported_entity_type(self):
        """Raises ValueError for unsupported entity type."""
        baseline = Scenario(name="Existing")
        comparison = Scenario(name="Proposed")

        with pytest.raises(ValueError, match="Unsupported entity type"):
            validate_explicit_map({}, baseline, comparison, "Unknown")


class TestValidateComparisonInputs:
    """Tests for validate_comparison_inputs."""

    def test_passes_with_valid_inputs(self):
        """Passes with valid inputs."""
        baseline = Scenario(id="s-1", name="Existing")
        baseline.add_drainage_area(DrainageArea(name="Area A"))

        comparison = Scenario(id="s-2", name="Proposed")
        comparison.add_drainage_area(DrainageArea(name="Area A"))

        validate_comparison_inputs(baseline, comparison)

    def test_raises_for_same_scenario(self):
        """Raises for same scenario."""
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(name="Area A"))

        with pytest.raises(SameScenarioError):
            validate_comparison_inputs(scenario, scenario)

    def test_raises_for_empty_baseline(self):
        """Raises when baseline has no entities."""
        baseline = Scenario(id="s-1", name="Existing")
        comparison = Scenario(id="s-2", name="Proposed")
        comparison.add_drainage_area(DrainageArea(name="Area A"))

        with pytest.raises(EmptyScenarioError):
            validate_comparison_inputs(baseline, comparison)

    def test_raises_for_empty_comparison(self):
        """Raises when comparison has no entities."""
        baseline = Scenario(id="s-1", name="Existing")
        baseline.add_drainage_area(DrainageArea(name="Area A"))
        comparison = Scenario(id="s-2", name="Proposed")

        with pytest.raises(EmptyScenarioError):
            validate_comparison_inputs(baseline, comparison)

    def test_skips_entity_check_when_not_required(self):
        """Skips entity check when require_entities=False."""
        baseline = Scenario(id="s-1", name="Existing")
        comparison = Scenario(id="s-2", name="Proposed")

        validate_comparison_inputs(baseline, comparison, require_entities=False)

    def test_validates_explicit_map(self):
        """Validates explicit map when provided."""
        baseline = Scenario(id="s-1", name="Existing")
        baseline.add_drainage_area(DrainageArea(id="area-1", name="Area A"))

        comparison = Scenario(id="s-2", name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="area-2", name="Area A"))

        explicit_map = {"invalid": "area-2"}

        with pytest.raises(InvalidExplicitMapError):
            validate_comparison_inputs(baseline, comparison, explicit_map=explicit_map)
