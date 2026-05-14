"""Scenario domain entity for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TYPE_CHECKING

from civil_toolbox.domain.base import BaseEntity

if TYPE_CHECKING:
    from civil_toolbox.domain.drainage import DrainageArea
    from civil_toolbox.domain.storm import StormEvent
    from civil_toolbox.domain.flow_path import FlowPath
    from civil_toolbox.domain.infrastructure import InfrastructureElement
    from civil_toolbox.domain.calculation import CalculationResult


@dataclass
class Scenario(BaseEntity):
    """A scenario within a project.

    Scenarios represent different conditions or alternatives:
    - Existing conditions
    - Proposed development
    - With/without detention
    - Design alternatives

    Each scenario contains its own drainage areas, storm events,
    flow paths, infrastructure, and calculation results.
    """

    name: str = ""
    description: str | None = None
    project_id: str | None = None
    drainage_areas: list[DrainageArea] = field(default_factory=list)
    storm_events: list[StormEvent] = field(default_factory=list)
    flow_paths: list[FlowPath] = field(default_factory=list)
    infrastructure: list[InfrastructureElement] = field(default_factory=list)
    calculation_results: list[CalculationResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Scenario requires a name")

    def add_drainage_area(self, area: DrainageArea) -> None:
        """Add a drainage area to the scenario."""
        from civil_toolbox.domain.drainage import DrainageArea

        if not isinstance(area, DrainageArea):
            raise TypeError("Expected a DrainageArea instance")
        area.scenario_id = self.id
        self.drainage_areas.append(area)
        self.touch()

    def add_storm_event(self, event: StormEvent) -> None:
        """Add a storm event to the scenario."""
        from civil_toolbox.domain.storm import StormEvent

        if not isinstance(event, StormEvent):
            raise TypeError("Expected a StormEvent instance")
        event.scenario_id = self.id
        self.storm_events.append(event)
        self.touch()

    def add_flow_path(self, path: FlowPath) -> None:
        """Add a flow path to the scenario."""
        from civil_toolbox.domain.flow_path import FlowPath

        if not isinstance(path, FlowPath):
            raise TypeError("Expected a FlowPath instance")
        path.scenario_id = self.id
        self.flow_paths.append(path)
        self.touch()

    def add_infrastructure(self, element: InfrastructureElement) -> None:
        """Add an infrastructure element to the scenario."""
        from civil_toolbox.domain.infrastructure import InfrastructureElement

        if not isinstance(element, InfrastructureElement):
            raise TypeError("Expected an InfrastructureElement instance")
        element.scenario_id = self.id
        self.infrastructure.append(element)
        self.touch()

    def add_calculation_result(self, result: CalculationResult) -> None:
        """Add a calculation result to the scenario."""
        from civil_toolbox.domain.calculation import CalculationResult

        if not isinstance(result, CalculationResult):
            raise TypeError("Expected a CalculationResult instance")
        result.scenario_id = self.id
        self.calculation_results.append(result)
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "drainage_areas": [a.to_dict() for a in self.drainage_areas],
            "storm_events": [e.to_dict() for e in self.storm_events],
            "flow_paths": [p.to_dict() for p in self.flow_paths],
            "infrastructure": [i.to_dict() for i in self.infrastructure],
            "calculation_results": [r.to_dict() for r in self.calculation_results],
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Scenario:
        """Deserialize from dictionary."""
        from civil_toolbox.domain.drainage import DrainageArea
        from civil_toolbox.domain.storm import StormEvent
        from civil_toolbox.domain.flow_path import FlowPath
        from civil_toolbox.domain.infrastructure import InfrastructureElement
        from civil_toolbox.domain.calculation import CalculationResult

        scenario = cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            name=data["name"],
            description=data.get("description"),
            project_id=data.get("project_id"),
            drainage_areas=[],
            storm_events=[],
            flow_paths=[],
            infrastructure=[],
            calculation_results=[],
        )

        for a_data in data.get("drainage_areas", []):
            area = DrainageArea.from_dict(a_data)
            area.scenario_id = scenario.id
            scenario.drainage_areas.append(area)

        for e_data in data.get("storm_events", []):
            event = StormEvent.from_dict(e_data)
            event.scenario_id = scenario.id
            scenario.storm_events.append(event)

        for p_data in data.get("flow_paths", []):
            path = FlowPath.from_dict(p_data)
            path.scenario_id = scenario.id
            scenario.flow_paths.append(path)

        for i_data in data.get("infrastructure", []):
            element = InfrastructureElement.from_dict(i_data)
            element.scenario_id = scenario.id
            scenario.infrastructure.append(element)

        for r_data in data.get("calculation_results", []):
            result = CalculationResult.from_dict(r_data)
            result.scenario_id = scenario.id
            scenario.calculation_results.append(result)

        return scenario
