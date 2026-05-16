"""Adapter error types.

These errors are raised when domain entities lack required fields
for a calculation. Adapters never infer missing values silently.
"""

from typing import Optional


class AdapterError(Exception):
    """Base class for adapter errors."""

    pass


class MissingFieldError(AdapterError):
    """Raised when a required field is missing from a domain entity.

    Adapters do not infer engineering assumptions. If a required field
    is None, the adapter raises this error with a clear message.
    """

    def __init__(
        self,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        field_name: Optional[str] = None,
    ):
        super().__init__(message)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.field_name = field_name


class IncompatibleEntityError(AdapterError):
    """Raised when entities cannot be used together for a calculation.

    For example, using a DrainageArea with a StormEvent that lacks
    rainfall intensity for the Rational Method.
    """

    def __init__(
        self,
        message: str,
        reason: Optional[str] = None,
    ):
        super().__init__(message)
        self.reason = reason


class CalculationNotApplicableError(AdapterError):
    """Raised when a calculation method is not applicable.

    Some methods have applicability limits (e.g., Rational Method
    for areas > 200 acres). This error signals when those limits
    are exceeded.
    """

    def __init__(
        self,
        message: str,
        method: Optional[str] = None,
        limit_exceeded: Optional[str] = None,
    ):
        super().__init__(message)
        self.method = method
        self.limit_exceeded = limit_exceeded
