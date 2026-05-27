"""Error types for design criteria operations.

Provides clear error hierarchy for criteria validation and lookup failures.
"""


class DesignCriteriaError(ValueError):
    """Base error for design criteria failures.

    All design criteria errors inherit from this class, allowing
    callers to catch all criteria errors with a single except clause.
    """

    pass


class InvalidDesignCriteriaError(DesignCriteriaError):
    """Raised when design criteria data is invalid.

    Examples:
        - Invalid runoff coefficient (outside 0-1)
        - Invalid curve number (outside 0-100)
        - Invalid soil group
        - Missing required fields
    """

    pass


class DesignCriteriaLookupError(DesignCriteriaError):
    """Raised when a criteria lookup cannot be completed.

    Examples:
        - Land use not found in coefficient table
        - Soil group not found for land use
        - Design storm not defined
    """

    pass


class CriteriaNotFoundError(DesignCriteriaError):
    """Raised when criteria set is not found in a library.

    Examples:
        - Unknown jurisdiction ID
        - Criteria ID not registered
    """

    pass
