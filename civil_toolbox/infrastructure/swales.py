"""Swale infrastructure model."""

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
)


@dataclass
class Swale(InfrastructureElementBase):
    """A vegetated swale for conveying and treating stormwater.

    Typically shallow with gentle side slopes and vegetated lining.
    """

    element_type: ElementType = field(default=ElementType.SWALE, init=False)

    swale_type: str = "grass"
    bottom_width_ft: float = 0.0
    depth_ft: float = 0.0
    side_slope: float = 3.0
    length_ft: float = 0.0
    slope_ft_per_ft: float = 0.0
    mannings_n: float = 0.035

    vegetation_type: str | None = None
    check_dam_spacing_ft: float | None = None
    infiltration_rate_in_per_hr: float | None = None

    upstream_node_id: str | None = None
    downstream_node_id: str | None = None
    upstream_invert_ft: float | None = None
    downstream_invert_ft: float | None = None

    def __post_init__(self) -> None:
        valid_types = {"grass", "bioswale", "rock", "concrete"}
        if self.swale_type not in valid_types:
            raise InvalidInfrastructureError(
                f"swale_type must be one of {sorted(valid_types)}, "
                f"got '{self.swale_type}'"
            )

        if self.length_ft <= 0:
            raise InvalidInfrastructureError("length_ft must be positive")
        validate_positive(self.length_ft, "length_ft")
        validate_non_negative(self.bottom_width_ft, "bottom_width_ft")
        validate_positive(self.depth_ft, "depth_ft")
        validate_non_negative(self.side_slope, "side_slope")
        validate_slope(self.slope_ft_per_ft)
        validate_mannings_n(self.mannings_n)

        if self.check_dam_spacing_ft is not None:
            validate_positive(self.check_dam_spacing_ft, "check_dam_spacing_ft")
        if self.infiltration_rate_in_per_hr is not None:
            validate_non_negative(
                self.infiltration_rate_in_per_hr, "infiltration_rate_in_per_hr"
            )

    @property
    def top_width_ft(self) -> float:
        """Calculate top width at full depth."""
        return self.bottom_width_ft + 2 * self.side_slope * self.depth_ft

    @property
    def cross_sectional_area_sqft(self) -> float:
        """Calculate cross-sectional area at full depth."""
        return (self.bottom_width_ft + self.top_width_ft) / 2.0 * self.depth_ft

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "swale_type": self.swale_type,
            "bottom_width_ft": self.bottom_width_ft,
            "depth_ft": self.depth_ft,
            "side_slope": self.side_slope,
            "length_ft": self.length_ft,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "mannings_n": self.mannings_n,
            "vegetation_type": self.vegetation_type,
            "check_dam_spacing_ft": self.check_dam_spacing_ft,
            "infiltration_rate_in_per_hr": self.infiltration_rate_in_per_hr,
            "upstream_node_id": self.upstream_node_id,
            "downstream_node_id": self.downstream_node_id,
            "upstream_invert_ft": self.upstream_invert_ft,
            "downstream_invert_ft": self.downstream_invert_ft,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Swale:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            swale_type=data.get("swale_type", "grass"),
            bottom_width_ft=data.get("bottom_width_ft", 0.0),
            depth_ft=data.get("depth_ft", 0.0),
            side_slope=data.get("side_slope", 3.0),
            length_ft=data["length_ft"],
            slope_ft_per_ft=data.get("slope_ft_per_ft", 0.0),
            mannings_n=data.get("mannings_n", 0.035),
            vegetation_type=data.get("vegetation_type"),
            check_dam_spacing_ft=data.get("check_dam_spacing_ft"),
            infiltration_rate_in_per_hr=data.get("infiltration_rate_in_per_hr"),
            upstream_node_id=data.get("upstream_node_id"),
            downstream_node_id=data.get("downstream_node_id"),
            upstream_invert_ft=data.get("upstream_invert_ft"),
            downstream_invert_ft=data.get("downstream_invert_ft"),
        )
