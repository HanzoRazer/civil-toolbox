"""Tests for pipe reach and profile hydraulic calculations."""

import pytest

from civil_toolbox.hydraulics.errors import (
    InvalidHydraulicInputError,
    MissingHydraulicDataError,
)
from civil_toolbox.hydraulics.models import PipeReachInput
from civil_toolbox.hydraulics.compute import (
    compute_pipe_reach_hydraulics,
    compute_hgl_profile,
)


class TestComputePipeReachHydraulics:
    """Tests for compute_pipe_reach_hydraulics."""

    def test_circular_pipe_basic(self):
        """Computes hydraulics for circular pipe."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.reach_id == "reach_001"
        assert result.design_flow_cfs == 10.0
        assert result.flow_area_sqft > 0
        assert result.velocity_fps > 0
        assert result.velocity_head_ft > 0
        assert result.friction_slope_ft_per_ft > 0
        assert result.friction_loss_ft > 0
        assert result.downstream_hgl_ft == 100.0
        assert result.upstream_hgl_ft > 100.0

    def test_box_pipe_basic(self):
        """Computes hydraulics for box pipe."""
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
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.reach_id == "reach_001"
        assert result.flow_area_sqft == pytest.approx(3.0, rel=0.01)
        assert result.upstream_hgl_ft > result.downstream_hgl_ft

    def test_zero_flow_zero_losses(self):
        """Zero flow produces zero friction loss."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=0.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.velocity_fps == 0.0
        assert result.velocity_head_ft == 0.0
        assert result.friction_loss_ft == 0.0
        assert result.upstream_hgl_ft == 100.0

    def test_hgl_propagates_upstream(self):
        """HGL increases from downstream to upstream."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.upstream_hgl_ft == pytest.approx(
            result.downstream_hgl_ft + result.friction_loss_ft
        )

    def test_egl_includes_velocity_head(self):
        """EGL equals HGL plus velocity head."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.downstream_egl_ft == pytest.approx(
            result.downstream_hgl_ft + result.velocity_head_ft
        )
        assert result.upstream_egl_ft == pytest.approx(
            result.upstream_hgl_ft + result.velocity_head_ft
        )

    def test_crown_elevations_computed(self):
        """Crown elevations computed from inverts."""
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
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.downstream_crown_elevation_ft == pytest.approx(99.5)
        assert result.upstream_crown_elevation_ft == pytest.approx(100.5)

    def test_surcharge_status_classified(self):
        """Surcharge status classified at both ends."""
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
            downstream_rim_elevation_ft=104.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.downstream_surcharge_status in [
            "free_surface",
            "surcharged_above_crown",
            "surcharged_above_rim",
            "unknown",
        ]
        assert result.upstream_surcharge_status in [
            "free_surface",
            "surcharged_above_crown",
            "surcharged_above_rim",
            "unknown",
        ]

    def test_freeboard_computed(self):
        """Freeboard computed when rim elevation available."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
            diameter_in=18.0,
            upstream_rim_elevation_ft=105.0,
            downstream_rim_elevation_ft=104.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

        assert result.downstream_freeboard_ft == pytest.approx(4.0)
        assert result.upstream_freeboard_ft is not None

    def test_missing_geometry_raises(self):
        """Missing geometry raises error."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=10.0,
            length_ft=200.0,
            roughness_n=0.013,
        )
        with pytest.raises(MissingHydraulicDataError, match="no valid geometry"):
            compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=100.0)

    def test_surcharge_warning_generated(self):
        """Warning generated when HGL exceeds rim."""
        reach = PipeReachInput(
            id="reach_001",
            pipe_id="pipe_001",
            name="Reach 1",
            design_flow_cfs=50.0,
            length_ft=500.0,
            roughness_n=0.013,
            diameter_in=12.0,
            upstream_invert_elevation_ft=99.0,
            downstream_invert_elevation_ft=98.0,
            upstream_rim_elevation_ft=101.0,
            downstream_rim_elevation_ft=100.0,
        )
        result = compute_pipe_reach_hydraulics(reach, downstream_hgl_ft=101.0)

        surcharge_warnings = [w for w in result.warnings if w.code == "surcharge_above_rim"]
        assert len(surcharge_warnings) > 0


class TestComputeHglProfile:
    """Tests for compute_hgl_profile."""

    def test_single_reach_profile(self):
        """Computes profile for single reach."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        assert profile.name == "Hydraulic Grade Line Profile"
        assert profile.profile_type == "hgl"
        assert len(profile.reaches) == 1
        assert profile.starting_downstream_hgl_ft == 100.0
        assert profile.ending_upstream_hgl_ft > 100.0

    def test_multiple_reaches_propagate(self):
        """HGL propagates through multiple reaches."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
            PipeReachInput(
                id="reach_002",
                pipe_id="pipe_002",
                name="Reach 2",
                design_flow_cfs=10.0,
                length_ft=150.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
            PipeReachInput(
                id="reach_003",
                pipe_id="pipe_003",
                name="Reach 3",
                design_flow_cfs=10.0,
                length_ft=100.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        assert len(profile.reaches) == 3
        assert profile.reaches[0].downstream_hgl_ft == 100.0
        assert profile.reaches[1].downstream_hgl_ft == profile.reaches[0].upstream_hgl_ft
        assert profile.reaches[2].downstream_hgl_ft == profile.reaches[1].upstream_hgl_ft
        assert profile.ending_upstream_hgl_ft == profile.reaches[2].upstream_hgl_ft

    def test_hgl_monotonically_increases(self):
        """HGL increases monotonically upstream."""
        reaches = [
            PipeReachInput(
                id=f"reach_{i:03d}",
                pipe_id=f"pipe_{i:03d}",
                name=f"Reach {i}",
                design_flow_cfs=10.0,
                length_ft=100.0,
                roughness_n=0.013,
                diameter_in=18.0,
            )
            for i in range(1, 6)
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        previous_hgl = 100.0
        for r in profile.reaches:
            assert r.downstream_hgl_ft >= previous_hgl
            assert r.upstream_hgl_ft >= r.downstream_hgl_ft
            previous_hgl = r.upstream_hgl_ft

    def test_empty_reaches_raises(self):
        """Empty reaches list raises error."""
        with pytest.raises(InvalidHydraulicInputError, match="cannot be empty"):
            compute_hgl_profile([], starting_downstream_hgl_ft=100.0)

    def test_assumptions_included(self):
        """Assumptions included in profile."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        assert len(profile.assumptions) > 0
        assert any("steady" in a.lower() for a in profile.assumptions)

    def test_warnings_aggregated(self):
        """Profile aggregates warnings from all reaches."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        all_warnings = profile.all_warnings()
        assert len(all_warnings) >= 2

    def test_custom_name(self):
        """Custom profile name accepted."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
        ]
        profile = compute_hgl_profile(
            reaches,
            starting_downstream_hgl_ft=100.0,
            name="Main Storm Trunk",
        )

        assert profile.name == "Main Storm Trunk"

    def test_mixed_pipe_types(self):
        """Profile handles mixed circular and box pipes."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Circular Reach",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
            ),
            PipeReachInput(
                id="reach_002",
                pipe_id="pipe_002",
                name="Box Reach",
                design_flow_cfs=10.0,
                length_ft=150.0,
                roughness_n=0.015,
                width_in=24.0,
                height_in=18.0,
            ),
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        assert len(profile.reaches) == 2
        assert profile.reaches[0].reach_id == "reach_001"
        assert profile.reaches[1].reach_id == "reach_002"


class TestHglProfileRoundTrip:
    """Tests for profile serialization."""

    def test_profile_round_trips(self):
        """Profile round-trips through dict."""
        reaches = [
            PipeReachInput(
                id="reach_001",
                pipe_id="pipe_001",
                name="Reach 1",
                design_flow_cfs=10.0,
                length_ft=200.0,
                roughness_n=0.013,
                diameter_in=18.0,
                upstream_invert_elevation_ft=99.0,
                downstream_invert_elevation_ft=98.0,
            ),
        ]
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        from civil_toolbox.hydraulics.models import HydraulicProfileResult

        restored = HydraulicProfileResult.from_dict(profile.to_dict())

        assert restored.name == profile.name
        assert restored.starting_downstream_hgl_ft == profile.starting_downstream_hgl_ft
        assert len(restored.reaches) == len(profile.reaches)
        assert restored.reaches[0].reach_id == profile.reaches[0].reach_id
