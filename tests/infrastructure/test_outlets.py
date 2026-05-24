"""Tests for OutletStructure."""

import pytest
import math

from civil_toolbox.infrastructure import OutletStructure
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestOutletStructure:
    """Tests for OutletStructure."""

    def test_basic_orifice(self):
        """Create a basic orifice outlet."""
        outlet = OutletStructure(
            id="o1",
            name="OS-1",
            outlet_type="orifice",
            orifice_diameter_in=6.0,
        )
        assert outlet.outlet_type == "orifice"
        assert outlet.orifice_diameter_in == 6.0

    def test_outlet_types(self):
        """All valid outlet types work."""
        for otype in ["orifice", "weir", "riser", "culvert", "combined"]:
            outlet = OutletStructure(id="o", name="O", outlet_type=otype)
            assert outlet.outlet_type == otype

    def test_invalid_outlet_type_raises(self):
        """Invalid outlet type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="must be one of"):
            OutletStructure(id="o", name="O", outlet_type="invalid")

    def test_orifice_area_calculation(self):
        """Orifice area is calculated correctly."""
        outlet = OutletStructure(
            id="o1",
            name="OS-1",
            orifice_diameter_in=12.0,  # 1 ft diameter
        )
        expected_area = math.pi * 0.5**2  # pi * r^2
        assert abs(outlet.orifice_area_sqft - expected_area) < 0.001

    def test_orifice_coefficient_validation(self):
        """Orifice coefficient must be 0-1."""
        with pytest.raises(InvalidInfrastructureError, match="between 0 and 1"):
            OutletStructure(id="o", name="O", orifice_coefficient=1.5)

        with pytest.raises(InvalidInfrastructureError, match="between 0 and 1"):
            OutletStructure(id="o", name="O", orifice_coefficient=0.0)

    def test_weir_properties(self):
        """Weir properties work."""
        outlet = OutletStructure(
            id="o1",
            name="OS-1",
            outlet_type="weir",
            weir_length_ft=10.0,
            weir_coefficient=3.33,
            weir_crest_elevation_ft=95.0,
        )
        assert outlet.weir_length_ft == 10.0
        assert outlet.weir_coefficient == 3.33
        assert outlet.weir_crest_elevation_ft == 95.0

    def test_riser_properties(self):
        """Riser properties work."""
        outlet = OutletStructure(
            id="o1",
            name="OS-1",
            outlet_type="riser",
            riser_diameter_in=48.0,
            riser_height_ft=6.0,
        )
        assert outlet.riser_diameter_in == 48.0
        assert outlet.riser_height_ft == 6.0

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = OutletStructure(
            id="o1",
            name="OS-1",
            description="Test outlet",
            outlet_type="combined",
            invert_elevation_ft=90.0,
            orifice_diameter_in=6.0,
            orifice_coefficient=0.6,
            weir_length_ft=5.0,
            weir_crest_elevation_ft=94.0,
            metadata={"test": True},
        )
        restored = OutletStructure.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.outlet_type == original.outlet_type
        assert restored.orifice_diameter_in == original.orifice_diameter_in
        assert restored.weir_length_ft == original.weir_length_ft
