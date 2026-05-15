"""TR-55 runoff depth and curve number calculators.

TR-55 is the USDA Natural Resources Conservation Service (NRCS) method
for estimating runoff depth from rainfall events. It uses the SCS
Curve Number method.

Key formulas:
    S = (1000 / CN) - 10           Potential maximum retention (inches)
    Ia = 0.2 × S                   Initial abstraction (inches)
    Q = (P - Ia)² / (P - Ia + S)   Runoff depth (inches), if P > Ia
    Q = 0                          Runoff depth (inches), if P <= Ia

Where:
    Q = runoff depth (inches)
    P = rainfall depth (inches)
    CN = curve number (0-100)
    S = potential maximum retention after runoff begins (inches)
    Ia = initial abstraction (inches)
"""

from dataclasses import dataclass
from typing import Optional

from civil_toolbox.calculators.validation import (
    CalculatorInputError,
    validate_positive,
    validate_non_negative,
    validate_curve_number,
)


@dataclass
class TR55RunoffResult:
    """Result from TR-55 runoff depth calculation."""

    runoff_depth_in: float
    rainfall_depth_in: float
    curve_number: float
    potential_retention_in: float
    initial_abstraction_in: float


class TR55:
    """TR-55 runoff depth calculator.

    Stateless calculator with static methods for computing runoff depth
    using the NRCS curve number method.
    """

    DEFAULT_IA_RATIO = 0.2

    @staticmethod
    def potential_retention(curve_number: float) -> float:
        """Calculate potential maximum retention S from curve number.

        Args:
            curve_number: SCS curve number (0 < CN <= 100)

        Returns:
            Potential maximum retention in inches

        Raises:
            CalculatorInputError: If curve number is invalid
        """
        validate_curve_number(curve_number)
        return (1000.0 / curve_number) - 10.0

    @staticmethod
    def initial_abstraction(
        potential_retention_in: float,
        ia_ratio: float = 0.2,
    ) -> float:
        """Calculate initial abstraction from potential retention.

        Args:
            potential_retention_in: S value in inches
            ia_ratio: Ia/S ratio (default 0.2, NRCS standard)

        Returns:
            Initial abstraction in inches

        Raises:
            CalculatorInputError: If inputs are invalid
        """
        validate_non_negative(potential_retention_in, "potential_retention_in")
        if ia_ratio < 0 or ia_ratio > 1:
            raise CalculatorInputError(
                f"ia_ratio must be between 0 and 1, got {ia_ratio}",
                parameter="ia_ratio",
            )
        return ia_ratio * potential_retention_in

    @staticmethod
    def runoff_depth(
        rainfall_depth_in: float,
        curve_number: float,
        ia_ratio: float = 0.2,
    ) -> TR55RunoffResult:
        """Calculate runoff depth using the SCS curve number method.

        Args:
            rainfall_depth_in: Total rainfall depth in inches
            curve_number: SCS curve number (0 < CN <= 100)
            ia_ratio: Ia/S ratio (default 0.2, NRCS standard)

        Returns:
            TR55RunoffResult with runoff depth and intermediate values

        Raises:
            CalculatorInputError: If any input is invalid
        """
        validate_non_negative(rainfall_depth_in, "rainfall_depth_in")
        validate_curve_number(curve_number)

        s = TR55.potential_retention(curve_number)
        ia = TR55.initial_abstraction(s, ia_ratio)

        if rainfall_depth_in <= ia:
            runoff = 0.0
        else:
            p_minus_ia = rainfall_depth_in - ia
            runoff = (p_minus_ia ** 2) / (p_minus_ia + s)

        return TR55RunoffResult(
            runoff_depth_in=runoff,
            rainfall_depth_in=rainfall_depth_in,
            curve_number=curve_number,
            potential_retention_in=s,
            initial_abstraction_in=ia,
        )

    @staticmethod
    def weighted_curve_number(
        sub_areas: list[tuple[float, float]],
    ) -> float:
        """Calculate area-weighted curve number for composite drainage area.

        Args:
            sub_areas: List of (curve_number, area_acres) tuples

        Returns:
            Area-weighted curve number

        Raises:
            CalculatorInputError: If any input is invalid
        """
        if not sub_areas:
            raise CalculatorInputError(
                "At least one sub-area required",
                parameter="sub_areas",
            )

        total_area = 0.0
        weighted_cn_sum = 0.0

        for i, (cn, area) in enumerate(sub_areas):
            validate_curve_number(cn)
            validate_positive(area, f"sub_areas[{i}].area")
            total_area += area
            weighted_cn_sum += cn * area

        return weighted_cn_sum / total_area

    @staticmethod
    def runoff_depth_metric(
        rainfall_depth_mm: float,
        curve_number: float,
        ia_ratio: float = 0.2,
    ) -> float:
        """Calculate runoff depth in millimeters.

        Convenience method that converts to inches, calculates, and converts back.

        Args:
            rainfall_depth_mm: Total rainfall depth in millimeters
            curve_number: SCS curve number (0 < CN <= 100)
            ia_ratio: Ia/S ratio (default 0.2, NRCS standard)

        Returns:
            Runoff depth in millimeters

        Raises:
            CalculatorInputError: If any input is invalid
        """
        rainfall_in = rainfall_depth_mm / 25.4
        result = TR55.runoff_depth(rainfall_in, curve_number, ia_ratio)
        return result.runoff_depth_in * 25.4
