"""Error types for rainfall IDF operations.

Provides clear error hierarchy for IDF data validation and lookup failures.
"""


class RainfallDataError(ValueError):
    """Base error for rainfall data failures.

    All rainfall-related errors inherit from this class, allowing
    callers to catch all rainfall errors with a single except clause.
    """

    pass


class InvalidIDFDataError(RainfallDataError):
    """Raised when IDF data is invalid.

    Examples:
        - Negative return period
        - Zero duration
        - Negative intensity
        - Duplicate return period + duration combinations
        - Empty point list
    """

    pass


class IDFLookupError(RainfallDataError):
    """Raised when an IDF lookup cannot be completed.

    Examples:
        - Requested return period not in curve
        - Requested duration outside interpolation range
    """

    pass


class IDFInterpolationError(IDFLookupError):
    """Raised when interpolation cannot be completed.

    Examples:
        - Duration outside available range
        - Return period interpolation requested but not implemented
        - Insufficient points for interpolation
    """

    pass
