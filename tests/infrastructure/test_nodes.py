"""Tests for InfrastructureNode."""

import pytest

from civil_toolbox.infrastructure import InfrastructureNode
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestInfrastructureNode:
    """Tests for InfrastructureNode."""

    def test_basic_creation(self):
        """Create a basic node."""
        node = InfrastructureNode(
            id="n1",
            name="Node-1",
            node_type="junction",
        )
        assert node.id == "n1"
        assert node.name == "Node-1"
        assert node.node_type == "junction"

    def test_node_types(self):
        """All valid node types work."""
        for node_type in ["junction", "manhole", "inlet", "outfall", "storage", "divider"]:
            node = InfrastructureNode(id="n", name="N", node_type=node_type)
            assert node.node_type == node_type

    def test_invalid_node_type_raises(self):
        """Invalid node type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="node_type must be one of"):
            InfrastructureNode(id="n", name="N", node_type="invalid")

    def test_elevations(self):
        """Elevation properties work."""
        node = InfrastructureNode(
            id="n1",
            name="MH-1",
            invert_elevation_ft=95.0,
            rim_elevation_ft=100.0,
            ground_elevation_ft=100.5,
        )
        assert node.invert_elevation_ft == 95.0
        assert node.rim_elevation_ft == 100.0
        assert node.ground_elevation_ft == 100.5

    def test_depth_property(self):
        """Depth is calculated from rim and invert."""
        node = InfrastructureNode(
            id="n1",
            name="MH-1",
            invert_elevation_ft=95.0,
            rim_elevation_ft=100.0,
        )
        assert node.depth_ft == 5.0

    def test_depth_none_when_missing(self):
        """Depth is None when rim or invert missing."""
        node = InfrastructureNode(id="n", name="N", invert_elevation_ft=95.0)
        assert node.depth_ft is None

        node2 = InfrastructureNode(id="n", name="N", rim_elevation_ft=100.0)
        assert node2.depth_ft is None

    def test_coordinates(self):
        """Coordinates can be set."""
        node = InfrastructureNode(
            id="n1",
            name="N-1",
            x_coordinate=100.0,
            y_coordinate=200.0,
        )
        assert node.x_coordinate == 100.0
        assert node.y_coordinate == 200.0

    def test_to_dict(self):
        """Serialization includes all fields."""
        node = InfrastructureNode(
            id="n1",
            name="MH-1",
            description="Test manhole",
            node_type="manhole",
            invert_elevation_ft=95.0,
            rim_elevation_ft=100.0,
            metadata={"test": True},
        )
        data = node.to_dict()
        assert data["id"] == "n1"
        assert data["name"] == "MH-1"
        assert data["description"] == "Test manhole"
        assert data["node_type"] == "manhole"
        assert data["invert_elevation_ft"] == 95.0
        assert data["rim_elevation_ft"] == 100.0
        assert data["metadata"]["test"] is True

    def test_from_dict(self):
        """Deserialization restores node."""
        data = {
            "id": "n1",
            "name": "MH-1",
            "node_type": "manhole",
            "invert_elevation_ft": 95.0,
            "rim_elevation_ft": 100.0,
        }
        node = InfrastructureNode.from_dict(data)
        assert node.id == "n1"
        assert node.name == "MH-1"
        assert node.node_type == "manhole"
        assert node.invert_elevation_ft == 95.0
        assert node.rim_elevation_ft == 100.0

    def test_roundtrip_serialization(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = InfrastructureNode(
            id="n1",
            name="MH-1",
            description="Test",
            node_type="manhole",
            invert_elevation_ft=95.0,
            rim_elevation_ft=100.0,
            ground_elevation_ft=100.5,
            x_coordinate=100.0,
            y_coordinate=200.0,
            metadata={"key": "value"},
        )
        restored = InfrastructureNode.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.description == original.description
        assert restored.node_type == original.node_type
        assert restored.invert_elevation_ft == original.invert_elevation_ft
        assert restored.rim_elevation_ft == original.rim_elevation_ft
        assert restored.x_coordinate == original.x_coordinate
        assert restored.y_coordinate == original.y_coordinate
