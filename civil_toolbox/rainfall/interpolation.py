"""Interpolation utilities for IDF curve lookups.

Provides deterministic linear interpolation within known data ranges.
No extrapolation is performed.
"""

from civil_toolbox.rainfall.errors import IDFInterpolationError


def linear_interpolate(
    x: float,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
) -> float:
    """Perform linear interpolation between two points.

    Args:
        x: The x value to interpolate at.
        x0: Lower x bound.
        y0: Value at x0.
        x1: Upper x bound.
        y1: Value at x1.

    Returns:
        Interpolated y value at x.

    Raises:
        IDFInterpolationError: If x0 == x1 (cannot interpolate).
    """
    if x0 == x1:
        if x == x0:
            return y0
        raise IDFInterpolationError(
            f"Cannot interpolate: x0 and x1 are equal ({x0})"
        )

    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)


def interpolate_from_points(
    x: float,
    points: dict[float, float],
) -> float:
    """Interpolate a value from a dictionary of points.

    Args:
        x: The x value to look up or interpolate.
        points: Dictionary mapping x values to y values.

    Returns:
        The exact or interpolated y value.

    Raises:
        IDFInterpolationError: If x is outside the range of points,
            or if points is empty or has insufficient data.
    """
    if not points:
        raise IDFInterpolationError("Cannot interpolate: no points provided")

    sorted_xs = sorted(points.keys())

    if x in points:
        return points[x]

    if len(sorted_xs) == 1:
        raise IDFInterpolationError(
            f"Cannot interpolate: only one point available ({sorted_xs[0]}), "
            f"requested {x}"
        )

    min_x = sorted_xs[0]
    max_x = sorted_xs[-1]

    if x < min_x:
        raise IDFInterpolationError(
            f"Cannot interpolate: {x} is below available range [{min_x}, {max_x}]"
        )

    if x > max_x:
        raise IDFInterpolationError(
            f"Cannot interpolate: {x} is above available range [{min_x}, {max_x}]"
        )

    x0 = None
    x1 = None
    for i, xi in enumerate(sorted_xs):
        if xi > x:
            x0 = sorted_xs[i - 1]
            x1 = xi
            break

    if x0 is None or x1 is None:
        raise IDFInterpolationError(
            f"Cannot find interpolation bounds for {x}"
        )

    return linear_interpolate(x, x0, points[x0], x1, points[x1])
