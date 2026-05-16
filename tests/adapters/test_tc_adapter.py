"""Tests for Time of Concentration adapter."""

import pytest

from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.domain.calculation import CalculationResult

from civil_toolbox.adapters.time_of_concentration import TimeOfConcentrationAdapter
from civil_toolbox.adapters.errors import MissingFieldError, IncompatibleEntityError


class TestTimeOfConcentrationAdapterKirpich:
    """Tests for TimeOfConcentrationAdapter.calculate_kirpich."""

    def test_calculates_tc_minutes(self):
        path = FlowPath(name="Test Path")
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=3000,
            slope_ft_per_ft=0.02,
        ))

        result = TimeOfConcentrationAdapter.calculate_kirpich(path)

        assert isinstance(result, CalculationResult)
        assert result.method == "tc_kirpich"
        assert result.outputs["tc_minutes"] > 0
        assert result.units["tc_minutes"] == "min"

    def test_includes_inputs(self):
        path = FlowPath(name="Test")
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=2000,
            slope_ft_per_ft=0.03,
        ))

        result = TimeOfConcentrationAdapter.calculate_kirpich(path)

        assert result.inputs["flow_length_ft"] == 2000
        assert result.inputs["elevation_diff_ft"] == pytest.approx(60.0)
        assert result.inputs["segment_count"] == 1

    def test_multiple_segments(self):
        path = FlowPath(name="Multi-segment")
        path.add_segment(FlowPathSegment(
            segment_type="shallow_concentrated",
            length_ft=1000,
            slope_ft_per_ft=0.02,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=2000,
            slope_ft_per_ft=0.01,
        ))

        result = TimeOfConcentrationAdapter.calculate_kirpich(path)

        assert result.inputs["flow_length_ft"] == 3000
        expected_drop = 1000 * 0.02 + 2000 * 0.01
        assert result.inputs["elevation_diff_ft"] == pytest.approx(expected_drop)

    def test_links_to_entity(self):
        path = FlowPath(name="Test")
        path.add_segment(FlowPathSegment(length_ft=1000, slope_ft_per_ft=0.02))

        result = TimeOfConcentrationAdapter.calculate_kirpich(path)

        assert result.entity_id == path.id
        assert result.entity_type == "FlowPath"

    def test_no_segments_raises(self):
        path = FlowPath(name="Empty")

        with pytest.raises(IncompatibleEntityError):
            TimeOfConcentrationAdapter.calculate_kirpich(path)

    def test_zero_length_raises(self):
        path = FlowPath(name="Bad Segment")
        path.segments.append(FlowPathSegment(length_ft=0, slope_ft_per_ft=0.02))

        with pytest.raises(MissingFieldError) as exc_info:
            TimeOfConcentrationAdapter.calculate_kirpich(path)

        assert exc_info.value.field_name == "length_ft"


class TestTimeOfConcentrationAdapterKerby:
    """Tests for TimeOfConcentrationAdapter.calculate_kerby."""

    def test_calculates_tc_minutes(self):
        path = FlowPath(name="Sheet Flow")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=300,
            slope_ft_per_ft=0.02,
            roughness_n=0.40,
        ))

        result = TimeOfConcentrationAdapter.calculate_kerby(path)

        assert result.method == "tc_kerby"
        assert result.outputs["tc_minutes"] > 0

    def test_includes_weighted_roughness(self):
        path = FlowPath(name="Multi-segment")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100,
            slope_ft_per_ft=0.02,
            roughness_n=0.20,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100,
            slope_ft_per_ft=0.02,
            roughness_n=0.40,
        ))

        result = TimeOfConcentrationAdapter.calculate_kerby(path)

        expected_n = (0.20 * 100 + 0.40 * 100) / 200
        assert result.inputs["retardance_n"] == pytest.approx(expected_n)

    def test_missing_roughness_raises(self):
        path = FlowPath(name="No Roughness")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=300,
            slope_ft_per_ft=0.02,
        ))

        with pytest.raises(MissingFieldError) as exc_info:
            TimeOfConcentrationAdapter.calculate_kerby(path)

        assert exc_info.value.field_name == "roughness_n"

    def test_warns_on_long_flow_length(self):
        path = FlowPath(name="Long Path")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=1500,
            slope_ft_per_ft=0.01,
            roughness_n=0.30,
        ))

        result = TimeOfConcentrationAdapter.calculate_kerby(path)

        assert len(result.warnings) == 1
        assert "1000" in result.warnings[0].message


class TestTimeOfConcentrationAdapterComposite:
    """Tests for TimeOfConcentrationAdapter.calculate_composite."""

    def test_calculates_composite_tc(self):
        path = FlowPath(name="Composite Path")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100,
            slope_ft_per_ft=0.02,
            roughness_n=0.15,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=2000,
            slope_ft_per_ft=0.01,
        ))

        result = TimeOfConcentrationAdapter.calculate_composite(
            path, rainfall_2yr_24hr_in=3.5
        )

        assert result.method == "tc_composite"
        assert result.outputs["tc_minutes"] > 0

    def test_records_segment_results(self):
        path = FlowPath(name="Two Segments")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100,
            slope_ft_per_ft=0.02,
            roughness_n=0.15,
        ))
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=1000,
            slope_ft_per_ft=0.02,
        ))

        result = TimeOfConcentrationAdapter.calculate_composite(
            path, rainfall_2yr_24hr_in=3.5
        )

        assert "segment_results" in result.metadata
        assert len(result.metadata["segment_results"]) == 2
        assert result.metadata["segment_results"][0]["method"] == "kinematic_wave"
        assert result.metadata["segment_results"][1]["method"] == "kirpich"

    def test_sheet_flow_without_rainfall_raises(self):
        path = FlowPath(name="Sheet Flow")
        path.add_segment(FlowPathSegment(
            segment_type="sheet",
            length_ft=100,
            slope_ft_per_ft=0.02,
            roughness_n=0.15,
        ))

        with pytest.raises(IncompatibleEntityError) as exc_info:
            TimeOfConcentrationAdapter.calculate_composite(path)

        assert "rainfall" in str(exc_info.value).lower()

    def test_channel_only_no_rainfall_needed(self):
        path = FlowPath(name="Channel Only")
        path.add_segment(FlowPathSegment(
            segment_type="channel",
            length_ft=2000,
            slope_ft_per_ft=0.02,
        ))

        result = TimeOfConcentrationAdapter.calculate_composite(path)

        assert result.outputs["tc_minutes"] > 0

    def test_no_segments_raises(self):
        path = FlowPath(name="Empty")

        with pytest.raises(IncompatibleEntityError):
            TimeOfConcentrationAdapter.calculate_composite(path)
