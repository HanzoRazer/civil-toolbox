"""Rational Method runoff calculator (Q = C × i × A).

The Rational Method estimates peak runoff rate for small drainage areas.
It is most accurate for areas less than 200 acres (80 hectares).

Formula (US customary units):
    Q = C × i × A

Where:
    Q = peak runoff rate (cfs)
    C = runoff coefficient (dimensionless, 0 < C <= 1)
    i = rainfall intensity (inches/hour)
    A = drainage area (acres)

Formula (SI units):
    Q = C × i × A / 360

Where:
    Q = peak runoff rate (m³/s)
    i = rainfall intensity (mm/hour)
    A = drainage area (hectares)
"""

from dataclasses import dataclass
from typing import Optional

from civil_toolbox.calculators.validation import (
    CalculatorInputError,
    validate_positive,
    validate_runoff_coefficient,
)


@dataclass
class RationalMethodResult:
    """Result from Rational Method calculation."""

    peak_runoff_cfs: float
    runoff_coefficient: float
    rainfall_intensity_in_per_hr: float
    area_acres: float


@dataclass
class RationalMethodResultMetric:
    """Result from Rational Method calculation (metric units)."""

    peak_runoff_m3_per_s: float
    runoff_coefficient: float
    rainfall_intensity_mm_per_hr: float
    area_hectares: float


class RationalMethod:
    """Rational Method peak runoff calculator.

    Stateless calculator with static methods for computing peak runoff
    using the Rational Method formula.
    """

    @staticmethod
    def calculate(
        runoff_coefficient: float,
        rainfall_intensity_in_per_hr: float,
        area_acres: float,
    ) -> RationalMethodResult:
        """Calculate peak runoff rate using the Rational Method.

        Args:
            runoff_coefficient: Dimensionless C value (0 < C <= 1)
            rainfall_intensity_in_per_hr: Rainfall intensity in inches/hour
            area_acres: Drainage area in acres

        Returns:
            RationalMethodResult with peak runoff in cfs

        Raises:
            CalculatorInputError: If any input is invalid
        """
        validate_runoff_coefficient(runoff_coefficient)
        validate_positive(rainfall_intensity_in_per_hr, "rainfall_intensity_in_per_hr")
        validate_positive(area_acres, "area_acres")

        peak_runoff_cfs = runoff_coefficient * rainfall_intensity_in_per_hr * area_acres

        return RationalMethodResult(
            peak_runoff_cfs=peak_runoff_cfs,
            runoff_coefficient=runoff_coefficient,
            rainfall_intensity_in_per_hr=rainfall_intensity_in_per_hr,
            area_acres=area_acres,
        )

    @staticmethod
    def calculate_metric(
        runoff_coefficient: float,
        rainfall_intensity_mm_per_hr: float,
        area_hectares: float,
    ) -> RationalMethodResultMetric:
        """Calculate peak runoff rate using the Rational Method (metric).

        Args:
            runoff_coefficient: Dimensionless C value (0 < C <= 1)
            rainfall_intensity_mm_per_hr: Rainfall intensity in mm/hour
            area_hectares: Drainage area in hectares

        Returns:
            RationalMethodResultMetric with peak runoff in m³/s

        Raises:
            CalculatorInputError: If any input is invalid
        """
        validate_runoff_coefficient(runoff_coefficient)
        validate_positive(rainfall_intensity_mm_per_hr, "rainfall_intensity_mm_per_hr")
        validate_positive(area_hectares, "area_hectares")

        peak_runoff_m3_per_s = (
            runoff_coefficient * rainfall_intensity_mm_per_hr * area_hectares / 360.0
        )

        return RationalMethodResultMetric(
            peak_runoff_m3_per_s=peak_runoff_m3_per_s,
            runoff_coefficient=runoff_coefficient,
            rainfall_intensity_mm_per_hr=rainfall_intensity_mm_per_hr,
            area_hectares=area_hectares,
        )

    @staticmethod
    def calculate_composite(
        sub_areas: list[tuple[float, float]],
        rainfall_intensity_in_per_hr: float,
    ) -> RationalMethodResult:
        """Calculate peak runoff for a composite drainage area.

        Computes area-weighted runoff coefficient from multiple sub-areas
        with different land uses.

        Args:
            sub_areas: List of (runoff_coefficient, area_acres) tuples
            rainfall_intensity_in_per_hr: Rainfall intensity in inches/hour

        Returns:
            RationalMethodResult with peak runoff in cfs

        Raises:
            CalculatorInputError: If any input is invalid
        """
        if not sub_areas:
            raise CalculatorInputError(
                "At least one sub-area required",
                parameter="sub_areas",
            )

        validate_positive(rainfall_intensity_in_per_hr, "rainfall_intensity_in_per_hr")

        total_area = 0.0
        weighted_c_sum = 0.0

        for i, (c, area) in enumerate(sub_areas):
            validate_runoff_coefficient(c)
            validate_positive(area, f"sub_areas[{i}].area")
            total_area += area
            weighted_c_sum += c * area

        composite_c = weighted_c_sum / total_area
        peak_runoff_cfs = composite_c * rainfall_intensity_in_per_hr * total_area

        return RationalMethodResult(
            peak_runoff_cfs=peak_runoff_cfs,
            runoff_coefficient=composite_c,
            rainfall_intensity_in_per_hr=rainfall_intensity_in_per_hr,
            area_acres=total_area,
        )
