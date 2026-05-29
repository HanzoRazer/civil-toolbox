"""Tests for HGL and EGL calculation utilities."""

import pytest

from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError
from civil_toolbox.hydraulics.hgl import (
    GRAVITY_FTPS2,
    velocity_fps,
    velocity_head_ft,
    friction_loss_ft,
    friction_slope_from_manning,
    pipe_crown_elevation_ft,
    classify_surcharge_status,
    freeboard_ft,
)


class TestVelocityFps:
    """Tests for velocity_fps."""

    def test_velocity_calculation(self):
        """Calculates velocity from flow and area."""
        result = velocity_fps(flow_cfs=10.0, area_sqft=2.0)
        assert result == 5.0

    def test_zero_flow_returns_zero(self):
        """Zero flow returns zero velocity."""
        result = velocity_fps(flow_cfs=0.0, area_sqft=2.0)
        assert result == 0.0

    def test_small_area_high_velocity(self):
        """Small area produces high velocity."""
        result = velocity_fps(flow_cfs=10.0, area_sqft=0.5)
        assert result == 20.0

    def test_zero_area_raises(self):
        """Zero area raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            velocity_fps(flow_cfs=10.0, area_sqft=0.0)

    def test_negative_area_raises(self):
        """Negative area raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            velocity_fps(flow_cfs=10.0, area_sqft=-1.0)

    def test_zero_flow_zero_area_returns_zero(self):
        """Zero flow with zero area returns zero (short-circuits)."""
        result = velocity_fps(flow_cfs=0.0, area_sqft=0.0)
        assert result == 0.0


class TestVelocityHeadFt:
    """Tests for velocity_head_ft."""

    def test_velocity_head_known_value(self):
        """Calculates velocity head for known velocity."""
        velocity = 10.0
        expected = (10.0 ** 2) / (2 * GRAVITY_FTPS2)
        result = velocity_head_ft(velocity)
        assert abs(result - expected) < 0.0001

    def test_zero_velocity_zero_head(self):
        """Zero velocity gives zero velocity head."""
        result = velocity_head_ft(0.0)
        assert result == 0.0

    def test_velocity_head_calculation(self):
        """Velocity head follows V²/2g formula."""
        result = velocity_head_ft(8.0)
        expected = 64.0 / (2 * 32.174)
        assert abs(result - expected) < 0.0001


class TestFrictionLossFt:
    """Tests for friction_loss_ft."""

    def test_friction_loss_calculation(self):
        """Calculates friction loss from slope and length."""
        result = friction_loss_ft(friction_slope_ft_per_ft=0.002, length_ft=200.0)
        assert result == 0.4

    def test_zero_slope_zero_loss(self):
        """Zero friction slope gives zero loss."""
        result = friction_loss_ft(friction_slope_ft_per_ft=0.0, length_ft=100.0)
        assert result == 0.0

    def test_zero_length_zero_loss(self):
        """Zero length gives zero loss."""
        result = friction_loss_ft(friction_slope_ft_per_ft=0.01, length_ft=0.0)
        assert result == 0.0


class TestFrictionSlopeFromManning:
    """Tests for friction_slope_from_manning."""

    def test_friction_slope_calculation(self):
        """Calculates friction slope using Manning's equation."""
        result = friction_slope_from_manning(
            flow_cfs=10.0,
            area_sqft=1.767,
            hydraulic_radius_ft=0.375,
            mannings_n=0.013,
        )
        assert result > 0

    def test_zero_flow_zero_slope(self):
        """Zero flow gives zero friction slope."""
        result = friction_slope_from_manning(
            flow_cfs=0.0,
            area_sqft=1.767,
            hydraulic_radius_ft=0.375,
            mannings_n=0.013,
        )
        assert result == 0.0

    def test_zero_area_raises(self):
        """Zero area raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            friction_slope_from_manning(
                flow_cfs=10.0,
                area_sqft=0.0,
                hydraulic_radius_ft=0.375,
                mannings_n=0.013,
            )

    def test_negative_area_raises(self):
        """Negative area raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            friction_slope_from_manning(
                flow_cfs=10.0,
                area_sqft=-1.0,
                hydraulic_radius_ft=0.375,
                mannings_n=0.013,
            )

    def test_zero_hydraulic_radius_raises(self):
        """Zero hydraulic radius raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            friction_slope_from_manning(
                flow_cfs=10.0,
                area_sqft=1.767,
                hydraulic_radius_ft=0.0,
                mannings_n=0.013,
            )

    def test_zero_mannings_n_raises(self):
        """Zero Manning's n raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            friction_slope_from_manning(
                flow_cfs=10.0,
                area_sqft=1.767,
                hydraulic_radius_ft=0.375,
                mannings_n=0.0,
            )

    def test_higher_roughness_higher_slope(self):
        """Higher Manning's n gives higher friction slope."""
        low_n = friction_slope_from_manning(
            flow_cfs=10.0,
            area_sqft=1.767,
            hydraulic_radius_ft=0.375,
            mannings_n=0.010,
        )
        high_n = friction_slope_from_manning(
            flow_cfs=10.0,
            area_sqft=1.767,
            hydraulic_radius_ft=0.375,
            mannings_n=0.020,
        )
        assert high_n > low_n


class TestPipeCrownElevationFt:
    """Tests for pipe_crown_elevation_ft."""

    def test_circular_pipe_crown(self):
        """Calculates crown elevation for circular pipe."""
        result = pipe_crown_elevation_ft(
            invert_elevation_ft=100.0,
            diameter_in=18.0,
        )
        assert result == 101.5

    def test_box_pipe_crown(self):
        """Calculates crown elevation for box pipe."""
        result = pipe_crown_elevation_ft(
            invert_elevation_ft=100.0,
            height_in=24.0,
        )
        assert result == 102.0

    def test_diameter_takes_precedence(self):
        """Diameter takes precedence over height if both provided."""
        result = pipe_crown_elevation_ft(
            invert_elevation_ft=100.0,
            diameter_in=12.0,
            height_in=24.0,
        )
        assert result == 101.0

    def test_none_invert_returns_none(self):
        """None invert elevation returns None."""
        result = pipe_crown_elevation_ft(
            invert_elevation_ft=None,
            diameter_in=18.0,
        )
        assert result is None

    def test_no_dimensions_returns_none(self):
        """No diameter or height returns None."""
        result = pipe_crown_elevation_ft(
            invert_elevation_ft=100.0,
        )
        assert result is None


class TestClassifySurchargeStatus:
    """Tests for classify_surcharge_status."""

    def test_free_surface_below_crown(self):
        """HGL below crown is free surface."""
        result = classify_surcharge_status(
            hgl_ft=101.0,
            crown_elevation_ft=102.0,
            rim_elevation_ft=105.0,
        )
        assert result == "free_surface"

    def test_free_surface_at_crown(self):
        """HGL at crown is free surface."""
        result = classify_surcharge_status(
            hgl_ft=102.0,
            crown_elevation_ft=102.0,
            rim_elevation_ft=105.0,
        )
        assert result == "free_surface"

    def test_surcharged_above_crown(self):
        """HGL above crown but below rim is surcharged_above_crown."""
        result = classify_surcharge_status(
            hgl_ft=103.0,
            crown_elevation_ft=102.0,
            rim_elevation_ft=105.0,
        )
        assert result == "surcharged_above_crown"

    def test_surcharged_above_rim(self):
        """HGL above rim is surcharged_above_rim."""
        result = classify_surcharge_status(
            hgl_ft=106.0,
            crown_elevation_ft=102.0,
            rim_elevation_ft=105.0,
        )
        assert result == "surcharged_above_rim"

    def test_surcharged_at_rim(self):
        """HGL at rim is surcharged_above_crown (not above rim)."""
        result = classify_surcharge_status(
            hgl_ft=105.0,
            crown_elevation_ft=102.0,
            rim_elevation_ft=105.0,
        )
        assert result == "surcharged_above_crown"

    def test_unknown_when_crown_missing(self):
        """Unknown status when crown elevation is missing."""
        result = classify_surcharge_status(
            hgl_ft=103.0,
            crown_elevation_ft=None,
            rim_elevation_ft=105.0,
        )
        assert result == "unknown"

    def test_surcharged_above_crown_no_rim(self):
        """Surcharged above crown when rim is None."""
        result = classify_surcharge_status(
            hgl_ft=103.0,
            crown_elevation_ft=102.0,
            rim_elevation_ft=None,
        )
        assert result == "surcharged_above_crown"


class TestFreeboardFt:
    """Tests for freeboard_ft."""

    def test_positive_freeboard(self):
        """HGL below rim gives positive freeboard."""
        result = freeboard_ft(rim_elevation_ft=105.0, hgl_ft=103.0)
        assert result == 2.0

    def test_zero_freeboard(self):
        """HGL at rim gives zero freeboard."""
        result = freeboard_ft(rim_elevation_ft=105.0, hgl_ft=105.0)
        assert result == 0.0

    def test_negative_freeboard(self):
        """HGL above rim gives negative freeboard."""
        result = freeboard_ft(rim_elevation_ft=105.0, hgl_ft=107.0)
        assert result == -2.0

    def test_none_rim_returns_none(self):
        """None rim elevation returns None."""
        result = freeboard_ft(rim_elevation_ft=None, hgl_ft=103.0)
        assert result is None


class TestGravityConstant:
    """Tests for gravity constant."""

    def test_gravity_value(self):
        """Gravity constant is standard ft/s²."""
        assert GRAVITY_FTPS2 == 32.174
