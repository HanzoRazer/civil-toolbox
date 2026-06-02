"""Tests for hydraulic result models."""

import pytest

from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError
from civil_toolbox.hydraulics.models import (
    HydraulicWarning,
    PipeReachInput,
    PipeReachHydraulicResult,
    HydraulicProfileResult,
)


class TestHydraulicWarning:
    """Tests for HydraulicWarning."""

    def test_create_warning(self):
        """Creates a warning."""
        warning = HydraulicWarning(
            code="steady_flow_assumption",
            message="Steady flow assumed",
        )
        assert warning.code == "steady_flow_assumption"
        assert warning.message == "Steady flow assumed"
        assert warning.severity == "warning"

    def test_create_warning_with_severity(self):
        """Creates a warning with custom severity."""
        warning = HydraulicWarning(
            code="test_code",
            message="Test message",
            severity="error",
        )
        assert warning.severity == "error"

    def test_create_warning_with_entity_id(self):
        """Creates a warning with entity ID."""
        warning = HydraulicWarning(
            code="test",
            message="Test",
            entity_id="pipe_001",
        )
        assert warning.entity_id == "pipe_001"

    def test_empty_code_fails(self):
        """Empty code raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="code cannot be empty"):
            HydraulicWarning(code="", message="Test")

    def test_empty_message_fails(self):
        """Empty message raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="message cannot be empty"):
            HydraulicWarning(code="test", message="")

    def test_invalid_severity_fails(self):
        """Invalid severity raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="severity must be one of"):
            HydraulicWarning(code="test", message="Test", severity="critical")

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        warning = HydraulicWarning(
            code="test_code",
            message="Test message",
            severity="info",
            entity_id="pipe_001",
            metadata={"key": "value"},
        )
        result = warning.to_dict()

        assert result["code"] == "test_code"
        assert result["message"] == "Test message"
        assert result["severity"] == "info"
        assert result["entity_id"] == "pipe_001"
        assert result["metadata"]["key"] == "value"

    def test_round_trips(self):
        """Round-trips through dict."""
        original = HydraulicWarning(
            code="test",
            message="Test message",
            severity="warning",
            entity_id="reach_001",
            metadata={"source": "calculation"},
        )
        restored = HydraulicWarning.from_dict(original.to_dict())

        assert restored.code == original.code
        assert restored.message == original.message
        assert restored.severity == original.severity
        assert restored.entity_id == original.entity_id
        assert restored.metadata == original.metadata


class TestPipeReachInput:
    """Tests for PipeReachInput."""

    def test_create_circular_reach(self):
        """Creates a circular pipe reach."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
        )
        assert reach.id == "reach_001"
        assert reach.is_circular
        assert not reach.is_rectangular

    def test_create_rectangular_reach(self):
        """Creates a rectangular pipe reach."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=15.0,
            length_ft=150.0,
            roughness_n=0.015,
            width_in=24.0,
            height_in=18.0,
        )
        assert reach.is_rectangular
        assert not reach.is_circular

    def test_create_reach_with_elevations(self):
        """Creates a reach with elevation data."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
            upstream_invert_elevation_ft=99.0,
            downstream_invert_elevation_ft=98.0,
            upstream_rim_elevation_ft=105.0,
            downstream_rim_elevation_ft=104.5,
        )
        assert reach.upstream_invert_elevation_ft == 99.0
        assert reach.downstream_rim_elevation_ft == 104.5

    def test_zero_flow_allowed(self):
        """Zero design flow is allowed."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=0.0,
            length_ft=100.0,
            roughness_n=0.013,
            diameter_in=18.0,
        )
        assert reach.design_flow_cfs == 0.0

    def test_negative_flow_fails(self):
        """Negative design flow raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="cannot be negative"):
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=-5.0,
                length_ft=100.0,
                roughness_n=0.013,
                diameter_in=18.0,
            )

    def test_zero_length_fails(self):
        """Zero length raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be positive"):
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=0.0,
                roughness_n=0.013,
                diameter_in=18.0,
            )

    def test_empty_id_fails(self):
        """Empty ID raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="id cannot be empty"):
            PipeReachInput(
                id="",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=100.0,
                roughness_n=0.013,
                diameter_in=18.0,
            )

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
            metadata={"source": "import"},
        )
        result = reach.to_dict()

        assert result["id"] == "reach_001"
        assert result["diameter_in"] == 18.0
        assert result["metadata"]["source"] == "import"

    def test_round_trips(self):
        """Round-trips through dict."""
        original = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
            upstream_invert_elevation_ft=99.0,
            downstream_invert_elevation_ft=98.0,
        )
        restored = PipeReachInput.from_dict(original.to_dict())

        assert restored.id == original.id
        assert restored.diameter_in == original.diameter_in
        assert restored.upstream_invert_elevation_ft == original.upstream_invert_elevation_ft


class TestPipeReachHydraulicResult:
    """Tests for PipeReachHydraulicResult."""

    def test_create_result(self):
        """Creates a result."""
        result = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
        )
        assert result.reach_id == "reach_001"
        assert result.upstream_hgl_ft == 100.40

    def test_create_result_with_surcharge_status(self):
        """Creates a result with surcharge status."""
        result = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
            downstream_surcharge_status="free_surface",
            upstream_surcharge_status="surcharged_above_crown",
        )
        assert result.downstream_surcharge_status == "free_surface"
        assert result.upstream_surcharge_status == "surcharged_above_crown"

    def test_invalid_surcharge_status_fails(self):
        """Invalid surcharge status raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="must be one of"):
            PipeReachHydraulicResult(
                reach_id="reach_001",
                pipe_id="pipe_001",
                design_flow_cfs=10.0,
                flow_area_sqft=1.767,
                velocity_fps=5.66,
                velocity_head_ft=0.50,
                friction_slope_ft_per_ft=0.002,
                friction_loss_ft=0.40,
                downstream_hgl_ft=100.0,
                upstream_hgl_ft=100.40,
                downstream_egl_ft=100.50,
                upstream_egl_ft=100.90,
                downstream_surcharge_status="invalid_status",
            )

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        result = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
            warnings=[HydraulicWarning(code="test", message="Test")],
        )
        data = result.to_dict()

        assert data["reach_id"] == "reach_001"
        assert len(data["warnings"]) == 1

    def test_round_trips(self):
        """Round-trips through dict."""
        original = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
            downstream_surcharge_status="free_surface",
            upstream_surcharge_status="surcharged_above_crown",
            downstream_freeboard_ft=2.5,
            upstream_freeboard_ft=1.0,
        )
        restored = PipeReachHydraulicResult.from_dict(original.to_dict())

        assert restored.reach_id == original.reach_id
        assert restored.downstream_surcharge_status == original.downstream_surcharge_status
        assert restored.upstream_freeboard_ft == original.upstream_freeboard_ft


class TestHydraulicProfileResult:
    """Tests for HydraulicProfileResult."""

    def test_create_profile(self):
        """Creates a profile result."""
        profile = HydraulicProfileResult(
            name="Test Profile",
            starting_downstream_hgl_ft=100.0,
        )
        assert profile.name == "Test Profile"
        assert profile.starting_downstream_hgl_ft == 100.0
        assert profile.profile_type == "hgl"

    def test_default_id_generated(self):
        """Default ID is generated."""
        profile = HydraulicProfileResult()
        assert profile.id

    def test_has_warnings_false_when_empty(self):
        """has_warnings returns False when no warnings."""
        profile = HydraulicProfileResult()
        assert not profile.has_warnings()

    def test_has_warnings_true_with_profile_warnings(self):
        """has_warnings returns True with profile-level warnings."""
        profile = HydraulicProfileResult(
            warnings=[HydraulicWarning(code="test", message="Test")],
        )
        assert profile.has_warnings()

    def test_has_warnings_true_with_reach_warnings(self):
        """has_warnings returns True with reach-level warnings."""
        reach_result = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
            warnings=[HydraulicWarning(code="reach_warning", message="Reach warning")],
        )
        profile = HydraulicProfileResult(reaches=[reach_result])
        assert profile.has_warnings()

    def test_all_warnings_aggregates(self):
        """all_warnings aggregates profile and reach warnings."""
        reach_result = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
            warnings=[HydraulicWarning(code="reach_warning", message="Reach warning")],
        )
        profile = HydraulicProfileResult(
            warnings=[HydraulicWarning(code="profile_warning", message="Profile warning")],
            reaches=[reach_result],
        )
        all_warnings = profile.all_warnings()
        assert len(all_warnings) == 2

    def test_serializes_to_dict(self):
        """Serializes to dictionary."""
        profile = HydraulicProfileResult(
            id="profile_001",
            name="Test Profile",
            starting_downstream_hgl_ft=100.0,
            assumptions=["Steady flow"],
            references=["Manning's equation"],
        )
        data = profile.to_dict()

        assert data["id"] == "profile_001"
        assert data["assumptions"] == ["Steady flow"]

    def test_round_trips(self):
        """Round-trips through dict."""
        reach = PipeReachHydraulicResult(
            reach_id="reach_001",
            pipe_id="pipe_001",
            design_flow_cfs=10.0,
            flow_area_sqft=1.767,
            velocity_fps=5.66,
            velocity_head_ft=0.50,
            friction_slope_ft_per_ft=0.002,
            friction_loss_ft=0.40,
            downstream_hgl_ft=100.0,
            upstream_hgl_ft=100.40,
            downstream_egl_ft=100.50,
            upstream_egl_ft=100.90,
        )
        original = HydraulicProfileResult(
            id="profile_001",
            name="Test Profile",
            reaches=[reach],
            starting_downstream_hgl_ft=100.0,
            ending_upstream_hgl_ft=100.40,
            assumptions=["Steady flow"],
        )
        restored = HydraulicProfileResult.from_dict(original.to_dict())

        assert restored.id == original.id
        assert restored.name == original.name
        assert len(restored.reaches) == 1
        assert restored.ending_upstream_hgl_ft == original.ending_upstream_hgl_ft
