"""Open channel infrastructure model."""

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
    validate_channel_shape,
)


@dataclass
class OpenChannel(InfrastructureElementBase):
    """An open channel element for conveying water.

    Supports rectangular, trapezoidal, triangular, and parabolic shapes.
    """

    element_type: ElementType = field(default=ElementType.CHANNEL, init=False)

    shape: str = "trapezoidal"
    bottom_width_ft: float | None = None
    depth_ft: float = 0.0
    side_slope: float | None = None
    side_slope_left: float | None = None
    side_slope_right: float | None = None

    length_ft: float = 0.0
    slope_ft_per_ft: float = 0.0
    mannings_n: float = 0.035
    lining: str | None = None

    upstream_node_id: str | None = None
    downstream_node_id: str | None = None
    upstream_invert_ft: float | None = None
    downstream_invert_ft: float | None = None

    freeboard_ft: float | None = None

    def __post_init__(self) -> None:
        self.shape = validate_channel_shape(self.shape)

        if self.length_ft <= 0:
            raise InvalidInfrastructureError("length_ft must be positive")
        validate_positive(self.length_ft, "length_ft")
        validate_positive(self.depth_ft, "depth_ft")
        validate_slope(self.slope_ft_per_ft)
        validate_mannings_n(self.mannings_n)

        if self.shape == "rectangular":
            if self.bottom_width_ft is None:
                raise InvalidInfrastructureError(
                    "bottom_width_ft is required for rectangular channels"
                )
            validate_positive(self.bottom_width_ft, "bottom_width_ft")

        elif self.shape == "trapezoidal":
            if self.bottom_width_ft is None:
                raise InvalidInfrastructureError(
                    "bottom_width_ft is required for trapezoidal channels"
                )
            validate_positive(self.bottom_width_ft, "bottom_width_ft")
            if self.side_slope is None:
                if self.side_slope_left is None or self.side_slope_right is None:
                    raise InvalidInfrastructureError(
                        "side_slope or side_slope_left/right required for trapezoidal"
                    )
                validate_non_negative(self.side_slope_left, "side_slope_left")
                validate_non_negative(self.side_slope_right, "side_slope_right")
            else:
                validate_non_negative(self.side_slope, "side_slope")

        elif self.shape == "triangular":
            if self.side_slope is None:
                if self.side_slope_left is None or self.side_slope_right is None:
                    raise InvalidInfrastructureError(
                        "side_slope or side_slope_left/right required for triangular"
                    )
                validate_non_negative(self.side_slope_left, "side_slope_left")
                validate_non_negative(self.side_slope_right, "side_slope_right")
            else:
                validate_non_negative(self.side_slope, "side_slope")

        if self.freeboard_ft is not None:
            validate_non_negative(self.freeboard_ft, "freeboard_ft")

    @property
    def effective_side_slope_left(self) -> float | None:
        """Left side slope (horizontal:vertical)."""
        if self.side_slope_left is not None:
            return self.side_slope_left
        return self.side_slope

    @property
    def effective_side_slope_right(self) -> float | None:
        """Right side slope (horizontal:vertical)."""
        if self.side_slope_right is not None:
            return self.side_slope_right
        return self.side_slope

    @property
    def top_width_ft(self) -> float | None:
        """Calculate top width at full depth."""
        if self.shape == "rectangular":
            return self.bottom_width_ft
        elif self.shape in ("trapezoidal", "triangular"):
            base = self.bottom_width_ft or 0.0
            ss_left = self.effective_side_slope_left or 0.0
            ss_right = self.effective_side_slope_right or 0.0
            return base + self.depth_ft * (ss_left + ss_right)
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        base = super().to_dict()
        base.update({
            "element_type": self.element_type.value,
            "shape": self.shape,
            "bottom_width_ft": self.bottom_width_ft,
            "depth_ft": self.depth_ft,
            "side_slope": self.side_slope,
            "side_slope_left": self.side_slope_left,
            "side_slope_right": self.side_slope_right,
            "length_ft": self.length_ft,
            "slope_ft_per_ft": self.slope_ft_per_ft,
            "mannings_n": self.mannings_n,
            "lining": self.lining,
            "upstream_node_id": self.upstream_node_id,
            "downstream_node_id": self.downstream_node_id,
            "upstream_invert_ft": self.upstream_invert_ft,
            "downstream_invert_ft": self.downstream_invert_ft,
            "freeboard_ft": self.freeboard_ft,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OpenChannel:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
            shape=data.get("shape", "trapezoidal"),
            bottom_width_ft=data.get("bottom_width_ft"),
            depth_ft=data.get("depth_ft", 0.0),
            side_slope=data.get("side_slope"),
            side_slope_left=data.get("side_slope_left"),
            side_slope_right=data.get("side_slope_right"),
            length_ft=data["length_ft"],
            slope_ft_per_ft=data.get("slope_ft_per_ft", 0.0),
            mannings_n=data.get("mannings_n", 0.035),
            lining=data.get("lining"),
            upstream_node_id=data.get("upstream_node_id"),
            downstream_node_id=data.get("downstream_node_id"),
            upstream_invert_ft=data.get("upstream_invert_ft"),
            downstream_invert_ft=data.get("downstream_invert_ft"),
            freeboard_ft=data.get("freeboard_ft"),
        )
