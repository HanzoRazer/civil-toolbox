"""Unit definitions and conversion helpers for Civil Toolbox.

This module defines standard unit strings used throughout the domain model.
Unit-explicit field names (e.g., area_acres, length_ft) are preferred over
generic names with separate unit fields.
"""

# Area units
ACRES = "acre"
SQUARE_FEET = "ft^2"
SQUARE_METERS = "m^2"

# Length units
FEET = "ft"
INCHES = "in"
METERS = "m"

# Slope units
FEET_PER_FOOT = "ft/ft"
PERCENT = "%"

# Flow rate units
CFS = "cfs"
GPM = "gpm"
CMS = "m^3/s"

# Rainfall units
INCHES_PER_HOUR = "in/hr"
MM_PER_HOUR = "mm/hr"

# Time units
MINUTES = "min"
HOURS = "hr"
SECONDS = "s"

# Volume units
CUBIC_FEET = "ft^3"
ACRE_FEET = "ac-ft"
CUBIC_METERS = "m^3"

# Dimensionless
DIMENSIONLESS = "dimensionless"


# Conversion factors
ACRES_TO_SQUARE_FEET = 43560.0
FEET_TO_INCHES = 12.0
FEET_TO_METERS = 0.3048
CUBIC_FEET_TO_ACRE_FEET = 1.0 / 43560.0


def acres_to_square_feet(acres: float) -> float:
    """Convert acres to square feet."""
    return acres * ACRES_TO_SQUARE_FEET


def square_feet_to_acres(square_feet: float) -> float:
    """Convert square feet to acres."""
    return square_feet / ACRES_TO_SQUARE_FEET


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters."""
    return feet * FEET_TO_METERS


def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters / FEET_TO_METERS
