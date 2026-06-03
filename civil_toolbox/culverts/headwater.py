"""Headwater estimation utilities for culvert analysis.

Provides barrel geometry helpers (reusing the infrastructure sizing Manning
helpers) and the governing-headwater combiner. The control-specific headwater
equations live in :mod:`civil_toolbox.culverts.inlet_control` and
:mod:`civil_toolbox.culverts.outlet_control`; this module only supplies the
shared geometry and combines their results.

Geometry support:
    - circular: exact circle.
    - box / arch / elliptical: rectangular (box) approximation, consistent with
      the existing barrel-capacity screening in
      ``infrastructure_sizing.culverts``. Arch/elliptical are approximations and
      the caller should record that assumption.
"""

from __future__ import annotations

from civil_toolbox.culverts.errors import (
    InvalidCulvertInputError,
    UnsupportedCulvertTypeError,
)
from civil_toolbox.infrastructure import Culvert
from civil_toolbox.infrastructure_sizing.manning import (
    box_full_flow_area_sqft,
    box_full_flow_hydraulic_radius_ft,
    circular_pipe_full_flow_area_sqft,
    circular_pipe_full_flow_hydraulic_radius_ft,
)

# Shapes handled via the rectangular (box) approximation.
_BOX_LIKE_SHAPES = ("box", "arch", "elliptical")


def barrel_rise_ft(culvert: Culvert) -> float:
    """Return the barrel rise (vertical interior dimension) in feet.

    For circular culverts this is the diameter; for box-like culverts it is the
    height.

    Raises:
        InvalidCulvertInputError: If the required dimension is missing.
        UnsupportedCulvertTypeError: If the shape is not supported.
    """
    if culvert.shape == "circular":
        if culvert.diameter_in is None:
            raise InvalidCulvertInputError(
                f"Culvert '{culvert.name}' is circular but has no diameter_in"
            )
        return culvert.diameter_in / 12.0
    if culvert.shape in _BOX_LIKE_SHAPES:
        if culvert.height_in is None:
            raise InvalidCulvertInputError(
                f"Culvert '{culvert.name}' is {culvert.shape} but has no height_in"
            )
        return culvert.height_in / 12.0
    raise UnsupportedCulvertTypeError(
        f"Unsupported culvert shape for headwater analysis: '{culvert.shape}'"
    )


def barrel_full_area_sqft(culvert: Culvert) -> float:
    """Return the full-barrel cross-sectional area in square feet.

    Raises:
        InvalidCulvertInputError: If a required dimension is missing.
        UnsupportedCulvertTypeError: If the shape is not supported.
    """
    if culvert.shape == "circular":
        if culvert.diameter_in is None:
            raise InvalidCulvertInputError(
                f"Culvert '{culvert.name}' is circular but has no diameter_in"
            )
        return circular_pipe_full_flow_area_sqft(culvert.diameter_in / 12.0)
    if culvert.shape in _BOX_LIKE_SHAPES:
        if culvert.width_in is None or culvert.height_in is None:
            raise InvalidCulvertInputError(
                f"Culvert '{culvert.name}' is {culvert.shape} but missing width_in/height_in"
            )
        return box_full_flow_area_sqft(culvert.width_in / 12.0, culvert.height_in / 12.0)
    raise UnsupportedCulvertTypeError(
        f"Unsupported culvert shape for headwater analysis: '{culvert.shape}'"
    )


def barrel_full_hydraulic_radius_ft(culvert: Culvert) -> float:
    """Return the full-barrel hydraulic radius in feet.

    Raises:
        InvalidCulvertInputError: If a required dimension is missing.
        UnsupportedCulvertTypeError: If the shape is not supported.
    """
    if culvert.shape == "circular":
        if culvert.diameter_in is None:
            raise InvalidCulvertInputError(
                f"Culvert '{culvert.name}' is circular but has no diameter_in"
            )
        return circular_pipe_full_flow_hydraulic_radius_ft(culvert.diameter_in / 12.0)
    if culvert.shape in _BOX_LIKE_SHAPES:
        if culvert.width_in is None or culvert.height_in is None:
            raise InvalidCulvertInputError(
                f"Culvert '{culvert.name}' is {culvert.shape} but missing width_in/height_in"
            )
        return box_full_flow_hydraulic_radius_ft(
            culvert.width_in / 12.0, culvert.height_in / 12.0
        )
    raise UnsupportedCulvertTypeError(
        f"Unsupported culvert shape for headwater analysis: '{culvert.shape}'"
    )


def estimate_headwater_depth_ft(
    inlet_control_headwater_ft: float,
    outlet_control_headwater_ft: float,
) -> tuple[float, str]:
    """Combine inlet- and outlet-control headwaters into the governing value.

    Under the standard FHWA HDS-5 approach the culvert operates under whichever
    control produces the greater required headwater.

    Args:
        inlet_control_headwater_ft: Headwater depth under inlet control.
        outlet_control_headwater_ft: Headwater depth under outlet control.

    Returns:
        Tuple of (governing_headwater_depth_ft, governing_control) where
        governing_control is 'inlet' or 'outlet'.
    """
    if outlet_control_headwater_ft > inlet_control_headwater_ft:
        return outlet_control_headwater_ft, "outlet"
    return inlet_control_headwater_ft, "inlet"


def estimate_headwater_elevation_ft(
    headwater_depth_ft: float,
    inlet_invert_elevation_ft: float | None,
) -> float | None:
    """Convert a headwater depth to an absolute elevation.

    Args:
        headwater_depth_ft: Headwater depth above the inlet invert.
        inlet_invert_elevation_ft: Inlet (upstream) invert elevation, or None.

    Returns:
        Headwater elevation, or None if the invert elevation is unknown.
    """
    if inlet_invert_elevation_ft is None:
        return None
    return inlet_invert_elevation_ft + headwater_depth_ft
