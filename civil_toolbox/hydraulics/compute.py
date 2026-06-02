"""Pipe reach hydraulic calculations."""

from __future__ import annotations

from civil_toolbox.hydraulics.errors import (
    InvalidHydraulicInputError,
    MissingHydraulicDataError,
)
from civil_toolbox.hydraulics.hgl import (
    velocity_fps,
    velocity_head_ft,
    friction_loss_ft,
    friction_slope_from_manning,
    pipe_crown_elevation_ft,
    classify_surcharge_status,
    freeboard_ft,
)
from civil_toolbox.hydraulics.models import (
    PipeReachInput,
    PipeReachHydraulicResult,
    HydraulicWarning,
    HydraulicProfileResult,
)
from civil_toolbox.infrastructure_sizing.manning import (
    circular_pipe_full_flow_area_sqft,
    circular_pipe_full_flow_hydraulic_radius_ft,
    box_full_flow_area_sqft,
    box_full_flow_hydraulic_radius_ft,
)


def compute_pipe_reach_hydraulics(
    reach: PipeReachInput,
    downstream_hgl_ft: float,
) -> PipeReachHydraulicResult:
    """Compute hydraulics for a single pipe reach.

    Uses simplified full-flow assumptions (pressurized flow).
    Propagates HGL from downstream to upstream using friction losses.

    Args:
        reach: Pipe reach input data.
        downstream_hgl_ft: Known HGL at downstream end (ft).

    Returns:
        PipeReachHydraulicResult with computed values.

    Raises:
        MissingHydraulicDataError: If required geometry is missing.
        InvalidHydraulicInputError: If inputs are invalid.
    """
    warnings: list[HydraulicWarning] = []

    if reach.is_circular:
        diameter_ft = reach.diameter_in / 12.0
        area_sqft = circular_pipe_full_flow_area_sqft(diameter_ft)
        hydraulic_radius_ft = circular_pipe_full_flow_hydraulic_radius_ft(diameter_ft)
    elif reach.is_rectangular:
        width_ft = reach.width_in / 12.0
        height_ft = reach.height_in / 12.0
        area_sqft = box_full_flow_area_sqft(width_ft, height_ft)
        hydraulic_radius_ft = box_full_flow_hydraulic_radius_ft(width_ft, height_ft)
    else:
        raise MissingHydraulicDataError(
            f"Reach '{reach.id}' has no valid geometry (need diameter or width+height)"
        )

    flow_cfs = reach.design_flow_cfs
    v = velocity_fps(flow_cfs, area_sqft)
    vh = velocity_head_ft(v)

    sf = friction_slope_from_manning(
        flow_cfs=flow_cfs,
        area_sqft=area_sqft,
        hydraulic_radius_ft=hydraulic_radius_ft,
        mannings_n=reach.roughness_n,
    )
    hf = friction_loss_ft(sf, reach.length_ft)

    upstream_hgl_ft = downstream_hgl_ft + hf

    downstream_egl_ft = downstream_hgl_ft + vh
    upstream_egl_ft = upstream_hgl_ft + vh

    ds_crown = pipe_crown_elevation_ft(
        reach.downstream_invert_elevation_ft,
        diameter_in=reach.diameter_in,
        height_in=reach.height_in,
    )
    us_crown = pipe_crown_elevation_ft(
        reach.upstream_invert_elevation_ft,
        diameter_in=reach.diameter_in,
        height_in=reach.height_in,
    )

    ds_surcharge = classify_surcharge_status(
        downstream_hgl_ft,
        ds_crown,
        reach.downstream_rim_elevation_ft,
    )
    us_surcharge = classify_surcharge_status(
        upstream_hgl_ft,
        us_crown,
        reach.upstream_rim_elevation_ft,
    )

    ds_freeboard = freeboard_ft(reach.downstream_rim_elevation_ft, downstream_hgl_ft)
    us_freeboard = freeboard_ft(reach.upstream_rim_elevation_ft, upstream_hgl_ft)

    if ds_surcharge == "surcharged_above_rim":
        warnings.append(
            HydraulicWarning(
                code="surcharge_above_rim",
                message=f"HGL exceeds rim elevation at downstream end of reach '{reach.id}'",
                severity="error",
                entity_id=reach.id,
            )
        )
    if us_surcharge == "surcharged_above_rim":
        warnings.append(
            HydraulicWarning(
                code="surcharge_above_rim",
                message=f"HGL exceeds rim elevation at upstream end of reach '{reach.id}'",
                severity="error",
                entity_id=reach.id,
            )
        )

    return PipeReachHydraulicResult(
        reach_id=reach.id,
        pipe_id=reach.pipe_id,
        design_flow_cfs=flow_cfs,
        flow_area_sqft=area_sqft,
        velocity_fps=v,
        velocity_head_ft=vh,
        friction_slope_ft_per_ft=sf,
        friction_loss_ft=hf,
        downstream_hgl_ft=downstream_hgl_ft,
        upstream_hgl_ft=upstream_hgl_ft,
        downstream_egl_ft=downstream_egl_ft,
        upstream_egl_ft=upstream_egl_ft,
        downstream_crown_elevation_ft=ds_crown,
        upstream_crown_elevation_ft=us_crown,
        downstream_rim_elevation_ft=reach.downstream_rim_elevation_ft,
        upstream_rim_elevation_ft=reach.upstream_rim_elevation_ft,
        downstream_freeboard_ft=ds_freeboard,
        upstream_freeboard_ft=us_freeboard,
        downstream_surcharge_status=ds_surcharge,
        upstream_surcharge_status=us_surcharge,
        warnings=warnings,
    )


def compute_hgl_profile(
    reaches: list[PipeReachInput],
    starting_downstream_hgl_ft: float,
    name: str = "Hydraulic Grade Line Profile",
) -> HydraulicProfileResult:
    """Compute HGL profile for ordered pipe reaches.

    Processes reaches from downstream to upstream, propagating HGL.
    Each reach's upstream HGL becomes the next reach's downstream HGL.

    Args:
        reaches: List of pipe reaches, ordered downstream to upstream.
        starting_downstream_hgl_ft: Starting HGL at downstream boundary (ft).
        name: Profile name for reporting.

    Returns:
        HydraulicProfileResult containing all reach results.

    Raises:
        InvalidHydraulicInputError: If reaches list is empty.
    """
    if not reaches:
        raise InvalidHydraulicInputError("reaches list cannot be empty")

    profile_warnings: list[HydraulicWarning] = []
    reach_results: list[PipeReachHydraulicResult] = []

    current_hgl = starting_downstream_hgl_ft

    for reach in reaches:
        result = compute_pipe_reach_hydraulics(reach, current_hgl)
        reach_results.append(result)
        current_hgl = result.upstream_hgl_ft

    ending_hgl = reach_results[-1].upstream_hgl_ft if reach_results else None

    profile_warnings.append(
        HydraulicWarning(
            code="steady_flow_assumption",
            message="Analysis assumes steady-state flow conditions",
            severity="info",
        )
    )
    profile_warnings.append(
        HydraulicWarning(
            code="full_flow_assumption",
            message="Analysis assumes full-flow (pressurized) conditions",
            severity="info",
        )
    )

    return HydraulicProfileResult(
        name=name,
        profile_type="hgl",
        reaches=reach_results,
        starting_downstream_hgl_ft=starting_downstream_hgl_ft,
        ending_upstream_hgl_ft=ending_hgl,
        warnings=profile_warnings,
        assumptions=[
            "Steady-state flow",
            "Full-flow (pressurized) conditions",
            "Uniform flow within each reach",
            "No local losses (entrance, exit, junction)",
        ],
        references=[
            "Manning's equation for friction slope",
        ],
    )
