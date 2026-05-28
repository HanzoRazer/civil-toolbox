"""Rainfall IDF curve support for Civil Toolbox.

This module provides structured IDF (Intensity-Duration-Frequency) curve data
for looking up rainfall intensity and generating design storm events.

Two main capabilities:

1. **IDF Lookup** — Get rainfall intensity or depth for a given return period
   and duration, with optional duration interpolation.

2. **StormEvent Generation** — Create domain StormEvent objects from IDF data
   for use with calculators and adapters.

Example:
    >>> from civil_toolbox.rainfall import IDFCurve, IDFPoint
    >>> curve = IDFCurve(
    ...     id="example",
    ...     name="Example IDF Curve",
    ...     points=[
    ...         IDFPoint(return_period_years=10, duration_minutes=15, rainfall_intensity_in_per_hr=4.5),
    ...         IDFPoint(return_period_years=100, duration_minutes=15, rainfall_intensity_in_per_hr=7.2),
    ...     ],
    ... )
    >>> intensity = curve.lookup_intensity(return_period_years=10, duration_minutes=15)
    >>> print(f"Intensity: {intensity:.2f} in/hr")

Example (storm generation):
    >>> storm = curve.to_storm_event(return_period_years=100, duration_minutes=15)
    >>> print(f"{storm.name}: {storm.rainfall_intensity_in_per_hr:.2f} in/hr")
"""

from civil_toolbox.rainfall.idf import IDFPoint, IDFCurve
from civil_toolbox.rainfall.examples import create_example_idf_curve
from civil_toolbox.rainfall.errors import (
    RainfallDataError,
    InvalidIDFDataError,
    IDFLookupError,
    IDFInterpolationError,
)

__all__ = [
    # Models
    "IDFPoint",
    "IDFCurve",
    # Examples
    "create_example_idf_curve",
    # Errors
    "RainfallDataError",
    "InvalidIDFDataError",
    "IDFLookupError",
    "IDFInterpolationError",
]
