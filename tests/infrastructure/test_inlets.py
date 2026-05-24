"""Tests for Inlet."""

import pytest

from civil_toolbox.infrastructure import Inlet
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestInlet:
    """Tests for Inlet."""

    def test_basic_creation(self):
        """Create a basic grate inlet."""
        inlet = Inlet(
            id="i1",
            name="I-1",
            inlet_type="grate",
            grate_length_in=24.0,
            grate_width_in=24.0,
        )
        assert inlet.id == "i1"
        assert inlet.inlet_type == "grate"
        assert inlet.grate_length_in == 24.0
        assert inlet.grate_width_in == 24.0

    def test_inlet_types(self):
        """All valid inlet types work."""
        for inlet_type in ["grate", "curb_opening", "combination", "slotted"]:
            inlet = Inlet(id="i", name="I", inlet_type=inlet_type)
            assert inlet.inlet_type == inlet_type

    def test_invalid_inlet_type_raises(self):
        """Invalid inlet type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be one of"):
            Inlet(id="i", name="I", inlet_type="invalid")

    def test_clogging_factor(self):
        """Clogging factor range validation."""
        inlet = Inlet(id="i", name="I", clogging_factor=0.5)
        assert inlet.clogging_factor == 0.5
        assert inlet.effective_clogging_factor == 0.5

    def test_clogging_factor_range(self):
        """Clogging factor must be 0-1."""
        with pytest.raises(InvalidInfrastructureError, match="between 0 and 1"):
            Inlet(id="i", name="I", clogging_factor=1.5)

        with pytest.raises(InvalidInfrastructureError, match="between 0 and 1"):
            Inlet(id="i", name="I", clogging_factor=-0.1)

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = Inlet(
            id="i1",
            name="I-1",
            description="Test inlet",
            inlet_type="combination",
            grate_length_in=24.0,
            grate_width_in=24.0,
            opening_length_ft=5.0,
            opening_height_in=6.0,
            clogging_factor=0.25,
            node_id="n1",
            metadata={"test": True},
        )
        restored = Inlet.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.inlet_type == original.inlet_type
        assert restored.grate_length_in == original.grate_length_in
        assert restored.clogging_factor == original.clogging_factor
