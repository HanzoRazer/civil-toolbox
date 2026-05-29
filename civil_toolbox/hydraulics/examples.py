"""Synthetic HGL examples for testing and demonstration."""

from __future__ import annotations

from civil_toolbox.hydraulics.models import PipeReachInput


def create_simple_trunk_reaches() -> list[PipeReachInput]:
    """Create a simple 3-reach storm trunk system.

    Returns reaches ordered downstream to upstream:
    - Reach 1: Outlet reach, 18" diameter
    - Reach 2: Middle reach, 18" diameter
    - Reach 3: Upstream reach, 15" diameter

    All reaches assume 10 cfs design flow.
    """
    return [
        PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Outlet Reach",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
            upstream_invert_elevation_ft=99.0,
            downstream_invert_elevation_ft=98.0,
            upstream_rim_elevation_ft=105.0,
            downstream_rim_elevation_ft=104.0,
        ),
        PipeReachInput(
            id="reach_002",
            pipe_id="pipe_002",
            name="Middle Reach",
            design_flow_cfs=10.0,
            length_ft=250.0,
            roughness_n=0.013,
            diameter_in=18.0,
            upstream_invert_elevation_ft=100.0,
            downstream_invert_elevation_ft=99.0,
            upstream_rim_elevation_ft=106.0,
            downstream_rim_elevation_ft=105.0,
        ),
        PipeReachInput(
            id="reach_003",
            pipe_id="pipe_003",
            name="Upstream Reach",
            design_flow_cfs=10.0,
            length_ft=150.0,
            roughness_n=0.013,
            diameter_in=15.0,
            upstream_invert_elevation_ft=101.5,
            downstream_invert_elevation_ft=100.0,
            upstream_rim_elevation_ft=107.0,
            downstream_rim_elevation_ft=106.0,
        ),
    ]


def create_surcharged_system_reaches() -> list[PipeReachInput]:
    """Create a system that will surcharge under design flow.

    Uses undersized pipes relative to design flow to demonstrate
    surcharge detection. Starting HGL at 100 ft with low rims
    will cause surcharged conditions.
    """
    return [
        PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Undersized Outlet",
            design_flow_cfs=25.0,
            length_ft=300.0,
            roughness_n=0.013,
            diameter_in=12.0,
            upstream_invert_elevation_ft=99.0,
            downstream_invert_elevation_ft=98.0,
            upstream_rim_elevation_ft=101.0,
            downstream_rim_elevation_ft=100.0,
        ),
        PipeReachInput(
            id="reach_002",
            pipe_id="pipe_002",
            name="Undersized Middle",
            design_flow_cfs=25.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=12.0,
            upstream_invert_elevation_ft=100.0,
            downstream_invert_elevation_ft=99.0,
            upstream_rim_elevation_ft=102.0,
            downstream_rim_elevation_ft=101.0,
        ),
    ]


def create_mixed_geometry_reaches() -> list[PipeReachInput]:
    """Create a system with mixed circular and box sections.

    Demonstrates transition from circular pipe to box culvert.
    """
    return [
        PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Box Culvert",
            design_flow_cfs=50.0,
            length_ft=100.0,
            roughness_n=0.015,
            width_in=48.0,
            height_in=36.0,
            upstream_invert_elevation_ft=97.0,
            downstream_invert_elevation_ft=96.5,
            upstream_rim_elevation_ft=104.0,
            downstream_rim_elevation_ft=103.5,
        ),
        PipeReachInput(
            id="reach_002",
            pipe_id="pipe_002",
            name="Transition Reach",
            design_flow_cfs=50.0,
            length_ft=50.0,
            roughness_n=0.013,
            diameter_in=36.0,
            upstream_invert_elevation_ft=97.5,
            downstream_invert_elevation_ft=97.0,
            upstream_rim_elevation_ft=104.5,
            downstream_rim_elevation_ft=104.0,
        ),
        PipeReachInput(
            id="reach_003",
            pipe_id="pipe_003",
            name="Upstream Circular",
            design_flow_cfs=50.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=36.0,
            upstream_invert_elevation_ft=98.5,
            downstream_invert_elevation_ft=97.5,
            upstream_rim_elevation_ft=106.0,
            downstream_rim_elevation_ft=104.5,
        ),
    ]


def create_minimal_reach() -> PipeReachInput:
    """Create a minimal single reach for unit testing.

    Has only required fields, no elevations.
    """
    return PipeReachInput(
        id="reach_min",
        pipe_id="pipe_min",
        name="Minimal Reach",
        design_flow_cfs=5.0,
        length_ft=100.0,
        roughness_n=0.013,
        diameter_in=12.0,
    )
