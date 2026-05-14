"""Project schema migration utilities."""

from __future__ import annotations

from typing import Any

from civil_toolbox.persistence.constants import PROJECT_SCHEMA_VERSION
from civil_toolbox.persistence.errors import UnsupportedProjectSchemaError
from civil_toolbox.persistence.validation import is_supported_schema_version


def migrate_project_data(data: dict[str, Any]) -> dict[str, Any]:
    """Migrate project data to the current schema version if needed.

    For version 1.0.0, this function validates the schema version and
    returns the data unchanged. Future versions will add migration logic.

    Args:
        data: Project file data dictionary with schema_version field.

    Returns:
        Migrated project file data (currently unchanged for v1.0.0).

    Raises:
        UnsupportedProjectSchemaError: If schema version cannot be migrated.
    """
    version = data.get("schema_version")

    if version is None:
        raise UnsupportedProjectSchemaError(
            "Project data is missing schema_version field",
            version=None,
        )

    if is_supported_schema_version(version):
        return data

    raise UnsupportedProjectSchemaError(
        f"Cannot migrate from schema version '{version}' to '{PROJECT_SCHEMA_VERSION}'. "
        f"No migration path available.",
        version=version,
    )
