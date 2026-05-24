"""Exception classes for infrastructure modeling."""

from __future__ import annotations


class InfrastructureError(Exception):
    """Base exception for infrastructure module."""


class InvalidInfrastructureError(InfrastructureError, ValueError):
    """Raised when infrastructure data is invalid."""


class InfrastructureValidationError(InfrastructureError):
    """Raised when infrastructure validation fails."""


class NodeNotFoundError(InfrastructureError, KeyError):
    """Raised when a referenced node is not found."""


class ElementNotFoundError(InfrastructureError, KeyError):
    """Raised when a referenced element is not found."""


class NetworkValidationError(InfrastructureError):
    """Raised when network-level validation fails."""
