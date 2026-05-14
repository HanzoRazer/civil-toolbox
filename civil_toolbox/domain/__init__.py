"""Civil Toolbox domain model entities."""

from civil_toolbox.domain.base import (
    BaseEntity,
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)
from civil_toolbox.domain.project import Project, DesignCriteria
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.domain.infrastructure import InfrastructureElement
from civil_toolbox.domain.calculation import CalculationResult

__all__ = [
    "BaseEntity",
    "EngineeringAssumption",
    "EngineeringReference",
    "ValidationWarning",
    "Project",
    "DesignCriteria",
    "Scenario",
    "DrainageArea",
    "StormEvent",
    "FlowPath",
    "FlowPathSegment",
    "InfrastructureElement",
    "CalculationResult",
]
