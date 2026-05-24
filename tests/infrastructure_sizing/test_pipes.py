"""Tests for pipe capacity functions."""

import pytest

from civil_toolbox.infrastructure import Pipe
from civil_toolbox.infrastructure_sizing import (
    estimate_pipe_full_flow_capacity_cfs,
    check_pipe_capacity,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestEstimatePipeCapacity:
    """Tests for estimate_pipe_full_flow_capacity_cfs."""

    def test_circular_pipe(self):
        """Estimate capacity of circular pipe."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            shape="circular",
            diameter_in=18.0,
            length_ft=200.0,
            slope_ft_per_ft=0.005,
            mannings_n=0.013,
        )
        capacity, velocity = estimate_pipe_full_flow_capacity_cfs(pipe)
        assert capacity > 0
        assert velocity > 0

    def test_box_pipe(self):
        """Estimate capacity of box pipe."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=100.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.012,
        )
        capacity, velocity = estimate_pipe_full_flow_capacity_cfs(pipe)
        assert capacity > 0
        assert velocity > 0

    def test_zero_slope_raises(self):
        """Zero slope raises error."""
        pipe = Pipe(
            id="p1",
            name="P-1",
            diameter_in=18.0,
            length_ft=100.0,
            slope_ft_per_ft=0.0,
        )
        with pytest.raises(InvalidSizingInputError, match="zero or negative slope"):
            estimate_pipe_full_flow_capacity_cfs(pipe)

    def test_larger_pipe_more_capacity(self):
        """Larger pipe has more capacity."""
        pipe_18 = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01, mannings_n=0.013,
        )
        pipe_24 = Pipe(
            id="p2", name="P-2",
            diameter_in=24.0, length_ft=100.0,
            slope_ft_per_ft=0.01, mannings_n=0.013,
        )
        cap_18, _ = estimate_pipe_full_flow_capacity_cfs(pipe_18)
        cap_24, _ = estimate_pipe_full_flow_capacity_cfs(pipe_24)
        assert cap_24 > cap_18

    def test_steeper_slope_more_capacity(self):
        """Steeper slope increases capacity."""
        pipe_flat = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.005, mannings_n=0.013,
        )
        pipe_steep = Pipe(
            id="p2", name="P-2",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.02, mannings_n=0.013,
        )
        cap_flat, _ = estimate_pipe_full_flow_capacity_cfs(pipe_flat)
        cap_steep, _ = estimate_pipe_full_flow_capacity_cfs(pipe_steep)
        assert cap_steep > cap_flat


class TestCheckPipeCapacity:
    """Tests for check_pipe_capacity."""

    def test_passes_when_below_capacity(self):
        """Check passes when design flow is below capacity."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=200.0,
            slope_ft_per_ft=0.005, mannings_n=0.013,
        )
        result = check_pipe_capacity(pipe, design_flow_cfs=5.0)
        assert result.passes is True
        assert result.capacity_cfs > 5.0
        assert result.utilization_ratio < 1.0

    def test_fails_when_above_capacity(self):
        """Check fails when design flow exceeds capacity."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=12.0, length_ft=200.0,
            slope_ft_per_ft=0.005, mannings_n=0.013,
        )
        result = check_pipe_capacity(pipe, design_flow_cfs=100.0)
        assert result.passes is False
        assert result.is_overcapacity is True

    def test_zero_design_flow_passes(self):
        """Zero design flow always passes."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=200.0,
            slope_ft_per_ft=0.005, mannings_n=0.013,
        )
        result = check_pipe_capacity(pipe, design_flow_cfs=0.0)
        assert result.passes is True

    def test_negative_design_flow_raises(self):
        """Negative design flow raises error."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        )
        with pytest.raises(InvalidSizingInputError, match="cannot be negative"):
            check_pipe_capacity(pipe, design_flow_cfs=-5.0)

    def test_result_has_assumptions(self):
        """Result includes assumptions."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        )
        result = check_pipe_capacity(pipe, design_flow_cfs=5.0)
        assert len(result.assumptions) > 0
        assert "Full-flow" in result.assumptions[0]

    def test_low_velocity_warning(self):
        """Low velocity generates warning."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=36.0, length_ft=100.0,
            slope_ft_per_ft=0.0002,
            mannings_n=0.013,
        )
        result = check_pipe_capacity(pipe, design_flow_cfs=1.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "LOW_VELOCITY" in warning_codes

    def test_high_utilization_warning(self):
        """High utilization generates warning."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.013,
        )
        capacity, _ = estimate_pipe_full_flow_capacity_cfs(pipe)
        result = check_pipe_capacity(pipe, design_flow_cfs=capacity * 0.85)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "HIGH_UTILIZATION" in warning_codes

    def test_zero_slope_warning(self):
        """Zero slope generates error warning."""
        pipe = Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.0,
        )
        result = check_pipe_capacity(pipe, design_flow_cfs=5.0)
        assert result.passes is False
        warning_codes = [w.warning_code for w in result.warnings]
        assert "ZERO_SLOPE" in warning_codes
