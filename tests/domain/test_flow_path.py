"""Tests for FlowPath and FlowPathSegment domain entities."""

import pytest

from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment


class TestFlowPathSegment:
    """Tests for FlowPathSegment."""

    def test_creates_with_defaults(self):
        segment = FlowPathSegment()
        assert segment.segment_type == "sheet"
        assert segment.length_ft == 0.0
        assert segment.slope_ft_per_ft == 0.0

    def test_creates_with_values(self):
        segment = FlowPathSegment(
            segment_type="shallow_concentrated",
            length_ft=500.0,
            slope_ft_per_ft=0.02,
            roughness_n=0.05,
        )
        assert segment.segment_type == "shallow_concentrated"
        assert segment.length_ft == 500.0
        assert segment.slope_ft_per_ft == 0.02
        assert segment.roughness_n == 0.05

    def test_valid_segment_types(self):
        for seg_type in ("sheet", "shallow_concentrated", "channel"):
            segment = FlowPathSegment(segment_type=seg_type)
            assert segment.segment_type == seg_type

    def test_raises_on_invalid_segment_type(self):
        with pytest.raises(ValueError, match="segment_type must be"):
            FlowPathSegment(segment_type="invalid")

    def test_raises_on_negative_length(self):
        with pytest.raises(ValueError, match="length_ft cannot be negative"):
            FlowPathSegment(length_ft=-100)

    def test_raises_on_negative_slope(self):
        with pytest.raises(ValueError, match="slope_ft_per_ft cannot be negative"):
            FlowPathSegment(slope_ft_per_ft=-0.01)

    def test_raises_on_non_positive_roughness(self):
        with pytest.raises(ValueError, match="roughness_n must be positive"):
            FlowPathSegment(roughness_n=0)
        with pytest.raises(ValueError, match="roughness_n must be positive"):
            FlowPathSegment(roughness_n=-0.1)

    def test_to_dict_serialization(self):
        segment = FlowPathSegment(
            segment_type="channel",
            length_ft=1000.0,
            slope_ft_per_ft=0.005,
            roughness_n=0.035,
        )
        data = segment.to_dict()
        assert data["segment_type"] == "channel"
        assert data["length_ft"] == 1000.0
        assert data["slope_ft_per_ft"] == 0.005

    def test_from_dict_deserialization(self):
        data = {
            "segment_type": "sheet",
            "length_ft": 100.0,
            "slope_ft_per_ft": 0.01,
            "roughness_n": 0.15,
        }
        segment = FlowPathSegment.from_dict(data)
        assert segment.segment_type == "sheet"
        assert segment.length_ft == 100.0

    def test_round_trip_serialization(self):
        segment = FlowPathSegment(
            segment_type="shallow_concentrated",
            length_ft=750.0,
            slope_ft_per_ft=0.015,
        )
        data = segment.to_dict()
        restored = FlowPathSegment.from_dict(data)
        assert restored.segment_type == segment.segment_type
        assert restored.length_ft == segment.length_ft


class TestFlowPath:
    """Tests for FlowPath."""

    def test_creates_with_name(self):
        path = FlowPath(name="Main Flow Path")
        assert path.name == "Main Flow Path"
        assert path.id is not None

    def test_raises_on_missing_name(self):
        with pytest.raises(ValueError, match="requires a name"):
            FlowPath(name="")

    def test_creates_with_empty_segments(self):
        path = FlowPath(name="Test")
        assert path.segments == []
        assert path.total_length_ft == 0.0

    def test_add_segment(self):
        path = FlowPath(name="Test")
        segment = FlowPathSegment(length_ft=200.0)
        path.add_segment(segment)
        assert len(path.segments) == 1

    def test_add_segment_validates_type(self):
        path = FlowPath(name="Test")
        with pytest.raises(TypeError, match="Expected a FlowPathSegment"):
            path.add_segment("not a segment")

    def test_total_length_sums_segments(self):
        path = FlowPath(name="Test")
        path.add_segment(FlowPathSegment(length_ft=100.0))
        path.add_segment(FlowPathSegment(length_ft=250.0))
        path.add_segment(FlowPathSegment(length_ft=500.0))
        assert path.total_length_ft == 850.0

    def test_creates_with_initial_segments(self):
        path = FlowPath(
            name="Pre-populated",
            segments=[
                FlowPathSegment(segment_type="sheet", length_ft=100.0),
                FlowPathSegment(segment_type="channel", length_ft=500.0),
            ],
        )
        assert len(path.segments) == 2
        assert path.total_length_ft == 600.0

    def test_to_dict_serialization(self):
        path = FlowPath(name="Serialize Test")
        path.add_segment(FlowPathSegment(length_ft=300.0, slope_ft_per_ft=0.02))
        data = path.to_dict()
        assert data["name"] == "Serialize Test"
        assert len(data["segments"]) == 1

    def test_from_dict_deserialization(self):
        data = {
            "id": "path-123",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
            "name": "Restored Path",
            "segments": [
                {"segment_type": "sheet", "length_ft": 150.0, "slope_ft_per_ft": 0.01},
                {"segment_type": "channel", "length_ft": 800.0, "slope_ft_per_ft": 0.005},
            ],
        }
        path = FlowPath.from_dict(data)
        assert path.id == "path-123"
        assert path.name == "Restored Path"
        assert len(path.segments) == 2
        assert path.total_length_ft == 950.0

    def test_round_trip_serialization(self):
        path = FlowPath(name="Round Trip Path")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100.0,
            slope_ft_per_ft=0.02,
            roughness_n=0.15,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="shallow_concentrated",
            length_ft=400.0,
            slope_ft_per_ft=0.01,
        ))
        data = path.to_dict()
        restored = FlowPath.from_dict(data)
        assert restored.id == path.id
        assert restored.name == path.name
        assert len(restored.segments) == 2
        assert restored.total_length_ft == path.total_length_ft
