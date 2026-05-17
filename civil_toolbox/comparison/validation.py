"""Validation utilities for comparison operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from civil_toolbox.domain.scenario import Scenario


class ComparisonValidationError(Exception):
    """Base exception for comparison validation errors."""

    pass


class SameScenarioError(ComparisonValidationError):
    """Raised when comparing a scenario to itself."""

    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        super().__init__(f"Cannot compare scenario '{scenario_id}' to itself")


class EmptyScenarioError(ComparisonValidationError):
    """Raised when a scenario has no entities to compare."""

    def __init__(self, scenario_name: str, entity_type: str):
        self.scenario_name = scenario_name
        self.entity_type = entity_type
        super().__init__(
            f"Scenario '{scenario_name}' has no {entity_type} entities to compare"
        )


class NoMatchesError(ComparisonValidationError):
    """Raised when no entities could be matched between scenarios."""

    def __init__(self, baseline_name: str, comparison_name: str):
        self.baseline_name = baseline_name
        self.comparison_name = comparison_name
        super().__init__(
            f"No entities could be matched between '{baseline_name}' "
            f"and '{comparison_name}'"
        )


class InvalidExplicitMapError(ComparisonValidationError):
    """Raised when explicit map contains invalid entries."""

    def __init__(self, message: str, invalid_keys: list[str] | None = None):
        self.invalid_keys = invalid_keys or []
        super().__init__(message)


def validate_scenarios_different(
    baseline: Scenario,
    comparison: Scenario,
) -> None:
    """Validate that baseline and comparison are different scenarios.

    Raises:
        SameScenarioError: If scenarios have the same ID.
    """
    if baseline.id == comparison.id:
        raise SameScenarioError(baseline.id)


def validate_scenario_has_entities(
    scenario: Scenario,
    entity_type: str = "DrainageArea",
) -> None:
    """Validate that scenario has entities of the specified type.

    Raises:
        EmptyScenarioError: If scenario has no entities of the type.
    """
    if entity_type == "DrainageArea":
        if not scenario.drainage_areas:
            raise EmptyScenarioError(scenario.name, entity_type)
    elif entity_type == "FlowPath":
        if not scenario.flow_paths:
            raise EmptyScenarioError(scenario.name, entity_type)
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")


def validate_explicit_map(
    explicit_map: dict[str, str],
    baseline: Scenario,
    comparison: Scenario,
    entity_type: str = "DrainageArea",
) -> None:
    """Validate that explicit map references valid entity IDs.

    Raises:
        InvalidExplicitMapError: If map contains invalid IDs.
    """
    if entity_type == "DrainageArea":
        baseline_ids = {a.id for a in baseline.drainage_areas}
        comparison_ids = {a.id for a in comparison.drainage_areas}
    elif entity_type == "FlowPath":
        baseline_ids = {p.id for p in baseline.flow_paths}
        comparison_ids = {p.id for p in comparison.flow_paths}
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")

    invalid_baseline_keys = [
        k for k in explicit_map.keys() if k not in baseline_ids
    ]
    invalid_comparison_values = [
        v for v in explicit_map.values() if v not in comparison_ids
    ]

    if invalid_baseline_keys:
        raise InvalidExplicitMapError(
            f"Explicit map contains baseline IDs not in scenario: "
            f"{invalid_baseline_keys}",
            invalid_keys=invalid_baseline_keys,
        )

    if invalid_comparison_values:
        raise InvalidExplicitMapError(
            f"Explicit map contains comparison IDs not in scenario: "
            f"{invalid_comparison_values}",
            invalid_keys=invalid_comparison_values,
        )


def validate_comparison_inputs(
    baseline: Scenario,
    comparison: Scenario,
    explicit_map: dict[str, str] | None = None,
    entity_type: str = "DrainageArea",
    require_entities: bool = True,
) -> None:
    """Validate all inputs for a comparison operation.

    Args:
        baseline: Baseline scenario.
        comparison: Comparison scenario.
        explicit_map: Optional explicit ID mapping.
        entity_type: Type of entity to compare.
        require_entities: If True, require at least one entity in each scenario.

    Raises:
        SameScenarioError: If scenarios are the same.
        EmptyScenarioError: If a scenario has no entities (when required).
        InvalidExplicitMapError: If explicit map is invalid.
    """
    validate_scenarios_different(baseline, comparison)

    if require_entities:
        validate_scenario_has_entities(baseline, entity_type)
        validate_scenario_has_entities(comparison, entity_type)

    if explicit_map:
        validate_explicit_map(explicit_map, baseline, comparison, entity_type)
