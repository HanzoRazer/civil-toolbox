"""Project domain entity for Civil Toolbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TYPE_CHECKING

from civil_toolbox.domain.base import BaseEntity, _generate_id, _utc_now

if TYPE_CHECKING:
    from civil_toolbox.domain.scenario import Scenario


@dataclass
class DesignCriteria:
    """Design criteria governing a project's calculations.

    Defines the engineering standards and parameters that apply
    to all scenarios within a project.
    """

    design_storm_years: int | None = None
    rainfall_distribution: str | None = None
    jurisdiction: str | None = None
    allowed_methods: list[str] = field(default_factory=list)
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "design_storm_years": self.design_storm_years,
            "rainfall_distribution": self.rainfall_distribution,
            "jurisdiction": self.jurisdiction,
            "allowed_methods": self.allowed_methods,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DesignCriteria:
        """Deserialize from dictionary."""
        return cls(
            design_storm_years=data.get("design_storm_years"),
            rainfall_distribution=data.get("rainfall_distribution"),
            jurisdiction=data.get("jurisdiction"),
            allowed_methods=data.get("allowed_methods", []),
            notes=data.get("notes"),
        )


@dataclass
class Project(BaseEntity):
    """A drainage analysis project.

    Projects organize scenarios, calculations, and reports for a
    specific site or development.
    """

    name: str = ""
    client: str | None = None
    description: str | None = None
    jurisdiction: str | None = None
    design_criteria: DesignCriteria = field(default_factory=DesignCriteria)
    scenarios: list[Scenario] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Project requires a name")

    def add_scenario(self, scenario: Scenario) -> None:
        """Add a scenario to the project."""
        from civil_toolbox.domain.scenario import Scenario

        if not isinstance(scenario, Scenario):
            raise TypeError("Expected a Scenario instance")
        scenario.project_id = self.id
        self.scenarios.append(scenario)
        self.touch()

    def remove_scenario(self, scenario_id: str) -> bool:
        """Remove a scenario by ID. Returns True if removed."""
        for i, s in enumerate(self.scenarios):
            if s.id == scenario_id:
                self.scenarios.pop(i)
                self.touch()
                return True
        return False

    def get_scenario(self, scenario_id: str) -> Scenario | None:
        """Get a scenario by ID."""
        for s in self.scenarios:
            if s.id == scenario_id:
                return s
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "client": self.client,
            "description": self.description,
            "jurisdiction": self.jurisdiction,
            "design_criteria": self.design_criteria.to_dict(),
            "scenarios": [s.to_dict() for s in self.scenarios],
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        """Deserialize from dictionary."""
        from civil_toolbox.domain.scenario import Scenario

        criteria_data = data.get("design_criteria", {})
        scenarios_data = data.get("scenarios", [])

        project = cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            name=data["name"],
            client=data.get("client"),
            description=data.get("description"),
            jurisdiction=data.get("jurisdiction"),
            design_criteria=DesignCriteria.from_dict(criteria_data),
            scenarios=[],
        )

        for s_data in scenarios_data:
            scenario = Scenario.from_dict(s_data)
            scenario.project_id = project.id
            project.scenarios.append(scenario)

        return project
