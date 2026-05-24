"""Inlet infrastructure model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.infrastructure.base import InfrastructureElementBase, ElementType
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError
from civil_toolbox.infrastructure.validation import (
    validate_positive,
    validate_non_negative,
    validate_inlet_type,
)


@dataclass
class Inlet(InfrastructureElementBase):
    """An inlet element for collecting surface runoff.

    Supports grate, curb opening, combination, and slotted inlet types.
    """

    element_type: ElementType = field(default=ElementType.INLET, init=False)

    inlet_type: str = "grate"
    grate_length_in: float | None = None
    grate_width_in: float | None = None
    opening_length_ft: float | None = None
    opening_height_in: float | None = None
    clogging_factor: float = 0.0

    node_id: str | None = None
    longitudinal_slope_ft_per_ft: float | None = None
    cross_slope_ft_per_ft: float | None = None

    def __post_init__(self) -> None:
        self.inlet_type = validate_inlet_type(self.inlet_type)

        if self.clogging_factor < 0 or self.clogging_factor > 1:
            raise InvalidInfrastructureError(
                f"clogging_factor must be between 0 and 1, got {self.clogging_factor}"
            )

        if self.grate_length_in is not None:
            validate_positive(self.grate_length_in, "grate_length_in")
        if self.grate_width_in is not None:
            validate_positive(self.grate_width_in, "grate_width_in")
        if self.opening_length_ft is not None:
            validate_positive(self.opening_length_ft, "opening_length_ft")
        if self.opening_height_in is not None:
            validate_positive(self.opening_height_in, "opening_height_in")

    @property
    def effective_clogging_factor(self) -> float:
        """Factor to reduce capacity (1.0 = full capacity, 0.0 = fully clogged)."""
        return 1.0 - self.clogging_factor

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "inlet_type": self.inlet_type,
            "grate_length_in": self.grate_length_in,
            "grate_width_in": self.grate_width_in,
            "opening_length_ft": self.opening_length_ft,
            "opening_height_in": self.opening_height_in,
            "clogging_factor": self.clogging_factor,
            "node_id": self.node_id,
            "longitudinal_slope_ft_per_ft": self.longitudinal_slope_ft_per_ft,
            "cross_slope_ft_per_ft": self.cross_slope_ft_per_ft,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Inlet:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            inlet_type=data.get("inlet_type", "grate"),
            grate_length_in=data.get("grate_length_in"),
            grate_width_in=data.get("grate_width_in"),
            opening_length_ft=data.get("opening_length_ft"),
            opening_height_in=data.get("opening_height_in"),
            clogging_factor=data.get("clogging_factor", 0.0),
            node_id=data.get("node_id"),
            longitudinal_slope_ft_per_ft=data.get("longitudinal_slope_ft_per_ft"),
            cross_slope_ft_per_ft=data.get("cross_slope_ft_per_ft"),
        )
