"""Tests for Swale."""

import pytest

from civil_toolbox.infrastructure import Swale
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestSwale:
    """Tests for Swale."""

    def test_basic_creation(self):
        """Create a basic grass swale."""
        swale = Swale(
            id="s1",
            name="SW-1",
            swale_type="grass",
            bottom_width_ft=2.0,
            depth_ft=1.0,
            side_slope=3.0,
            length_ft=300.0,
        )
        assert swale.swale_type == "grass"
        assert swale.bottom_width_ft == 2.0
        assert swale.depth_ft == 1.0
        assert swale.side_slope == 3.0

    def test_swale_types(self):
        """All valid swale types work."""
        for stype in ["grass", "bioswale", "rock", "concrete"]:
            swale = Swale(
                id="s", name="S",
                swale_type=stype,
                depth_ft=1.0, length_ft=100.0,
            )
            assert swale.swale_type == stype

    def test_invalid_swale_type_raises(self):
        """Invalid swale type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="swale_type must be one of"):
            Swale(
                id="s", name="S",
                swale_type="invalid",
                depth_ft=1.0, length_ft=100.0,
            )

    def test_top_width_calculation(self):
        """Top width is calculated correctly."""
        swale = Swale(
            id="s1",
            name="SW-1",
            bottom_width_ft=2.0,
            depth_ft=1.0,
            side_slope=3.0,
            length_ft=100.0,
        )
        assert swale.top_width_ft == 8.0  # 2 + 2*3*1

    def test_cross_sectional_area(self):
        """Cross-sectional area is calculated correctly."""
        swale = Swale(
            id="s1",
            name="SW-1",
            bottom_width_ft=2.0,
            depth_ft=1.0,
            side_slope=3.0,
            length_ft=100.0,
        )
        expected = (2.0 + 8.0) / 2.0 * 1.0  # (bottom + top) / 2 * depth
        assert swale.cross_sectional_area_sqft == expected

    def test_default_mannings_n(self):
        """Default Manning's n for swale is 0.035."""
        swale = Swale(id="s", name="S", depth_ft=1.0, length_ft=100.0)
        assert swale.mannings_n == 0.035

    def test_bioswale_properties(self):
        """Bioswale can have infiltration rate."""
        swale = Swale(
            id="s1",
            name="SW-1",
            swale_type="bioswale",
            bottom_width_ft=3.0,
            depth_ft=1.5,
            side_slope=4.0,
            length_ft=200.0,
            infiltration_rate_in_per_hr=1.0,
        )
        assert swale.infiltration_rate_in_per_hr == 1.0

    def test_check_dams(self):
        """Check dam spacing can be specified."""
        swale = Swale(
            id="s1",
            name="SW-1",
            depth_ft=1.0,
            length_ft=300.0,
            check_dam_spacing_ft=50.0,
        )
        assert swale.check_dam_spacing_ft == 50.0

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = Swale(
            id="s1",
            name="SW-1",
            description="Test swale",
            swale_type="bioswale",
            bottom_width_ft=3.0,
            depth_ft=1.5,
            side_slope=4.0,
            length_ft=200.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.040,
            vegetation_type="Native grasses",
            check_dam_spacing_ft=50.0,
            infiltration_rate_in_per_hr=1.0,
            metadata={"test": True},
        )
        restored = Swale.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.swale_type == original.swale_type
        assert restored.bottom_width_ft == original.bottom_width_ft
        assert restored.infiltration_rate_in_per_hr == original.infiltration_rate_in_per_hr
        assert restored.check_dam_spacing_ft == original.check_dam_spacing_ft
