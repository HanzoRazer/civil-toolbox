"""Example infrastructure data for testing and documentation."""

from __future__ import annotations

from civil_toolbox.infrastructure.nodes import InfrastructureNode
from civil_toolbox.infrastructure.pipes import Pipe
from civil_toolbox.infrastructure.inlets import Inlet
from civil_toolbox.infrastructure.culverts import Culvert
from civil_toolbox.infrastructure.channels import OpenChannel
from civil_toolbox.infrastructure.detention import (
    DetentionFacility,
    StageStoragePoint,
)
from civil_toolbox.infrastructure.outlets import OutletStructure
from civil_toolbox.infrastructure.swales import Swale
from civil_toolbox.infrastructure.networks import InfrastructureNetwork


def create_example_node() -> InfrastructureNode:
    """Create an example junction node."""
    return InfrastructureNode(
        id="node-example-1",
        name="MH-1",
        description="Example manhole",
        node_type="manhole",
        invert_elevation_ft=95.0,
        rim_elevation_ft=100.0,
        metadata={"synthetic": True},
    )


def create_example_pipe() -> Pipe:
    """Create an example circular pipe."""
    return Pipe(
        id="pipe-example-1",
        name="P-1",
        description="Example 18-inch RCP",
        shape="circular",
        diameter_in=18.0,
        length_ft=200.0,
        slope_ft_per_ft=0.005,
        mannings_n=0.013,
        material="RCP",
        upstream_node_id="node-example-1",
        downstream_node_id="node-example-2",
        metadata={"synthetic": True},
    )


def create_example_box_culvert() -> Culvert:
    """Create an example box culvert."""
    return Culvert(
        id="culvert-example-1",
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
        metadata={"synthetic": True},
    )


def create_example_inlet() -> Inlet:
    """Create an example grate inlet."""
    return Inlet(
        id="inlet-example-1",
        name="I-1",
        description="Example grate inlet",
        inlet_type="grate",
        grate_length_in=24.0,
        grate_width_in=24.0,
        clogging_factor=0.5,
        metadata={"synthetic": True},
    )


def create_example_channel() -> OpenChannel:
    """Create an example trapezoidal channel."""
    return OpenChannel(
        id="channel-example-1",
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
        metadata={"synthetic": True},
    )


def create_example_detention() -> DetentionFacility:
    """Create an example detention pond with stage-storage."""
    return DetentionFacility(
        id="detention-example-1",
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
        metadata={"synthetic": True},
    )


def create_example_outlet() -> OutletStructure:
    """Create an example combined outlet structure."""
    return OutletStructure(
        id="outlet-example-1",
        name="OS-1",
        description="Example outlet with orifice and weir",
        outlet_type="combined",
        invert_elevation_ft=90.0,
        orifice_diameter_in=6.0,
        orifice_coefficient=0.6,
        weir_length_ft=5.0,
        weir_coefficient=3.33,
        weir_crest_elevation_ft=94.0,
        metadata={"synthetic": True},
    )


def create_example_swale() -> Swale:
    """Create an example grass swale."""
    return Swale(
        id="swale-example-1",
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
        metadata={"synthetic": True},
    )


def create_example_network() -> InfrastructureNetwork:
    """Create an example network with multiple connected elements."""
    network = InfrastructureNetwork(
        id="network-example-1",
        name="Example Drainage Network",
        description="A synthetic network for testing and documentation",
        metadata={"synthetic": True},
    )

    node1 = InfrastructureNode(
        id="MH1",
        name="MH-1",
        node_type="manhole",
        invert_elevation_ft=95.0,
        rim_elevation_ft=100.0,
    )
    node2 = InfrastructureNode(
        id="MH2",
        name="MH-2",
        node_type="manhole",
        invert_elevation_ft=94.0,
        rim_elevation_ft=99.5,
    )
    node3 = InfrastructureNode(
        id="OUT1",
        name="Outfall-1",
        node_type="outfall",
        invert_elevation_ft=92.0,
    )

    network.add_node(node1)
    network.add_node(node2)
    network.add_node(node3)

    pipe1 = Pipe(
        id="P1",
        name="P-1",
        shape="circular",
        diameter_in=18.0,
        length_ft=200.0,
        slope_ft_per_ft=0.005,
        mannings_n=0.013,
        material="RCP",
        upstream_node_id="MH1",
        downstream_node_id="MH2",
    )
    pipe2 = Pipe(
        id="P2",
        name="P-2",
        shape="circular",
        diameter_in=24.0,
        length_ft=150.0,
        slope_ft_per_ft=0.013,
        mannings_n=0.013,
        material="RCP",
        upstream_node_id="MH2",
        downstream_node_id="OUT1",
    )

    network.add_element(pipe1)
    network.add_element(pipe2)

    inlet1 = Inlet(
        id="I1",
        name="I-1",
        inlet_type="grate",
        grate_length_in=24.0,
        grate_width_in=24.0,
        node_id="MH1",
    )
    network.add_element(inlet1)

    return network
