"""Project file save and load utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TYPE_CHECKING

from civil_toolbox.persistence.constants import (
    PROJECT_FILE_TYPE,
    PROJECT_SCHEMA_VERSION,
)
from civil_toolbox.persistence.errors import (
    InvalidProjectFileError,
    ProjectFileReadError,
    ProjectFileWriteError,
)
from civil_toolbox.persistence.validation import validate_project_file_data
from civil_toolbox.persistence.migration import migrate_project_data

if TYPE_CHECKING:
    from civil_toolbox.domain.project import Project


def project_to_file_data(project: Project) -> dict[str, Any]:
    """Convert a Project to a file-ready data envelope.

    Args:
        project: The Project domain object to serialize.

    Returns:
        Dictionary with file_type, schema_version, and project payload.
    """
    return {
        "file_type": PROJECT_FILE_TYPE,
        "schema_version": PROJECT_SCHEMA_VERSION,
        "project": project.to_dict(),
    }


def save_project(project: Project, path: str | Path) -> Path:
    """Save a Project to a Civil Toolbox project file.

    Args:
        project: The Project domain object to save.
        path: File path to write (str or Path).

    Returns:
        The Path where the project was saved.

    Raises:
        ProjectFileWriteError: If the file cannot be written.
    """
    path = Path(path)
    file_data = project_to_file_data(project)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=2, sort_keys=True, ensure_ascii=False)
    except OSError as e:
        raise ProjectFileWriteError(
            f"Failed to write project file: {e}",
            path=str(path),
        ) from e

    return path


def project_from_file_data(data: dict[str, Any]) -> "Project":
    """Reconstruct a Project from validated file data.

    Args:
        data: Project file data dictionary (already validated).

    Returns:
        Reconstructed Project domain object.

    Raises:
        InvalidProjectFileError: If project payload cannot be reconstructed.
    """
    from civil_toolbox.domain.project import Project

    try:
        return Project.from_dict(data["project"])
    except (KeyError, TypeError, ValueError) as e:
        raise InvalidProjectFileError(
            f"Failed to reconstruct project from file data: {e}",
            field="project",
        ) from e


def load_project(path: str | Path) -> "Project":
    """Load a Project from a Civil Toolbox project file.

    Args:
        path: File path to read (str or Path).

    Returns:
        Reconstructed Project domain object.

    Raises:
        ProjectFileReadError: If the file cannot be read or parsed.
        InvalidProjectFileError: If the file is not a valid project file.
        UnsupportedProjectSchemaError: If the schema version is not supported.
    """
    path = Path(path)

    # Read file
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError as e:
        raise ProjectFileReadError(
            f"Project file not found: {path}",
            path=str(path),
        ) from e
    except OSError as e:
        raise ProjectFileReadError(
            f"Failed to read project file: {e}",
            path=str(path),
        ) from e

    # Parse JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ProjectFileReadError(
            f"Invalid JSON in project file: {e}",
            path=str(path),
        ) from e

    # Validate envelope
    validate_project_file_data(data)

    # Migrate if needed
    data = migrate_project_data(data)

    # Reconstruct project
    return project_from_file_data(data)
