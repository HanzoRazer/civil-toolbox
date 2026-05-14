"""Project file validation utilities."""

from __future__ import annotations

from typing import Any

from civil_toolbox.persistence.constants import (
    PROJECT_FILE_TYPE,
    PROJECT_SCHEMA_VERSION,
)
from civil_toolbox.persistence.errors import (
    InvalidProjectFileError,
    UnsupportedProjectSchemaError,
)


def is_supported_schema_version(version: str) -> bool:
    """Check if a schema version is supported."""
    return version == PROJECT_SCHEMA_VERSION


def validate_project_file_type(data: dict[str, Any]) -> None:
    """Validate that data has correct file_type field.

    Raises:
        InvalidProjectFileError: If file_type is missing or incorrect.
    """
    if "file_type" not in data:
        raise InvalidProjectFileError(
            "Missing required field 'file_type' in project file",
            field="file_type",
        )

    if data["file_type"] != PROJECT_FILE_TYPE:
        raise InvalidProjectFileError(
            f"Invalid file_type: expected '{PROJECT_FILE_TYPE}', "
            f"got '{data['file_type']}'",
            field="file_type",
        )


def validate_project_schema_version(data: dict[str, Any]) -> None:
    """Validate that data has a supported schema_version.

    Raises:
        InvalidProjectFileError: If schema_version is missing.
        UnsupportedProjectSchemaError: If schema_version is not supported.
    """
    if "schema_version" not in data:
        raise InvalidProjectFileError(
            "Missing required field 'schema_version' in project file",
            field="schema_version",
        )

    version = data["schema_version"]
    if not is_supported_schema_version(version):
        raise UnsupportedProjectSchemaError(
            f"Unsupported schema version '{version}'. "
            f"Current supported version is '{PROJECT_SCHEMA_VERSION}'.",
            version=version,
        )


def validate_project_payload(data: dict[str, Any]) -> None:
    """Validate that data has a valid project payload.

    Raises:
        InvalidProjectFileError: If project is missing or not a dict.
    """
    if "project" not in data:
        raise InvalidProjectFileError(
            "Missing required field 'project' in project file",
            field="project",
        )

    if not isinstance(data["project"], dict):
        raise InvalidProjectFileError(
            f"Field 'project' must be a dictionary, got {type(data['project']).__name__}",
            field="project",
        )


def validate_project_file_data(data: Any) -> None:
    """Validate a complete project file envelope.

    Validates:
        - data is a dictionary
        - file_type is correct
        - schema_version is supported
        - project payload exists and is a dictionary

    Raises:
        InvalidProjectFileError: If validation fails.
        UnsupportedProjectSchemaError: If schema version is not supported.
    """
    if not isinstance(data, dict):
        raise InvalidProjectFileError(
            f"Project file data must be a dictionary, got {type(data).__name__}",
            field=None,
        )

    validate_project_file_type(data)
    validate_project_schema_version(data)
    validate_project_payload(data)
