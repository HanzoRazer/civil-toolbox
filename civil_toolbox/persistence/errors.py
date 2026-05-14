"""Error types for project persistence."""

from __future__ import annotations


class ProjectPersistenceError(Exception):
    """Base error for project persistence failures."""


class ProjectFileReadError(ProjectPersistenceError):
    """Raised when a project file cannot be read."""

    def __init__(self, message: str, path: str | None = None) -> None:
        self.path = path
        super().__init__(message)


class ProjectFileWriteError(ProjectPersistenceError):
    """Raised when a project file cannot be written."""

    def __init__(self, message: str, path: str | None = None) -> None:
        self.path = path
        super().__init__(message)


class InvalidProjectFileError(ProjectPersistenceError):
    """Raised when a file is not a valid Civil Toolbox project file."""

    def __init__(self, message: str, field: str | None = None) -> None:
        self.field = field
        super().__init__(message)


class UnsupportedProjectSchemaError(ProjectPersistenceError):
    """Raised when a project file uses an unsupported schema version."""

    def __init__(self, message: str, version: str | None = None) -> None:
        self.version = version
        super().__init__(message)
