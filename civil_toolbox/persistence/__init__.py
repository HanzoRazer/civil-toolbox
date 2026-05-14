"""Civil Toolbox project persistence layer."""

from civil_toolbox.persistence.constants import (
    PROJECT_FILE_TYPE,
    PROJECT_SCHEMA_VERSION,
    PROJECT_FILE_EXTENSION,
)
from civil_toolbox.persistence.errors import (
    ProjectPersistenceError,
    ProjectFileReadError,
    ProjectFileWriteError,
    InvalidProjectFileError,
    UnsupportedProjectSchemaError,
)
from civil_toolbox.persistence.project_io import (
    project_to_file_data,
    project_from_file_data,
    save_project,
    load_project,
)

__all__ = [
    # Constants
    "PROJECT_FILE_TYPE",
    "PROJECT_SCHEMA_VERSION",
    "PROJECT_FILE_EXTENSION",
    # Errors
    "ProjectPersistenceError",
    "ProjectFileReadError",
    "ProjectFileWriteError",
    "InvalidProjectFileError",
    "UnsupportedProjectSchemaError",
    # IO
    "project_to_file_data",
    "project_from_file_data",
    "save_project",
    "load_project",
]
