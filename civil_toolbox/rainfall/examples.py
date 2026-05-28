"""Example IDF curves for testing and documentation.

These are SYNTHETIC data for demonstration purposes only.
Do not use for engineering design or permitting.
"""

from civil_toolbox.rainfall.idf import IDFCurve, IDFPoint


def create_example_idf_curve() -> IDFCurve:
    """Create a synthetic example IDF curve.

    This curve is for TESTING AND DEMONSTRATION ONLY.
    It does not represent actual rainfall data for any location.

    Returns:
        IDFCurve with synthetic data for multiple return periods
        and durations.

    Example:
        >>> curve = create_example_idf_curve()
        >>> intensity = curve.lookup_intensity(
        ...     return_period_years=10,
        ...     duration_minutes=15,
        ... )
        >>> print(f"10-year 15-min intensity: {intensity:.2f} in/hr")
    """
    points = []

    idf_data = {
        2: {5: 4.1, 10: 3.5, 15: 3.0, 30: 2.2, 60: 1.5, 120: 0.9, 360: 0.4, 1440: 0.15},
        5: {5: 5.0, 10: 4.2, 15: 3.6, 30: 2.7, 60: 1.8, 120: 1.1, 360: 0.5, 1440: 0.19},
        10: {5: 5.8, 10: 4.9, 15: 4.2, 30: 3.1, 60: 2.1, 120: 1.3, 360: 0.6, 1440: 0.22},
        25: {5: 6.8, 10: 5.7, 15: 4.9, 30: 3.6, 60: 2.5, 120: 1.5, 360: 0.7, 1440: 0.26},
        50: {5: 7.6, 10: 6.4, 15: 5.5, 30: 4.0, 60: 2.8, 120: 1.7, 360: 0.8, 1440: 0.29},
        100: {5: 8.5, 10: 7.1, 15: 6.1, 30: 4.5, 60: 3.1, 120: 1.9, 360: 0.9, 1440: 0.33},
    }

    for return_period, durations in idf_data.items():
        for duration_minutes, intensity in durations.items():
            points.append(
                IDFPoint(
                    return_period_years=return_period,
                    duration_minutes=float(duration_minutes),
                    rainfall_intensity_in_per_hr=intensity,
                )
            )

    return IDFCurve(
        id="example-synthetic",
        name="Example Synthetic IDF Curve",
        source="Civil Toolbox Demo Data",
        location="Synthetic (No Real Location)",
        points=points,
        metadata={
            "synthetic": True,
            "for_testing_only": True,
            "warning": "This data is for demonstration purposes only. "
            "Do not use for engineering design or permitting.",
        },
    )
