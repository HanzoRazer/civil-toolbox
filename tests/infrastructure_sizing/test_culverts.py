"""Tests for culvert capacity functions."""

import pytest

from civil_toolbox.infrastructure import Culvert
from civil_toolbox.infrastructure_sizing import (
    estimate_culvert_barrel_capacity_cfs,
    check_culvert_capacity,
)
from civil_toolbox.infrastructure_sizing.errors import InvalidSizingInputError


class TestEstimateCulvertCapacity:
    """Tests for estimate_culvert_barrel_capacity_cfs."""

    def test_circular_culvert(self):
        """Estimate capacity of circular culvert."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            shape="circular",
            diameter_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.024,
        )
        capacity, velocity = estimate_culvert_barrel_capacity_cfs(culvert)
        assert capacity > 0
        assert velocity > 0

    def test_box_culvert(self):
        """Estimate capacity of box culvert."""
        culvert = Culvert(
            id="c1",
            name="BC-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.012,
        )
        capacity, velocity = estimate_culvert_barrel_capacity_cfs(culvert)
        assert capacity > 0
        assert velocity > 0

    def test_zero_slope_raises(self):
        """Zero slope raises error."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.0,
        )
        with pytest.raises(InvalidSizingInputError, match="zero or negative slope"):
            estimate_culvert_barrel_capacity_cfs(culvert)


class TestCheckCulvertCapacity:
    """Tests for check_culvert_capacity."""

    def test_passes_when_below_capacity(self):
        """Check passes when design flow is below capacity."""
        culvert = Culvert(
            id="c1",
            name="BC-1",
            shape="box",
            width_in=48.0,
            height_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.012,
        )
        result = check_culvert_capacity(culvert, design_flow_cfs=50.0)
        assert result.passes is True
        assert result.capacity_cfs > 50.0

    def test_fails_when_above_capacity(self):
        """Check fails when design flow exceeds capacity."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=24.0,
            length_ft=80.0,
            slope_ft_per_ft=0.005,
        )
        result = check_culvert_capacity(culvert, design_flow_cfs=500.0)
        assert result.passes is False
        assert result.is_overcapacity is True

    def test_barrel_capacity_only_warning(self):
        """Result includes barrel-capacity-only warning."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
        )
        result = check_culvert_capacity(culvert, design_flow_cfs=50.0)
        warning_codes = [w.warning_code for w in result.warnings]
        assert "BARREL_CAPACITY_ONLY" in warning_codes

    def test_result_has_assumptions(self):
        """Result includes assumptions about barrel capacity."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
        )
        result = check_culvert_capacity(culvert, design_flow_cfs=50.0)
        assert len(result.assumptions) > 0
        assert any("barrel" in a.lower() for a in result.assumptions)

    def test_negative_design_flow_raises(self):
        """Negative design flow raises error."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
        )
        with pytest.raises(InvalidSizingInputError, match="cannot be negative"):
            check_culvert_capacity(culvert, design_flow_cfs=-10.0)

    def test_method_indicates_manning(self):
        """Method field indicates Manning's equation."""
        culvert = Culvert(
            id="c1",
            name="C-1",
            diameter_in=36.0,
            length_ft=80.0,
            slope_ft_per_ft=0.01,
        )
        result = check_culvert_capacity(culvert, design_flow_cfs=50.0)
        assert "Manning" in result.method
        assert "barrel" in result.method.lower()
