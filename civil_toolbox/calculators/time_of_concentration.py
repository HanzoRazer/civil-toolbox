"""Time of concentration calculators (Kirpich, Kerby, NRCS lag).

Time of concentration (Tc) is the time required for runoff to travel from
the most hydraulically distant point in the watershed to the outlet.

ALL METHODS IN THIS MODULE RETURN TIME IN MINUTES.

Methods:
- Kirpich: empirical formula for small rural watersheds (< 200 acres)
- Kerby: overland flow for small watersheds (< 10 acres, slopes < 1%)
- NRCS lag: relates lag time to time of concentration via Tc = Tlag / 0.6
"""

import math
from dataclasses import dataclass
from typing import Optional

from civil_toolbox.calculators.validation import (
    CalculatorInputError,
    validate_positive,
    validate_curve_number,
    validate_mannings_n,
)


@dataclass
class TimeOfConcentrationResult:
    """Result from time of concentration calculation."""

    tc_minutes: float
    method: str
    flow_length_ft: float
    slope_percent: float


class TimeOfConcentration:
    """Time of concentration calculator.

    Stateless calculator with static methods for computing time of
    concentration using various empirical methods.

    All methods return time in MINUTES.
    """

    @staticmethod
    def kirpich(
        flow_length_ft: float,
        elevation_diff_ft: float,
    ) -> TimeOfConcentrationResult:
        """Calculate Tc using the Kirpich formula.

        Best for: small rural watersheds (< 200 acres), natural channels.

        Formula:
            Tc = 0.0078 × L^0.77 × S^(-0.385)

        Where:
            L = flow length in feet
            S = average slope (ft/ft)

        Args:
            flow_length_ft: Flow path length in feet
            elevation_diff_ft: Elevation difference along flow path in feet

        Returns:
            TimeOfConcentrationResult with Tc in minutes

        Raises:
            CalculatorInputError: If inputs are invalid
        """
        validate_positive(flow_length_ft, "flow_length_ft")
        validate_positive(elevation_diff_ft, "elevation_diff_ft")

        slope_ft_per_ft = elevation_diff_ft / flow_length_ft
        slope_percent = slope_ft_per_ft * 100

        tc_minutes = 0.0078 * (flow_length_ft ** 0.77) * (slope_ft_per_ft ** -0.385)

        return TimeOfConcentrationResult(
            tc_minutes=tc_minutes,
            method="kirpich",
            flow_length_ft=flow_length_ft,
            slope_percent=slope_percent,
        )

    @staticmethod
    def kerby(
        flow_length_ft: float,
        slope_percent: float,
        retardance_n: float,
    ) -> TimeOfConcentrationResult:
        """Calculate Tc using the Kerby formula.

        Best for: overland flow on small watersheds (< 10 acres),
        mild slopes (< 1%), and flow lengths < 1000 feet.

        Formula:
            Tc = 0.83 × (L × n)^0.467 × S^(-0.235)

        Where:
            L = flow length in feet
            n = Kerby retardance coefficient (similar to Manning's n)
            S = slope (ft/ft)

        Typical retardance values:
            0.02 - Smooth pavement
            0.10 - Bare soil
            0.20 - Poor grass
            0.40 - Dense grass
            0.80 - Dense forest

        Args:
            flow_length_ft: Flow path length in feet (recommend < 1000 ft)
            slope_percent: Average slope as percentage
            retardance_n: Kerby retardance coefficient

        Returns:
            TimeOfConcentrationResult with Tc in minutes

        Raises:
            CalculatorInputError: If inputs are invalid
        """
        validate_positive(flow_length_ft, "flow_length_ft")
        validate_positive(slope_percent, "slope_percent")
        validate_positive(retardance_n, "retardance_n")

        if retardance_n > 1.0:
            raise CalculatorInputError(
                f"retardance_n is unusually high (> 1.0), got {retardance_n}. "
                f"Typical values are 0.02-0.80.",
                parameter="retardance_n",
            )

        slope_ft_per_ft = slope_percent / 100.0

        tc_minutes = (
            0.83
            * ((flow_length_ft * retardance_n) ** 0.467)
            * (slope_ft_per_ft ** -0.235)
        )

        return TimeOfConcentrationResult(
            tc_minutes=tc_minutes,
            method="kerby",
            flow_length_ft=flow_length_ft,
            slope_percent=slope_percent,
        )

    @staticmethod
    def nrcs_lag(
        flow_length_ft: float,
        slope_percent: float,
        curve_number: float,
    ) -> TimeOfConcentrationResult:
        """Calculate Tc using the NRCS lag method.

        This method calculates lag time and converts to Tc using Tc = Tlag / 0.6.

        Formula:
            Tlag = L^0.8 × (S + 1)^0.7 / (1900 × √Y)
            Tc = Tlag / 0.6

        Where:
            L = flow length in feet
            S = potential maximum retention = (1000/CN) - 10
            Y = average watershed slope (%)

        Args:
            flow_length_ft: Flow path length in feet
            slope_percent: Average watershed slope as percentage
            curve_number: SCS curve number (0 < CN <= 100)

        Returns:
            TimeOfConcentrationResult with Tc in minutes

        Raises:
            CalculatorInputError: If inputs are invalid
        """
        validate_positive(flow_length_ft, "flow_length_ft")
        validate_positive(slope_percent, "slope_percent")
        validate_curve_number(curve_number)

        s = (1000.0 / curve_number) - 10.0

        tlag_hr = (
            (flow_length_ft ** 0.8)
            * ((s + 1) ** 0.7)
            / (1900.0 * math.sqrt(slope_percent))
        )

        tc_hr = tlag_hr / 0.6
        tc_minutes = tc_hr * 60.0

        return TimeOfConcentrationResult(
            tc_minutes=tc_minutes,
            method="nrcs_lag",
            flow_length_ft=flow_length_ft,
            slope_percent=slope_percent,
        )

    @staticmethod
    def composite(
        segments: list[tuple[str, dict]],
    ) -> float:
        """Calculate composite Tc by summing segment travel times.

        For flow paths with multiple segments (e.g., sheet flow, shallow
        concentrated flow, channel flow), calculate Tc for each segment
        and sum them.

        Args:
            segments: List of (method_name, kwargs) tuples. Each tuple
                     specifies a method and its parameters.

        Returns:
            Total time of concentration in minutes

        Raises:
            CalculatorInputError: If any segment calculation fails

        Example:
            tc = TimeOfConcentration.composite([
                ("kerby", {"flow_length_ft": 300, "slope_percent": 2.0,
                          "retardance_n": 0.40}),
                ("kirpich", {"flow_length_ft": 2000, "elevation_diff_ft": 40}),
            ])
        """
        if not segments:
            raise CalculatorInputError(
                "At least one segment required",
                parameter="segments",
            )

        methods = {
            "kirpich": TimeOfConcentration.kirpich,
            "kerby": TimeOfConcentration.kerby,
            "nrcs_lag": TimeOfConcentration.nrcs_lag,
        }

        total_tc_minutes = 0.0

        for i, (method_name, kwargs) in enumerate(segments):
            if method_name not in methods:
                raise CalculatorInputError(
                    f"Unknown method '{method_name}' in segment {i}. "
                    f"Available methods: {list(methods.keys())}",
                    parameter=f"segments[{i}]",
                )
            result = methods[method_name](**kwargs)
            total_tc_minutes += result.tc_minutes

        return total_tc_minutes
