"""Tests for open channel capacity functions."""

import pytest

from civil_toolbox.infrastructure import OpenChannel
from civil_toolbox.infrastructure_sizing import (
    estimate_open_channel_capacity_cfs,
    check_open_channel_capacity,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestEstimateChannelCapacity:
    """Tests for estimate_open_channel_capacity_cfs."""

    def test_rectangular_channel(self):
        """Estimate capacity of rectangular channel."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="rectangular",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            length_ft=500.0,
            slope_ft_per_ft=0.002,
            mannings_n=0.030,
        )
        capacity, velocity = estimate_open_channel_capacity_cfs(channel)
        assert capacity > 0
        assert velocity > 0

    def test_trapezoidal_channel(self):
        """Estimate capacity of trapezoidal channel."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="trapezoidal",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            side_slope=2.0,
            length_ft=500.0,
            slope_ft_per_ft=0.002,
            mannings_n=0.030,
        )
        capacity, velocity = estimate_open_channel_capacity_cfs(channel)
        assert capacity > 0
        assert velocity > 0

    def test_triangular_channel(self):
        """Estimate capacity of triangular channel."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="triangular",
            depth_ft=2.0,
            side_slope=3.0,
            length_ft=200.0,
            slope_ft_per_ft=0.005,
            mannings_n=0.035,
        )
        capacity, velocity = estimate_open_channel_capacity_cfs(channel)
        assert capacity > 0
        assert velocity > 0

    def test_parabolic_not_implemented(self):
        """Parabolic shape raises not implemented error."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="parabolic",
            depth_ft=2.0,
            length_ft=200.0,
            slope_ft_per_ft=0.005,
        )
        with pytest.raises(InvalidSizingInputError, match="not yet implemented"):
            estimate_open_channel_capacity_cfs(channel)

    def test_zero_slope_raises(self):
        """Zero slope raises error."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="rectangular",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            length_ft=500.0,
            slope_ft_per_ft=0.0,
        )
        with pytest.raises(InvalidSizingInputError, match="zero or negative slope"):
            estimate_open_channel_capacity_cfs(channel)


class TestCheckChannelCapacity:
    """Tests for check_open_channel_capacity."""

    def test_passes_when_below_capacity(self):
        """Check passes when design flow is below capacity."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="trapezoidal",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            side_slope=2.0,
            length_ft=500.0,
            slope_ft_per_ft=0.002,
            mannings_n=0.030,
        )
        result = check_open_channel_capacity(channel, design_flow_cfs=20.0)
        assert result.passes is True
        assert result.capacity_cfs > 20.0

    def test_fails_when_above_capacity(self):
        """Check fails when design flow exceeds capacity."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="rectangular",
            bottom_width_ft=4.0,
            depth_ft=2.0,
            length_ft=500.0,
            slope_ft_per_ft=0.001,
            mannings_n=0.035,
        )
        result = check_open_channel_capacity(channel, design_flow_cfs=500.0)
        assert result.passes is False

    def test_grass_velocity_warning(self):
        """High velocity in grass-lined channel generates warning."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="trapezoidal",
            bottom_width_ft=4.0,
            depth_ft=2.0,
            side_slope=2.0,
            length_ft=500.0,
            slope_ft_per_ft=0.05,
            mannings_n=0.030,
            lining="Grass",
        )
        result = check_open_channel_capacity(channel, design_flow_cfs=50.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "HIGH_VELOCITY_GRASS" in warning_codes

    def test_freeboard_warning(self):
        """Channel with freeboard gets informational warning."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="rectangular",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            length_ft=500.0,
            slope_ft_per_ft=0.002,
            freeboard_ft=0.5,
        )
        result = check_open_channel_capacity(channel, design_flow_cfs=10.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "FREEBOARD_NOT_CHECKED" in warning_codes

    def test_result_has_assumptions(self):
        """Result includes uniform flow assumptions."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="rectangular",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            length_ft=500.0,
            slope_ft_per_ft=0.002,
        )
        result = check_open_channel_capacity(channel, design_flow_cfs=10.0)
        assert len(result.assumptions) > 0
        assert any("uniform" in a.lower() for a in result.assumptions)
