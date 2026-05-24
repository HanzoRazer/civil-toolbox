"""Tests for swale capacity functions."""

import pytest

from civil_toolbox.infrastructure import Swale
from civil_toolbox.infrastructure_sizing import (
    estimate_swale_capacity_cfs,
    check_swale_capacity,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestEstimateSwaleCapacity:
    """Tests for estimate_swale_capacity_cfs."""

    def test_grass_swale(self):
        """Estimate capacity of grass swale."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            swale_type="grass",
            bottom_width_ft=2.0,
            depth_ft=1.0,
            side_slope=4.0,
            length_ft=300.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.035,
        )
        capacity, velocity = estimate_swale_capacity_cfs(swale)
        assert capacity > 0
        assert velocity > 0

    def test_bioswale(self):
        """Estimate capacity of bioswale."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            swale_type="bioswale",
            bottom_width_ft=3.0,
            depth_ft=1.5,
            side_slope=3.0,
            length_ft=200.0,
            slope_ft_per_ft=0.02,
            mannings_n=0.040,
        )
        capacity, velocity = estimate_swale_capacity_cfs(swale)
        assert capacity > 0
        assert velocity > 0

    def test_zero_slope_raises(self):
        """Zero slope raises error."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            depth_ft=1.0,
            length_ft=300.0,
            slope_ft_per_ft=0.0,
        )
        with pytest.raises(InvalidSizingInputError, match="zero or negative slope"):
            estimate_swale_capacity_cfs(swale)


class TestCheckSwaleCapacity:
    """Tests for check_swale_capacity."""

    def test_passes_when_below_capacity(self):
        """Check passes when design flow is below capacity."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            swale_type="grass",
            bottom_width_ft=2.0,
            depth_ft=1.0,
            side_slope=4.0,
            length_ft=300.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.035,
        )
        result = check_swale_capacity(swale, design_flow_cfs=2.0)
        assert result.passes is True
        assert result.capacity_cfs > 2.0

    def test_fails_when_above_capacity(self):
        """Check fails when design flow exceeds capacity."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            depth_ft=0.5,
            length_ft=100.0,
            slope_ft_per_ft=0.005,
        )
        result = check_swale_capacity(swale, design_flow_cfs=50.0)
        assert result.passes is False

    def test_high_velocity_warning_grass(self):
        """High velocity in grass swale generates warning."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            swale_type="grass",
            bottom_width_ft=2.0,
            depth_ft=1.5,
            side_slope=3.0,
            length_ft=300.0,
            slope_ft_per_ft=0.05,
            mannings_n=0.025,
        )
        result = check_swale_capacity(swale, design_flow_cfs=10.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "HIGH_VELOCITY" in warning_codes

    def test_infiltration_not_credited_warning(self):
        """Bioswale with infiltration rate gets informational warning."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            swale_type="bioswale",
            bottom_width_ft=3.0,
            depth_ft=1.5,
            side_slope=3.0,
            length_ft=200.0,
            slope_ft_per_ft=0.02,
            infiltration_rate_in_per_hr=1.0,
        )
        result = check_swale_capacity(swale, design_flow_cfs=5.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "INFILTRATION_NOT_CREDITED" in warning_codes

    def test_check_dams_warning(self):
        """Swale with check dams gets informational warning."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            depth_ft=1.0,
            length_ft=300.0,
            slope_ft_per_ft=0.01,
            check_dam_spacing_ft=50.0,
        )
        result = check_swale_capacity(swale, design_flow_cfs=3.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "CHECK_DAMS_NOT_MODELED" in warning_codes

    def test_result_has_assumptions(self):
        """Result includes conveyance-only assumptions."""
        swale = Swale(
            id="sw1",
            name="SW-1",
            depth_ft=1.0,
            length_ft=100.0,
            slope_ft_per_ft=0.01,
        )
        result = check_swale_capacity(swale, design_flow_cfs=2.0)
        assert len(result.assumptions) > 0
        assert any("conveyance" in a.lower() for a in result.assumptions)
