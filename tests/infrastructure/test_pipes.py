"""Tests for Pipe."""

import pytest

from civil_toolbox.infrastructure import Pipe
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestPipeCircular:
    """Tests for circular pipes."""

    def test_basic_creation(self):
        """Create a basic circular pipe."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            shape="circular",
            diameter_in=18.0,
            length_ft=200.0,
            slope_ft_per_ft=0.005,
        )
        assert pipe.id == "p1"
        assert pipe.name == "P-1"
        assert pipe.shape == "circular"
        assert pipe.diameter_in == 18.0
        assert pipe.length_ft == 200.0
        assert pipe.slope_ft_per_ft == 0.005

    def test_diameter_required_for_circular(self):
        """Circular pipe requires diameter_in."""
        with pytest.raises(InvalidInfrastructureError, match="diameter_in is required"):
            Pipe(id="p1", name="P-1", shape="circular", length_ft=100.0)

    def test_diameter_ft_property(self):
        """diameter_ft converts from inches."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            diameter_in=24.0,
            length_ft=100.0,
        )
        assert pipe.diameter_ft == 2.0

    def test_default_mannings_n(self):
        """Default Manning's n is 0.013."""
        pipe = Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0)
        assert pipe.mannings_n == 0.013


class TestPipeBox:
    """Tests for box pipes."""

    def test_box_pipe_creation(self):
        """Create a box pipe with width and height."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=100.0,
        )
        assert pipe.shape == "box"
        assert pipe.width_in == 48.0
        assert pipe.height_in == 36.0

    def test_box_requires_width_and_height(self):
        """Box pipe requires both width_in and height_in."""
        with pytest.raises(InvalidInfrastructureError, match="width_in and height_in"):
            Pipe(id="p1", name="P-1", shape="box", width_in=48.0, length_ft=100.0)

        with pytest.raises(InvalidInfrastructureError, match="width_in and height_in"):
            Pipe(id="p1", name="P-1", shape="box", height_in=36.0, length_ft=100.0)

    def test_width_ft_height_ft_properties(self):
        """width_ft and height_ft convert from inches."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=100.0,
        )
        assert pipe.width_ft == 4.0
        assert pipe.height_ft == 3.0


class TestPipeValidation:
    """Tests for pipe validation."""

    def test_length_must_be_positive(self):
        """length_ft must be positive."""
        with pytest.raises(InvalidInfrastructureError, match="length_ft must be positive"):
            Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=0.0)

    def test_diameter_must_be_positive(self):
        """diameter_in must be positive."""
        with pytest.raises(InvalidInfrastructureError, match="diameter_in must be positive"):
            Pipe(id="p1", name="P-1", diameter_in=-18.0, length_ft=100.0)

    def test_slope_cannot_be_negative(self):
        """slope_ft_per_ft cannot be negative."""
        with pytest.raises(InvalidInfrastructureError, match="cannot be negative"):
            Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0, slope_ft_per_ft=-0.01)

    def test_mannings_n_validation(self):
        """mannings_n must be in valid range."""
        with pytest.raises(InvalidInfrastructureError, match="between 0 and 0.5"):
            Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0, mannings_n=0.0)


class TestPipeSerialization:
    """Tests for pipe serialization."""

    def test_to_dict(self):
        """Serialization includes all fields."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            description="Test pipe",
            diameter_in=18.0,
            length_ft=200.0,
            slope_ft_per_ft=0.005,
            mannings_n=0.013,
            material="RCP",
            upstream_node_id="n1",
            downstream_node_id="n2",
        )
        data = pipe.to_dict()
        assert data["id"] == "p1"
        assert data["shape"] == "circular"
        assert data["diameter_in"] == 18.0
        assert data["length_ft"] == 200.0
        assert data["material"] == "RCP"
        assert data["upstream_node_id"] == "n1"

    def test_from_dict(self):
        """Deserialization restores pipe."""
        data = {
            "id": "p1",
            "name": "P-1",
            "shape": "circular",
            "diameter_in": 18.0,
            "length_ft": 200.0,
            "slope_ft_per_ft": 0.005,
        }
        pipe = Pipe.from_dict(data)
        assert pipe.id == "p1"
        assert pipe.diameter_in == 18.0
        assert pipe.length_ft == 200.0

    def test_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = Pipe(
            id="p1",
            name="P-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=100.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.012,
            material="Concrete",
            metadata={"test": True},
        )
        restored = Pipe.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.shape == original.shape
        assert restored.width_in == original.width_in
        assert restored.height_in == original.height_in
