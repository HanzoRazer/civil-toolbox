"""Pipe infrastructure model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.infrastructure.base import InfrastructureElementBase, ElementType
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError
from civil_toolbox.infrastructure.validation import (
    validate_positive,
    validate_non_negative,
    validate_mannings_n,
    validate_slope,
    validate_pipe_shape,
)


@dataclass
class Pipe(InfrastructureElementBase):
    """A pipe element in the drainage network.

    Supports circular, box, arch, and elliptical shapes.
    """

    element_type: ElementType = field(default=ElementType.PIPE, init=False)

    shape: str = "circular"
    diameter_in: float | None = None
    width_in: float | None = None
    height_in: float | None = None
    length_ft: float = 0.0
    slope_ft_per_ft: float = 0.0
    mannings_n: float = 0.013
    material: str | None = None

    upstream_node_id: str | None = None
    downstream_node_id: str | None = None
    upstream_invert_ft: float | None = None
    downstream_invert_ft: float | None = None

    def __post_init__(self) -> None:
        self.shape = validate_pipe_shape(self.shape)

        if self.length_ft <= 0:
            raise InvalidInfrastructureError("length_ft must be positive")
        validate_positive(self.length_ft, "length_ft")
        validate_slope(self.slope_ft_per_ft)
        validate_mannings_n(self.mannings_n)

        if self.shape == "circular":
            if self.diameter_in is None:
                raise InvalidInfrastructureError(
                    "diameter_in is required for circular pipes"
                )
            validate_positive(self.diameter_in, "diameter_in")
        elif self.shape in ("box", "arch", "elliptical"):
            if self.width_in is None or self.height_in is None:
                raise InvalidInfrastructureError(
                    f"width_in and height_in are required for {self.shape} pipes"
                )
            validate_positive(self.width_in, "width_in")
            validate_positive(self.height_in, "height_in")

    @property
    def diameter_ft(self) -> float | None:
        """Diameter in feet."""
        if self.diameter_in is not None:
            return self.diameter_in / 12.0
        return None

    @property
    def width_ft(self) -> float | None:
        """Width in feet."""
        if self.width_in is not None:
            return self.width_in / 12.0
        return None

    @property
    def height_ft(self) -> float | None:
        """Height in feet."""
        if self.height_in is not None:
            return self.height_in / 12.0
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "shape": self.shape,
            "diameter_in": self.diameter_in,
            "width_in": self.width_in,
            "height_in": self.height_in,
            "length_ft": self.length_ft,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "mannings_n": self.mannings_n,
            "material": self.material,
            "upstream_node_id": self.upstream_node_id,
            "downstream_node_id": self.downstream_node_id,
            "upstream_invert_ft": self.upstream_invert_ft,
            "downstream_invert_ft": self.downstream_invert_ft,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Pipe:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            shape=data.get("shape", "circular"),
            diameter_in=data.get("diameter_in"),
            width_in=data.get("width_in"),
            height_in=data.get("height_in"),
            length_ft=data["length_ft"],
            slope_ft_per_ft=data.get("slope_ft_per_ft", 0.0),
            mannings_n=data.get("mannings_n", 0.013),
            material=data.get("material"),
            upstream_node_id=data.get("upstream_node_id"),
            downstream_node_id=data.get("downstream_node_id"),
            upstream_invert_ft=data.get("upstream_invert_ft"),
            downstream_invert_ft=data.get("downstream_invert_ft"),
        )
