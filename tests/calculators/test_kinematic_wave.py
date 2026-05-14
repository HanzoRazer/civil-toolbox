"""Tests for kinematic wave sheet flow calculator."""

import pytest

from civil_toolbox.calculators.kinematic_wave import (
    KinematicWave,
    SheetFlowResult,
)
from civil_toolbox.calculators.validation import CalculatorInputError


class TestSheetFlowTime:
    """Tests for KinematicWave.sheet_flow_time."""

    def test_returns_hours(self):
        result = KinematicWave.sheet_flow_time(
            flow_length_ft=100,
            slope_percent=2.0,
            mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5,
        )
        assert result.travel_time_hours > 0
        assert result.travel_time_hours < 1.0

    def test_returns_result_dataclass(self):
        result = KinematicWave.sheet_flow_time(
            flow_length_ft=100,
            slope_percent=2.0,
            mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5,
        )
        assert isinstance(result, SheetFlowResult)
        assert result.flow_length_ft == 100
        assert result.slope_percent == 2.0
        assert result.mannings_n == 0.15
        assert result.rainfall_2yr_24hr_in == 3.5

    def test_longer_path_more_time(self):
        short = KinematicWave.sheet_flow_time(
            flow_length_ft=50, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        long = KinematicWave.sheet_flow_time(
            flow_length_ft=200, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        assert long.travel_time_hours > short.travel_time_hours

    def test_rougher_surface_more_time(self):
        smooth = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.011,
            rainfall_2yr_24hr_in=3.5
        )
        rough = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.40,
            rainfall_2yr_24hr_in=3.5
        )
        assert rough.travel_time_hours > smooth.travel_time_hours

    def test_steeper_slope_less_time(self):
        gentle = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=0.5, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        steep = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=5.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        assert steep.travel_time_hours < gentle.travel_time_hours

    def test_more_rainfall_less_time(self):
        light = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=2.0
        )
        heavy = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=5.0
        )
        assert heavy.travel_time_hours < light.travel_time_hours

    def test_known_value(self):
        result = KinematicWave.sheet_flow_time(
            flow_length_ft=100,
            slope_percent=2.0,
            mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5,
        )
        slope_ft_per_ft = 0.02
        numerator = 0.007 * ((0.15 * 100) ** 0.8)
        denominator = (3.5 ** 0.5) * (slope_ft_per_ft ** 0.4)
        expected = numerator / denominator
        assert result.travel_time_hours == pytest.approx(expected)

    def test_invalid_length_raises(self):
        with pytest.raises(CalculatorInputError):
            KinematicWave.sheet_flow_time(
                flow_length_ft=0, slope_percent=2.0, mannings_n=0.15,
                rainfall_2yr_24hr_in=3.5
            )

    def test_invalid_slope_raises(self):
        with pytest.raises(CalculatorInputError):
            KinematicWave.sheet_flow_time(
                flow_length_ft=100, slope_percent=0, mannings_n=0.15,
                rainfall_2yr_24hr_in=3.5
            )

    def test_invalid_mannings_raises(self):
        with pytest.raises(CalculatorInputError):
            KinematicWave.sheet_flow_time(
                flow_length_ft=100, slope_percent=2.0, mannings_n=0,
                rainfall_2yr_24hr_in=3.5
            )

    def test_invalid_rainfall_raises(self):
        with pytest.raises(CalculatorInputError):
            KinematicWave.sheet_flow_time(
                flow_length_ft=100, slope_percent=2.0, mannings_n=0.15,
                rainfall_2yr_24hr_in=0
            )


class TestSheetFlowTimeMinutes:
    """Tests for KinematicWave.sheet_flow_time_minutes."""

    def test_returns_minutes(self):
        hours_result = KinematicWave.sheet_flow_time(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        minutes_result = KinematicWave.sheet_flow_time_minutes(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        assert minutes_result == pytest.approx(hours_result.travel_time_hours * 60)

    def test_reasonable_value(self):
        minutes = KinematicWave.sheet_flow_time_minutes(
            flow_length_ft=100, slope_percent=2.0, mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5
        )
        assert minutes > 1
        assert minutes < 60


class TestIsLengthRecommended:
    """Tests for KinematicWave.is_length_recommended."""

    def test_below_limit_is_recommended(self):
        assert KinematicWave.is_length_recommended(100) is True
        assert KinematicWave.is_length_recommended(299) is True

    def test_at_limit_is_recommended(self):
        assert KinematicWave.is_length_recommended(300) is True

    def test_above_limit_not_recommended(self):
        assert KinematicWave.is_length_recommended(301) is False
        assert KinematicWave.is_length_recommended(500) is False


class TestKinematicWaveUnits:
    """Verify sheet_flow_time returns HOURS as documented."""

    def test_returns_hours_not_minutes(self):
        result = KinematicWave.sheet_flow_time(
            flow_length_ft=300,
            slope_percent=1.0,
            mannings_n=0.40,
            rainfall_2yr_24hr_in=2.5,
        )
        assert result.travel_time_hours < 2.0
        assert result.travel_time_hours > 0.05

    def test_typical_case_is_fraction_of_hour(self):
        result = KinematicWave.sheet_flow_time(
            flow_length_ft=100,
            slope_percent=2.0,
            mannings_n=0.15,
            rainfall_2yr_24hr_in=3.5,
        )
        assert result.travel_time_hours < 1.0
