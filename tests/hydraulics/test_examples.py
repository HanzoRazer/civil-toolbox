"""Tests for synthetic HGL examples."""

import pytest

from civil_toolbox.hydraulics.examples import (
    create_simple_trunk_reaches,
    create_surcharged_system_reaches,
    create_mixed_geometry_reaches,
    create_minimal_reach,
)
from civil_toolbox.hydraulics.compute import compute_hgl_profile


class TestCreateSimpleTrunkReaches:
    """Tests for create_simple_trunk_reaches."""

    def test_returns_three_reaches(self):
        """Returns three reaches."""
        reaches = create_simple_trunk_reaches()
        assert len(reaches) == 3

    def test_reaches_ordered_downstream_to_upstream(self):
        """Reaches are ordered downstream to upstream."""
        reaches = create_simple_trunk_reaches()
        assert reaches[0].name == "Outlet Reach"
        assert reaches[2].name == "Upstream Reach"

    def test_all_reaches_have_elevations(self):
        """All reaches have elevation data."""
        reaches = create_simple_trunk_reaches()
        for reach in reaches:
            assert reach.upstream_invert_elevation_ft is not None
            assert reach.downstream_invert_elevation_ft is not None
            assert reach.upstream_rim_elevation_ft is not None
            assert reach.downstream_rim_elevation_ft is not None

    def test_profile_computes_successfully(self):
        """Profile computes without errors."""
        reaches = create_simple_trunk_reaches()
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        assert len(profile.reaches) == 3
        assert profile.ending_upstream_hgl_ft > 100.0


class TestCreateSurchargedSystemReaches:
    """Tests for create_surcharged_system_reaches."""

    def test_returns_two_reaches(self):
        """Returns two reaches."""
        reaches = create_surcharged_system_reaches()
        assert len(reaches) == 2

    def test_produces_surcharge_warnings(self):
        """Produces surcharge warnings when analyzed."""
        reaches = create_surcharged_system_reaches()
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=100.0)

        all_warnings = profile.all_warnings()
        surcharge_warnings = [w for w in all_warnings if "surcharge" in w.code]
        assert len(surcharge_warnings) > 0


class TestCreateMixedGeometryReaches:
    """Tests for create_mixed_geometry_reaches."""

    def test_returns_three_reaches(self):
        """Returns three reaches."""
        reaches = create_mixed_geometry_reaches()
        assert len(reaches) == 3

    def test_has_box_culvert(self):
        """First reach is a box culvert."""
        reaches = create_mixed_geometry_reaches()
        assert reaches[0].is_rectangular
        assert not reaches[0].is_circular

    def test_has_circular_pipes(self):
        """Later reaches are circular."""
        reaches = create_mixed_geometry_reaches()
        assert reaches[1].is_circular
        assert reaches[2].is_circular

    def test_profile_computes_successfully(self):
        """Profile computes with mixed geometry."""
        reaches = create_mixed_geometry_reaches()
        profile = compute_hgl_profile(reaches, starting_downstream_hgl_ft=98.0)

        assert len(profile.reaches) == 3
        assert profile.ending_upstream_hgl_ft > 98.0


class TestCreateMinimalReach:
    """Tests for create_minimal_reach."""

    def test_returns_single_reach(self):
        """Returns a single reach."""
        reach = create_minimal_reach()
        assert reach.id == "reach_min"

    def test_no_elevations(self):
        """Has no elevation data."""
        reach = create_minimal_reach()
        assert reach.upstream_invert_elevation_ft is None
        assert reach.downstream_invert_elevation_ft is None

    def test_is_circular(self):
        """Is a circular pipe."""
        reach = create_minimal_reach()
        assert reach.is_circular

    def test_computes_successfully(self):
        """Computes without errors."""
        reach = create_minimal_reach()
        profile = compute_hgl_profile([reach], starting_downstream_hgl_ft=100.0)

        assert len(profile.reaches) == 1
