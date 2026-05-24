"""Tests for DetentionFacility."""

import pytest

from civil_toolbox.infrastructure import DetentionFacility, StageStoragePoint
from civil_toolbox.infrastructure.errors import InvalidInfrastructureError


class TestStageStoragePoint:
    """Tests for StageStoragePoint."""

    def test_basic_creation(self):
        """Create a stage-storage point."""
        point = StageStoragePoint(stage_ft=90.0, storage_cuft=0)
        assert point.stage_ft == 90.0
        assert point.storage_cuft == 0

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip."""
        original = StageStoragePoint(stage_ft=92.0, storage_cuft=25000)
        restored = StageStoragePoint.from_dict(original.to_dict())
        assert restored.stage_ft == original.stage_ft
        assert restored.storage_cuft == original.storage_cuft


class TestDetentionFacility:
    """Tests for DetentionFacility."""

    def test_basic_creation(self):
        """Create a basic detention facility."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            facility_type="detention",
            pond_bottom_elevation_ft=90.0,
        )
        assert facility.id == "d1"
        assert facility.facility_type == "detention"

    def test_facility_types(self):
        """All valid facility types work."""
        for ftype in ["detention", "retention", "infiltration", "constructed_wetland"]:
            facility = DetentionFacility(id="d", name="D", facility_type=ftype)
            assert facility.facility_type == ftype

    def test_invalid_facility_type_raises(self):
        """Invalid facility type raises error."""
        with pytest.raises(InvalidInfrastructureError, match="facility_type must be one of"):
            DetentionFacility(id="d", name="D", facility_type="invalid")

    def test_stage_storage_curve(self):
        """Stage-storage curve works."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=92.0, storage_cuft=25000),
                StageStoragePoint(stage_ft=94.0, storage_cuft=60000),
                StageStoragePoint(stage_ft=96.0, storage_cuft=110000),
            ],
        )
        assert facility.total_storage_cuft == 110000

    def test_stage_storage_must_be_sorted(self):
        """Stage-storage must be sorted by stage."""
        with pytest.raises(InvalidInfrastructureError, match="sorted"):
            DetentionFacility(
                id="d", name="D",
                stage_storage=[
                    StageStoragePoint(stage_ft=92.0, storage_cuft=25000),
                    StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                ],
            )

    def test_storage_at_stage_interpolation(self):
        """storage_at_stage interpolates correctly."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=92.0, storage_cuft=20000),
                StageStoragePoint(stage_ft=94.0, storage_cuft=60000),
            ],
        )
        assert facility.storage_at_stage(90.0) == 0
        assert facility.storage_at_stage(91.0) == 10000
        assert facility.storage_at_stage(92.0) == 20000
        assert facility.storage_at_stage(93.0) == 40000

    def test_storage_at_stage_below_returns_zero(self):
        """Stage below minimum returns 0."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=92.0, storage_cuft=20000),
            ],
        )
        assert facility.storage_at_stage(88.0) == 0

    def test_storage_at_stage_above_returns_max(self):
        """Stage above maximum returns max storage."""
        facility = DetentionFacility(
            id="d1",
            name="DP-1",
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=92.0, storage_cuft=20000),
            ],
        )
        assert facility.storage_at_stage(100.0) == 20000

    def test_storage_at_stage_empty_curve(self):
        """Empty stage-storage returns None."""
        facility = DetentionFacility(id="d", name="D")
        assert facility.storage_at_stage(90.0) is None
        assert facility.total_storage_cuft is None

    def test_serialization_roundtrip(self):
        """to_dict/from_dict roundtrip preserves data."""
        original = DetentionFacility(
            id="d1",
            name="DP-1",
            description="Test pond",
            facility_type="detention",
            pond_bottom_elevation_ft=90.0,
            pond_bottom_area_sqft=10000.0,
            side_slope=3.0,
            maximum_depth_ft=6.0,
            stage_storage=[
                StageStoragePoint(stage_ft=90.0, storage_cuft=0),
                StageStoragePoint(stage_ft=96.0, storage_cuft=110000),
            ],
            spillway_elevation_ft=95.5,
            spillway_width_ft=10.0,
            metadata={"test": True},
        )
        restored = DetentionFacility.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.facility_type == original.facility_type
        assert restored.pond_bottom_area_sqft == original.pond_bottom_area_sqft
        assert len(restored.stage_storage) == 2
        assert restored.spillway_width_ft == original.spillway_width_ft
