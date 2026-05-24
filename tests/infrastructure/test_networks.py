"""Tests for InfrastructureNetwork."""

import pytest

from civil_toolbox.infrastructure import (
    InfrastructureNetwork,
    InfrastructureNode,
    Pipe,
    Inlet,
    Culvert,
    OpenChannel,
    DetentionFacility,
    OutletStructure,
    Swale,
)
from civil_toolbox.infrastructure.errors import (
    NodeNotFoundError,
    ElementNotFoundError,
)


class TestNetworkNodeOperations:
    """Tests for network node operations."""

    def test_add_and_get_node(self):
        """Add and retrieve a node."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        node = InfrastructureNode(id="n1", name="N-1")
        network.add_node(node)
        retrieved = network.get_node("n1")
        assert retrieved.id == "n1"

    def test_has_node(self):
        """Check if node exists."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        node = InfrastructureNode(id="n1", name="N-1")
        network.add_node(node)
        assert network.has_node("n1") is True
        assert network.has_node("n2") is False

    def test_get_missing_node_raises(self):
        """Getting missing node raises error."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        with pytest.raises(NodeNotFoundError, match="not found"):
            network.get_node("missing")

    def test_remove_node(self):
        """Remove and return a node."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        node = InfrastructureNode(id="n1", name="N-1")
        network.add_node(node)
        removed = network.remove_node("n1")
        assert removed.id == "n1"
        assert network.has_node("n1") is False

    def test_remove_missing_node_raises(self):
        """Removing missing node raises error."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        with pytest.raises(NodeNotFoundError, match="not found"):
            network.remove_node("missing")


class TestNetworkElementOperations:
    """Tests for network element operations."""

    def test_add_and_get_element(self):
        """Add and retrieve an element."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        pipe = Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0)
        network.add_element(pipe)
        retrieved = network.get_element("p1")
        assert retrieved.id == "p1"

    def test_has_element(self):
        """Check if element exists."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        pipe = Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0)
        network.add_element(pipe)
        assert network.has_element("p1") is True
        assert network.has_element("p2") is False

    def test_get_missing_element_raises(self):
        """Getting missing element raises error."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        with pytest.raises(ElementNotFoundError, match="not found"):
            network.get_element("missing")

    def test_remove_element(self):
        """Remove and return an element."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        pipe = Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0)
        network.add_element(pipe)
        removed = network.remove_element("p1")
        assert removed.id == "p1"
        assert network.has_element("p1") is False


class TestNetworkIterators:
    """Tests for network iteration methods."""

    def test_iter_nodes(self):
        """Iterate over nodes."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_node(InfrastructureNode(id="n2", name="N-2"))
        nodes = list(network.iter_nodes())
        assert len(nodes) == 2

    def test_iter_elements(self):
        """Iterate over all elements."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_element(Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0))
        network.add_element(Inlet(id="i1", name="I-1"))
        elements = list(network.iter_elements())
        assert len(elements) == 2

    def test_iter_pipes(self):
        """Iterate over pipes only."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_element(Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0))
        network.add_element(Inlet(id="i1", name="I-1"))
        pipes = list(network.iter_pipes())
        assert len(pipes) == 1
        assert pipes[0].id == "p1"

    def test_iter_inlets(self):
        """Iterate over inlets only."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_element(Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0))
        network.add_element(Inlet(id="i1", name="I-1"))
        inlets = list(network.iter_inlets())
        assert len(inlets) == 1
        assert inlets[0].id == "i1"


class TestNetworkValidation:
    """Tests for network validation."""

    def test_valid_network(self):
        """Valid network passes validation."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_node(InfrastructureNode(id="n2", name="N-2"))
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            upstream_node_id="n1", downstream_node_id="n2",
        ))
        result = network.validate()
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_node_reference(self):
        """Missing node reference creates error."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            upstream_node_id="n1", downstream_node_id="missing",
        ))
        result = network.validate()
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "missing" in result.errors[0]

    def test_disconnected_node_warning(self):
        """Disconnected node creates warning."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_node(InfrastructureNode(id="n2", name="N-2"))  # Not connected
        network.add_element(Inlet(id="i1", name="I-1", node_id="n1"))
        result = network.validate()
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0].warning_code == "DISCONNECTED_NODE"

    def test_len(self):
        """Network length is nodes + elements."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_node(InfrastructureNode(id="n2", name="N-2"))
        network.add_element(Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0))
        assert len(network) == 3


class TestNetworkSerialization:
    """Tests for network serialization."""

    def test_to_dict(self):
        """Serialization includes all components."""
        network = InfrastructureNetwork(
            id="net1",
            name="Test Network",
            description="Test",
            metadata={"test": True},
        )
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_element(Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0))

        data = network.to_dict()
        assert data["id"] == "net1"
        assert data["name"] == "Test Network"
        assert len(data["nodes"]) == 1
        assert len(data["elements"]) == 1

    def test_from_dict(self):
        """Deserialization restores network."""
        data = {
            "id": "net1",
            "name": "Test Network",
            "nodes": [{"id": "n1", "name": "N-1"}],
            "elements": [
                {
                    "_type": "Pipe",
                    "id": "p1",
                    "name": "P-1",
                    "diameter_in": 18.0,
                    "length_ft": 100.0,
                }
            ],
        }
        network = InfrastructureNetwork.from_dict(data)
        assert network.id == "net1"
        assert network.has_node("n1")
        assert network.has_element("p1")

    def test_roundtrip_with_multiple_element_types(self):
        """Roundtrip preserves different element types."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_element(Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0))
        network.add_element(Inlet(id="i1", name="I-1"))
        network.add_element(Culvert(id="c1", name="C-1", diameter_in=24.0, length_ft=50.0))

        restored = InfrastructureNetwork.from_dict(network.to_dict())
        assert len(list(restored.iter_pipes())) == 1
        assert len(list(restored.iter_inlets())) == 1
        assert len(list(restored.iter_culverts())) == 1
