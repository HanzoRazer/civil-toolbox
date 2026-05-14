"""Tests for time of concentration calculators."""

import pytest

from civil_toolbox.calculators.time_of_concentration import (
    TimeOfConcentration,
    TimeOfConcentrationResult,
)
from civil_toolbox.calculators.validation import CalculatorInputError


class TestKirpich:
    """Tests for TimeOfConcentration.kirpich."""

    def test_returns_minutes(self):
        result = TimeOfConcentration.kirpich(
            flow_length_ft=5000,
            elevation_diff_ft=100,
        )
        assert result.tc_minutes > 0
        assert result.method == "kirpich"

    def test_returns_result_dataclass(self):
        result = TimeOfConcentration.kirpich(
            flow_length_ft=5000,
            elevation_diff_ft=100,
        )
        assert isinstance(result, TimeOfConcentrationResult)
        assert result.flow_length_ft == 5000
        assert result.slope_percent == pytest.approx(2.0)

    def test_longer_path_more_time(self):
        short = TimeOfConcentration.kirpich(flow_length_ft=1000, elevation_diff_ft=50)
        long = TimeOfConcentration.kirpich(flow_length_ft=5000, elevation_diff_ft=50)
        assert long.tc_minutes > short.tc_minutes

    def test_steeper_slope_less_time(self):
        gentle = TimeOfConcentration.kirpich(flow_length_ft=5000, elevation_diff_ft=50)
        steep = TimeOfConcentration.kirpich(flow_length_ft=5000, elevation_diff_ft=200)
        assert steep.tc_minutes < gentle.tc_minutes

    def test_known_value(self):
        result = TimeOfConcentration.kirpich(
            flow_length_ft=3000,
            elevation_diff_ft=60,
        )
        slope = 60 / 3000
        expected = 0.0078 * (3000 ** 0.77) * (slope ** -0.385)
        assert result.tc_minutes == pytest.approx(expected)

    def test_invalid_length_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.kirpich(flow_length_ft=0, elevation_diff_ft=100)

    def test_invalid_elevation_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.kirpich(flow_length_ft=5000, elevation_diff_ft=0)


class TestKerby:
    """Tests for TimeOfConcentration.kerby."""

    def test_returns_minutes(self):
        result = TimeOfConcentration.kerby(
            flow_length_ft=300,
            slope_percent=2.0,
            retardance_n=0.40,
        )
        assert result.tc_minutes > 0
        assert result.method == "kerby"

    def test_returns_result_dataclass(self):
        result = TimeOfConcentration.kerby(
            flow_length_ft=300,
            slope_percent=2.0,
            retardance_n=0.40,
        )
        assert isinstance(result, TimeOfConcentrationResult)
        assert result.flow_length_ft == 300
        assert result.slope_percent == 2.0

    def test_rougher_surface_more_time(self):
        smooth = TimeOfConcentration.kerby(
            flow_length_ft=300, slope_percent=2.0, retardance_n=0.02
        )
        rough = TimeOfConcentration.kerby(
            flow_length_ft=300, slope_percent=2.0, retardance_n=0.40
        )
        assert rough.tc_minutes > smooth.tc_minutes

    def test_steeper_slope_less_time(self):
        gentle = TimeOfConcentration.kerby(
            flow_length_ft=300, slope_percent=0.5, retardance_n=0.20
        )
        steep = TimeOfConcentration.kerby(
            flow_length_ft=300, slope_percent=2.0, retardance_n=0.20
        )
        assert steep.tc_minutes < gentle.tc_minutes

    def test_known_value(self):
        result = TimeOfConcentration.kerby(
            flow_length_ft=300,
            slope_percent=2.0,
            retardance_n=0.40,
        )
        slope_ft_per_ft = 0.02
        expected = 0.83 * ((300 * 0.40) ** 0.467) * (slope_ft_per_ft ** -0.235)
        assert result.tc_minutes == pytest.approx(expected)

    def test_invalid_retardance_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.kerby(
                flow_length_ft=300, slope_percent=2.0, retardance_n=1.5
            )

    def test_invalid_length_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.kerby(
                flow_length_ft=0, slope_percent=2.0, retardance_n=0.40
            )

    def test_invalid_slope_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.kerby(
                flow_length_ft=300, slope_percent=0, retardance_n=0.40
            )


class TestNRCSLag:
    """Tests for TimeOfConcentration.nrcs_lag."""

    def test_returns_minutes(self):
        result = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000,
            slope_percent=3.0,
            curve_number=75,
        )
        assert result.tc_minutes > 0
        assert result.method == "nrcs_lag"

    def test_returns_result_dataclass(self):
        result = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000,
            slope_percent=3.0,
            curve_number=75,
        )
        assert isinstance(result, TimeOfConcentrationResult)
        assert result.flow_length_ft == 5000
        assert result.slope_percent == 3.0

    def test_higher_cn_less_time(self):
        low_cn = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000, slope_percent=3.0, curve_number=60
        )
        high_cn = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000, slope_percent=3.0, curve_number=90
        )
        assert high_cn.tc_minutes < low_cn.tc_minutes

    def test_steeper_slope_less_time(self):
        gentle = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000, slope_percent=1.0, curve_number=75
        )
        steep = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000, slope_percent=5.0, curve_number=75
        )
        assert steep.tc_minutes < gentle.tc_minutes

    def test_known_value(self):
        result = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000,
            slope_percent=3.0,
            curve_number=75,
        )
        import math

        s = (1000 / 75) - 10
        tlag_hr = (5000 ** 0.8) * ((s + 1) ** 0.7) / (1900 * math.sqrt(3.0))
        tc_hr = tlag_hr / 0.6
        expected_minutes = tc_hr * 60
        assert result.tc_minutes == pytest.approx(expected_minutes)

    def test_invalid_cn_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.nrcs_lag(
                flow_length_ft=5000, slope_percent=3.0, curve_number=0
            )

    def test_invalid_length_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.nrcs_lag(
                flow_length_ft=0, slope_percent=3.0, curve_number=75
            )


class TestComposite:
    """Tests for TimeOfConcentration.composite."""

    def test_single_segment(self):
        result = TimeOfConcentration.composite([
            ("kirpich", {"flow_length_ft": 3000, "elevation_diff_ft": 60}),
        ])
        single = TimeOfConcentration.kirpich(flow_length_ft=3000, elevation_diff_ft=60)
        assert result == pytest.approx(single.tc_minutes)

    def test_multiple_segments_sum(self):
        seg1 = TimeOfConcentration.kerby(
            flow_length_ft=300, slope_percent=2.0, retardance_n=0.40
        )
        seg2 = TimeOfConcentration.kirpich(
            flow_length_ft=2000, elevation_diff_ft=40
        )

        result = TimeOfConcentration.composite([
            ("kerby", {"flow_length_ft": 300, "slope_percent": 2.0,
                       "retardance_n": 0.40}),
            ("kirpich", {"flow_length_ft": 2000, "elevation_diff_ft": 40}),
        ])

        expected = seg1.tc_minutes + seg2.tc_minutes
        assert result == pytest.approx(expected)

    def test_three_segments(self):
        seg1 = TimeOfConcentration.kerby(
            flow_length_ft=200, slope_percent=3.0, retardance_n=0.20
        )
        seg2 = TimeOfConcentration.kirpich(
            flow_length_ft=1500, elevation_diff_ft=30
        )
        seg3 = TimeOfConcentration.nrcs_lag(
            flow_length_ft=3000, slope_percent=2.0, curve_number=80
        )

        result = TimeOfConcentration.composite([
            ("kerby", {"flow_length_ft": 200, "slope_percent": 3.0,
                       "retardance_n": 0.20}),
            ("kirpich", {"flow_length_ft": 1500, "elevation_diff_ft": 30}),
            ("nrcs_lag", {"flow_length_ft": 3000, "slope_percent": 2.0,
                          "curve_number": 80}),
        ])

        expected = seg1.tc_minutes + seg2.tc_minutes + seg3.tc_minutes
        assert result == pytest.approx(expected)

    def test_empty_segments_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            TimeOfConcentration.composite([])
        assert exc_info.value.parameter == "segments"

    def test_unknown_method_raises(self):
        with pytest.raises(CalculatorInputError) as exc_info:
            TimeOfConcentration.composite([
                ("unknown_method", {"flow_length_ft": 1000}),
            ])
        assert "unknown_method" in str(exc_info.value)

    def test_invalid_segment_params_raises(self):
        with pytest.raises(CalculatorInputError):
            TimeOfConcentration.composite([
                ("kirpich", {"flow_length_ft": 0, "elevation_diff_ft": 50}),
            ])


class TestTimeOfConcentrationUnits:
    """Verify all methods return MINUTES as documented."""

    def test_kirpich_returns_minutes(self):
        result = TimeOfConcentration.kirpich(
            flow_length_ft=10000,
            elevation_diff_ft=100,
        )
        assert result.tc_minutes < 120
        assert result.tc_minutes > 5

    def test_kerby_returns_minutes(self):
        result = TimeOfConcentration.kerby(
            flow_length_ft=500,
            slope_percent=1.0,
            retardance_n=0.40,
        )
        assert result.tc_minutes < 60
        assert result.tc_minutes > 1

    def test_nrcs_lag_returns_minutes(self):
        result = TimeOfConcentration.nrcs_lag(
            flow_length_ft=5000,
            slope_percent=2.0,
            curve_number=70,
        )
        assert result.tc_minutes < 120
        assert result.tc_minutes > 5
