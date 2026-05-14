"""Tests for project schema migration utilities."""

import pytest

from civil_toolbox.persistence.constants import (
    PROJECT_FILE_TYPE,
    PROJECT_SCHEMA_VERSION,
)
from civil_toolbox.persistence.errors import UnsupportedProjectSchemaError
from civil_toolbox.persistence.migration import migrate_project_data


class TestMigrateProjectData:
    """Tests for migrate_project_data."""

    def test_current_schema_returns_unchanged(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {"name": "Test"},
        }
        result = migrate_project_data(data)
        assert result == data
        assert result is data  # Same object, not a copy

    def test_current_schema_preserves_all_fields(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {
                "id": "proj-123",
                "name": "Full Project",
                "scenarios": [{"name": "Existing"}],
            },
            "extra_field": "preserved",
        }
        result = migrate_project_data(data)
        assert result["project"]["name"] == "Full Project"
        assert result["extra_field"] == "preserved"

    def test_unsupported_future_version_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": "2.0.0",
            "project": {},
        }
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            migrate_project_data(data)
        assert exc_info.value.version == "2.0.0"
        assert "Cannot migrate" in str(exc_info.value)

    def test_unsupported_old_version_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": "0.1.0",
            "project": {},
        }
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            migrate_project_data(data)
        assert exc_info.value.version == "0.1.0"

    def test_missing_schema_version_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "project": {},
        }
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            migrate_project_data(data)
        assert exc_info.value.version is None
        assert "missing schema_version" in str(exc_info.value)

    def test_invalid_version_string_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": "invalid",
            "project": {},
        }
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            migrate_project_data(data)
        assert exc_info.value.version == "invalid"

    def test_empty_version_string_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": "",
            "project": {},
        }
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            migrate_project_data(data)
        assert exc_info.value.version == ""
