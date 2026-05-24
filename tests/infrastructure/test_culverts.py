"""Tests for Culvert."""

import pytest

from civil_toolbox.infrastructure import Culvert
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestCulvert:
    """Tests for Culvert."""

    def test_circular_culvert(self):
        """Create a circular culvert."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            shape="circular",
            diameter_in=36.0,
            length_ft=80.0,
        )
        assert culvert.shape == "circular"
        assert culvert.diameter_in == 36.0
        assert culvert.diameter_ft == 3.0

    def test_box_culvert(self):
        """Create a box culvert."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=80.0,
        )
        assert culvert.shape == "box"
        assert culvert.rise_ft == 3.0
        assert culvert.span_ft == 4.0

    def test_inlet_types(self):
        """Valid inlet types work."""
        for inlet_type in ["projecting", "mitered", "headwall", "wingwall", "beveled"]:
            culvert = Culvert(
                id="c", name="C",
                diameter_in=24.0, length_ft=50.0,
                inlet_type=inlet_type,
            )
            assert culvert.inlet_type == inlet_type

    def test_invalid_inlet_type_raises(self):
        """Invalid inlet type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="inlet_type must be one of"):
            Culvert(
                id="c", name="C",
                diameter_in=24.0, length_ft=50.0,
                inlet_type="invalid",
            )

    def test_default_mannings_n(self):
        """Default Manning's n for culvert is 0.024."""
        culvert = Culvert(id="c", name="C", diameter_in=24.0, length_ft=50.0)
        assert culvert.mannings_n == 0.024

    def test_headwater_properties(self):
        """Embankment and allowable headwater work."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=36.0,
            length_ft=80.0,
            embankment_height_ft=10.0,
            allowable_headwater_ft=8.0,
        )
        assert culvert.embankment_height_ft == 10.0
        assert culvert.allowable_headwater_ft == 8.0

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = Culvert(
            id="c1",
            name="BC-1",
            description="Test box culvert",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.012,
            material="Concrete",
            inlet_type="headwall",
            embankment_height_ft=12.0,
            metadata={"test": True},
        )
        restored = Culvert.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.shape == original.shape
        assert restored.width_in == original.width_in
        assert restored.inlet_type == original.inlet_type
        assert restored.embankment_height_ft == original.embankment_height_ft
