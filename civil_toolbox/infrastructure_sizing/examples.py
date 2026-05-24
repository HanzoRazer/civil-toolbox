"""Example infrastructure sizing checks for testing and documentation."""

from __future__ import annotations

from civil_toolbox.infrastructure import (
    Pipe,
    Culvert,
    OpenChannel,
    Swale,
    DetentionFacility,
    StageStoragePoint,
)
from civil_toolbox.infrastructure_sizing.models import InfrastructureCheckResult
from civil_toolbox.infrastructure_sizing.pipes import check_pipe_capacity
from civil_toolbox.infrastructure_sizing.culverts import check_culvert_capacity
from civil_toolbox.infrastructure_sizing.channels import check_open_channel_capacity
from civil_toolbox.infrastructure_sizing.swales import check_swale_capacity
from civil_toolbox.infrastructure_sizing.detention import check_detention_storage


def create_example_pipe_check() -> InfrastructureCheckResult:
    """Create an example pipe capacity check result.

    Returns:
        InfrastructureCheckResult for an 18" RCP pipe.
    """
    pipe = Pipe(
        id="example-pipe",
        name="P-1",
        description="Example 18-inch RCP",
        shape="circular",
        diameter_in=18.0,
        length_ft=200.0,
        slope_ft_per_ft=0.005,
        mannings_n=0.013,
        material="RCP",
    )
    return check_pipe_capacity(pipe, design_flow_cfs=10.0)


def create_example_culvert_check() -> InfrastructureCheckResult:
    """Create an example culvert capacity check result.

    Returns:
        InfrastructureCheckResult for a 4'x3' box culvert.
    """
    culvert = Culvert(
        id="example-culvert",
        name="BC-1",
        description="Example 4x3 box culvert",
        shape="box",
        width_in=48.0,
        height_in=36.0,
        length_ft=80.0,
        slope_ft_per_ft=0.01,
        mannings_n=0.012,
        material="Concrete",
        inlet_type="headwall",
    )
    return check_culvert_capacity(culvert, design_flow_cfs=100.0)


def create_example_channel_check() -> InfrastructureCheckResult:
    """Create an example channel capacity check result.

    Returns:
        InfrastructureCheckResult for a trapezoidal channel.
    """
    channel = OpenChannel(
        id="example-channel",
        name="CH-1",
        description="Example trapezoidal channel",
        shape="trapezoidal",
        bottom_width_ft=6.0,
        depth_ft=3.0,
        side_slope=2.0,
        length_ft=500.0,
        slope_ft_per_ft=0.002,
        mannings_n=0.030,
        lining="Grass",
    )
    return check_open_channel_capacity(channel, design_flow_cfs=50.0)


def create_example_swale_check() -> InfrastructureCheckResult:
    """Create an example swale capacity check result.

    Returns:
        InfrastructureCheckResult for a grass swale.
    """
    swale = Swale(
        id="example-swale",
        name="SW-1",
        description="Example grass swale",
        swale_type="grass",
        bottom_width_ft=2.0,
        depth_ft=1.0,
        side_slope=4.0,
        length_ft=300.0,
        slope_ft_per_ft=0.01,
        mannings_n=0.035,
        vegetation_type="Bermuda grass",
    )
    return check_swale_capacity(swale, design_flow_cfs=5.0)


def create_example_detention_check() -> InfrastructureCheckResult:
    """Create an example detention storage check result.

    Returns:
        InfrastructureCheckResult for a detention pond.
    """
    facility = DetentionFacility(
        id="example-detention",
        name="DP-1",
        description="Example detention pond",
        facility_type="detention",
        pond_bottom_elevation_ft=90.0,
        pond_bottom_area_sqft=10000.0,
        side_slope=3.0,
        maximum_depth_ft=6.0,
        stage_storage=[
            StageStoragePoint(stage_ft=90.0, storage_cuft=0),
            StageStoragePoint(stage_ft=92.0, storage_cuft=25000),
            StageStoragePoint(stage_ft=94.0, storage_cuft=60000),
            StageStoragePoint(stage_ft=96.0, storage_cuft=110000),
        ],
        spillway_elevation_ft=95.5,
        spillway_width_ft=10.0,
    )
    return check_detention_storage(facility, required_storage_cuft=80000.0)
