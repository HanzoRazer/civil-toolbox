"""Error types for the reporting engine."""

from __future__ import annotations


class ReportingError(Exception):
    """Base exception for reporting errors."""

    pass


class InvalidReportDataError(ReportingError):
    """Raised when report data is invalid or incomplete."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


class MissingProjectError(ReportingError):
    """Raised when a report requires a project but none is provided."""

    pass


class MissingScenarioError(ReportingError):
    """Raised when a report requires scenarios but none are provided."""

    pass


class MissingComparisonError(ReportingError):
    """Raised when a comparison report requires comparison data but none is provided."""

    pass


class RenderingError(ReportingError):
    """Raised when report rendering fails."""

    def __init__(self, message: str, section_index: int | None = None):
        self.section_index = section_index
        super().__init__(message)
