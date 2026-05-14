"""Kinematic wave sheet flow time calculator.

The kinematic wave equation estimates travel time for sheet flow over
land surfaces. Sheet flow is shallow, unconcentrated flow over plane
surfaces, typically limited to the first 300 feet of the longest flow
path.

IMPORTANT: This method returns time in HOURS, not minutes.
This differs from TimeOfConcentration methods which return minutes.

Formula:
    Tt = (0.007 × (n × L)^0.8) / (P2^0.5 × S^0.4)

Where:
    Tt = travel time (hours)
    n = Manning's roughness coefficient
    L = flow length (feet), recommend ≤ 300 ft
    P2 = 2-year, 24-hour rainfall depth (inches)
    S = slope (ft/ft)

Typical Manning's n values for sheet flow:
    0.011 - Smooth surfaces (concrete, asphalt)
    0.05  - Fallow (no residue)
    0.06  - Cultivated (with residue)
    0.13  - Grass (short prairie)
    0.24  - Grass (dense)
    0.40  - Woods (light underbrush)
    0.80  - Woods (dense underbrush)
"""

from dataclasses import dataclass

from civil_toolbox.calculators.validation import (
    CalculatorInputError,
    validate_positive,
    validate_mannings_n,
)


@dataclass
class SheetFlowResult:
    """Result from kinematic wave sheet flow calculation."""

    travel_time_hours: float
    flow_length_ft: float
    slope_percent: float
    mannings_n: float
    rainfall_2yr_24hr_in: float


class KinematicWave:
    """Kinematic wave sheet flow calculator.

    Stateless calculator with static methods for computing sheet flow
    travel time using the kinematic wave equation.

    IMPORTANT: Returns time in HOURS, not minutes.
    """

    MAX_RECOMMENDED_LENGTH_FT = 300.0

    @staticmethod
    def sheet_flow_time(
        flow_length_ft: float,
        slope_percent: float,
        mannings_n: float,
        rainfall_2yr_24hr_in: float,
    ) -> SheetFlowResult:
        """Calculate sheet flow travel time using kinematic wave equation.

        IMPORTANT: Returns time in HOURS, not minutes.

        Formula:
            Tt = (0.007 × (n × L)^0.8) / (P2^0.5 × S^0.4)

        Args:
            flow_length_ft: Sheet flow length in feet (recommend ≤ 300 ft)
            slope_percent: Land slope as percentage
            mannings_n: Manning's roughness coefficient
            rainfall_2yr_24hr_in: 2-year, 24-hour rainfall depth in inches

        Returns:
            SheetFlowResult with travel time in HOURS

        Raises:
            CalculatorInputError: If any input is invalid
        """
        validate_positive(flow_length_ft, "flow_length_ft")
        validate_positive(slope_percent, "slope_percent")
        validate_mannings_n(mannings_n)
        validate_positive(rainfall_2yr_24hr_in, "rainfall_2yr_24hr_in")

        slope_ft_per_ft = slope_percent / 100.0

        numerator = 0.007 * ((mannings_n * flow_length_ft) ** 0.8)
        denominator = (rainfall_2yr_24hr_in ** 0.5) * (slope_ft_per_ft ** 0.4)

        travel_time_hours = numerator / denominator

        return SheetFlowResult(
            travel_time_hours=travel_time_hours,
            flow_length_ft=flow_length_ft,
            slope_percent=slope_percent,
            mannings_n=mannings_n,
            rainfall_2yr_24hr_in=rainfall_2yr_24hr_in,
        )

    @staticmethod
    def sheet_flow_time_minutes(
        flow_length_ft: float,
        slope_percent: float,
        mannings_n: float,
        rainfall_2yr_24hr_in: float,
    ) -> float:
        """Calculate sheet flow travel time in minutes.

        Convenience method that converts the result to minutes.

        Args:
            flow_length_ft: Sheet flow length in feet (recommend ≤ 300 ft)
            slope_percent: Land slope as percentage
            mannings_n: Manning's roughness coefficient
            rainfall_2yr_24hr_in: 2-year, 24-hour rainfall depth in inches

        Returns:
            Travel time in minutes

        Raises:
            CalculatorInputError: If any input is invalid
        """
        result = KinematicWave.sheet_flow_time(
            flow_length_ft=flow_length_ft,
            slope_percent=slope_percent,
            mannings_n=mannings_n,
            rainfall_2yr_24hr_in=rainfall_2yr_24hr_in,
        )
        return result.travel_time_hours * 60.0

    @staticmethod
    def is_length_recommended(flow_length_ft: float) -> bool:
        """Check if flow length is within recommended limits.

        Sheet flow is typically limited to the first 300 feet of a flow
        path. Beyond this distance, flow usually concentrates.

        Args:
            flow_length_ft: Flow length to check

        Returns:
            True if length is ≤ 300 feet, False otherwise
        """
        return flow_length_ft <= KinematicWave.MAX_RECOMMENDED_LENGTH_FT
