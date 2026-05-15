"""Hydrology calculation engine for Civil Toolbox.

This module provides calculators for hydrology and drainage analysis:

- RationalMethod: Peak runoff rate (Q = C × i × A)
- TR55: Runoff depth using SCS curve number method
- TimeOfConcentration: Travel time using Kirpich, Kerby, NRCS lag methods
- KinematicWave: Sheet flow travel time

Unit Conventions:
    - TimeOfConcentration methods return time in MINUTES
    - KinematicWave.sheet_flow_time() returns time in HOURS
    - US customary units are primary (feet, inches, acres, cfs)
    - Metric convenience methods are available where applicable
"""

from civil_toolbox.calculators.validation import (
    CalculatorInputError,
    validate_positive,
    validate_non_negative,
    validate_range,
    validate_runoff_coefficient,
    validate_curve_number,
    validate_slope_percent,
    validate_mannings_n,
)

from civil_toolbox.calculators.rational_method import (
    RationalMethod,
    RationalMethodResult,
    RationalMethodResultMetric,
)

from civil_toolbox.calculators.tr55 import (
    TR55,
    TR55RunoffResult,
)

from civil_toolbox.calculators.time_of_concentration import (
    TimeOfConcentration,
    TimeOfConcentrationResult,
)

from civil_toolbox.calculators.kinematic_wave import (
    KinematicWave,
    SheetFlowResult,
)

__all__ = [
    # Validation
    "CalculatorInputError",
    "validate_positive",
    "validate_non_negative",
    "validate_range",
    "validate_runoff_coefficient",
    "validate_curve_number",
    "validate_slope_percent",
    "validate_mannings_n",
    # Rational Method
    "RationalMethod",
    "RationalMethodResult",
    "RationalMethodResultMetric",
    # TR-55
    "TR55",
    "TR55RunoffResult",
    # Time of Concentration
    "TimeOfConcentration",
    "TimeOfConcentrationResult",
    # Kinematic Wave
    "KinematicWave",
    "SheetFlowResult",
]
