"""Tests for OpenChannel."""

import pytest

from civil_toolbox.infrastructure import OpenChannel
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestOpenChannel:
    """Tests for OpenChannel."""

    def test_rectangular_channel(self):
        """Create a rectangular channel."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="rectangular",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            length_ft=500.0,
        )
        assert channel.shape == "rectangular"
        assert channel.bottom_width_ft == 6.0
        assert channel.top_width_ft == 6.0

    def test_trapezoidal_channel(self):
        """Create a trapezoidal channel."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="trapezoidal",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            side_slope=2.0,
            length_ft=500.0,
        )
        assert channel.shape == "trapezoidal"
        assert channel.top_width_ft == 18.0  # 6 + 2*2*3

    def test_triangular_channel(self):
        """Create a triangular channel."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="triangular",
            depth_ft=2.0,
            side_slope=3.0,
            length_ft=200.0,
        )
        assert channel.shape == "triangular"
        assert channel.top_width_ft == 12.0  # 0 + 2*3*2

    def test_asymmetric_side_slopes(self):
        """Channels can have different left/right side slopes."""
        channel = OpenChannel(
            id="ch1",
            name="CH-1",
            shape="trapezoidal",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            side_slope_left=2.0,
            side_slope_right=3.0,
            length_ft=500.0,
        )
        assert channel.effective_side_slope_left == 2.0
        assert channel.effective_side_slope_right == 3.0
        assert channel.top_width_ft == 21.0  # 6 + 3*(2+3)

    def test_rectangular_requires_bottom_width(self):
        """Rectangular channel requires bottom_width_ft."""
        with pytest.raises(InvalidInfrastructureError, match="bottom_width_ft is required"):
            OpenChannel(
                id="ch", name="CH",
                shape="rectangular",
                depth_ft=3.0, length_ft=100.0,
            )

    def test_trapezoidal_requires_side_slope(self):
        """Trapezoidal channel requires side slope."""
        with pytest.raises(InvalidInfrastructureError, match="side_slope"):
            OpenChannel(
                id="ch", name="CH",
                shape="trapezoidal",
                bottom_width_ft=6.0, depth_ft=3.0, length_ft=100.0,
            )

    def test_triangular_requires_side_slope(self):
        """Triangular channel requires side slope."""
        with pytest.raises(InvalidInfrastructureError, match="side_slope"):
            OpenChannel(
                id="ch", name="CH",
                shape="triangular",
                depth_ft=2.0, length_ft=100.0,
            )

    def test_default_mannings_n(self):
        """Default Manning's n for channel is 0.035."""
        channel = OpenChannel(
            id="ch", name="CH",
            shape="rectangular",
            bottom_width_ft=6.0, depth_ft=3.0, length_ft=100.0,
        )
        assert channel.mannings_n == 0.035

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = OpenChannel(
            id="ch1",
            name="CH-1",
            description="Test channel",
            shape="trapezoidal",
            bottom_width_ft=6.0,
            depth_ft=3.0,
            side_slope=2.0,
            length_ft=500.0,
            slope_ft_per_ft=0.002,
            mannings_n=0.030,
            lining="Grass",
            freeboard_ft=0.5,
            metadata={"test": True},
        )
        restored = OpenChannel.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.shape == original.shape
        assert restored.bottom_width_ft == original.bottom_width_ft
        assert restored.side_slope == original.side_slope
        assert restored.lining == original.lining
