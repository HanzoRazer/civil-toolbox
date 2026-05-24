"""Tests for infrastructure example data."""

import pytest

from civil_toolbox.infrastructure import (
    create_example_node,
    create_example_pipe,
    create_example_box_culvert,
    create_example_inlet,
    create_example_channel,
    create_example_detention,
    create_example_outlet,
    create_example_swale,
    create_example_network,
    InfrastructureNode,
    Pipe,
    Culvert,
    Inlet,
    OpenChannel,
    DetentionFacility,
    OutletStructure,
    Swale,
    InfrastructureNetwork,
)


class TestExampleCreators:
    """Tests for example creation functions."""

    def test_create_example_node(self):
        """create_example_node returns valid node."""
        node = create_example_node()
        assert isinstance(node, InfrastructureNode)
        assert node.id == "node-example-1"
        assert node.metadata.get("synthetic") is True

    def test_create_example_pipe(self):
        """create_example_pipe returns valid pipe."""
        pipe = create_example_pipe()
        assert isinstance(pipe, Pipe)
        assert pipe.id == "pipe-example-1"
        assert pipe.shape == "circular"
        assert pipe.diameter_in == 18.0

    def test_create_example_box_culvert(self):
        """create_example_box_culvert returns valid culvert."""
        culvert = create_example_box_culvert()
        assert isinstance(culvert, Culvert)
        assert culvert.id == "culvert-example-1"
        assert culvert.shape == "box"
        assert culvert.width_in == 48.0
        assert culvert.height_in == 36.0

    def test_create_example_inlet(self):
        """create_example_inlet returns valid inlet."""
        inlet = create_example_inlet()
        assert isinstance(inlet, Inlet)
        assert inlet.id == "inlet-example-1"
        assert inlet.inlet_type == "grate"

    def test_create_example_channel(self):
        """create_example_channel returns valid channel."""
        channel = create_example_channel()
        assert isinstance(channel, OpenChannel)
        assert channel.id == "channel-example-1"
        assert channel.shape == "trapezoidal"

    def test_create_example_detention(self):
        """create_example_detention returns valid facility."""
        facility = create_example_detention()
        assert isinstance(facility, DetentionFacility)
        assert facility.id == "detention-example-1"
        assert len(facility.stage_storage) > 0

    def test_create_example_outlet(self):
        """create_example_outlet returns valid outlet."""
        outlet = create_example_outlet()
        assert isinstance(outlet, OutletStructure)
        assert outlet.id == "outlet-example-1"
        assert outlet.outlet_type == "combined"

    def test_create_example_swale(self):
        """create_example_swale returns valid swale."""
        swale = create_example_swale()
        assert isinstance(swale, Swale)
        assert swale.id == "swale-example-1"
        assert swale.swale_type == "grass"


class TestExampleNetwork:
    """Tests for example network."""

    def test_create_example_network(self):
        """create_example_network returns valid network."""
        network = create_example_network()
        assert isinstance(network, InfrastructureNetwork)
        assert network.id == "network-example-1"

    def test_network_has_nodes(self):
        """Example network has nodes."""
        network = create_example_network()
        nodes = list(network.iter_nodes())
        assert len(nodes) >= 3

    def test_network_has_elements(self):
        """Example network has elements."""
        network = create_example_network()
        elements = list(network.iter_elements())
        assert len(elements) >= 3

    def test_network_has_pipes(self):
        """Example network has pipes."""
        network = create_example_network()
        pipes = list(network.iter_pipes())
        assert len(pipes) >= 2

    def test_network_has_inlet(self):
        """Example network has inlet."""
        network = create_example_network()
        inlets = list(network.iter_inlets())
        assert len(inlets) >= 1

    def test_network_validates(self):
        """Example network passes validation."""
        network = create_example_network()
        result = network.validate()
        assert result.is_valid is True

    def test_network_serialization(self):
        """Example network serializes correctly."""
        network = create_example_network()
        data = network.to_dict()
        restored = InfrastructureNetwork.from_dict(data)
        assert restored.id == network.id
        assert len(list(restored.iter_nodes())) == len(list(network.iter_nodes()))
        assert len(list(restored.iter_elements())) == len(list(network.iter_elements()))
