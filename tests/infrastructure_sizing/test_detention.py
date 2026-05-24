"""Tests for detention storage functions."""

import pytest

from civil_toolbox.infrastructure import DetentionFacility, StageStoragePoint
from civil_toolbox.infrastructure_sizing import check_detention_storage
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestCheckDetentionStorage:
    """Tests for check_detention_storage."""

    def test_passes_when_storage_adequate(self):
        """Check passes when required storage is less than available."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=80000.0)
        assert result.passes is True
        assert result.storage_cuft == 100000
        assert result.utilization_ratio == pytest.approx(0.8)

    def test_fails_when_storage_inadequate(self):
        """Check fails when required storage exceeds available."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=50000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=80000.0)
        assert result.passes is False
        assert result.utilization_ratio > 1.0

    def test_zero_required_storage_passes(self):
        """Zero required storage always passes."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=0.0)
        assert result.passes is True

    def test_negative_required_storage_raises(self):
        """Negative required storage raises error."""
        facility = DetentionFacility(id="d1", name="DP-1")
        with pytest.raises(InvalidSizingInputError, match="cannot be negative"):
            check_detention_storage(facility, required_storage_cuft=-1000.0)

    def test_estimates_from_geometry(self):
        """Storage is estimated from geometry when no stage-storage."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            pond_bottom_area_sqft=10000.0,
            maximum_depth_ft=5.0,
        )
        result = check_detention_storage(facility, required_storage_cuft=40000.0)
        assert result.passes is True
        assert result.storage_cuft == pytest.approx(50000.0)

    def test_no_storage_data_fails(self):
        """Check fails when no storage data available."""
        facility = DetentionFacility(id="d1", name="DP-1")
        result = check_detention_storage(facility, required_storage_cuft=50000.0)
        assert result.passes is False
        warning_codes = [w.warning_code for w in result.warnings]
        assert "NO_STORAGE_DATA" in warning_codes

    def test_high_utilization_warning(self):
        """High utilization generates warning."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=95000.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "HIGH_UTILIZATION" in warning_codes

    def test_routing_required_warning(self):
        """Result includes routing-required informational warning."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=50000.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "ROUTING_REQUIRED" in warning_codes

    def test_permanent_pool_warning(self):
        """Facility with permanent pool gets informational warning."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            permanent_pool_depth_ft=2.0,
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=50000.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "PERMANENT_POOL" in warning_codes

    def test_spillway_limits_storage(self):
        """Spillway below max stage limits usable storage."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=94.0, storage_cuft=60000),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
            spillway_elevation_ft=94.0,
        )
        result = check_detention_storage(facility, required_storage_cuft=80000.0)
        assert result.passes is False
        assert result.storage_cuft == 60000.0
        warning_codes = [w.warning_code for w in result.warnings]
        assert "SPILLWAY_LIMITS_STORAGE" in warning_codes

    def test_result_has_assumptions(self):
        """Result includes volume-comparison assumptions."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=100000),
            ],
        )
        result = check_detention_storage(facility, required_storage_cuft=50000.0)
        assert len(result.assumptions) > 0
        assert any("routing" in a.lower() for a in result.assumptions)
