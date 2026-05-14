"""Tests for project file validation utilities."""

import pytest

from civil_toolbox.persistence.constants import (
    PROJECT_FILE_TYPE,
    PROJECT_SCHEMA_VERSION,
)
from civil_toolbox.persistence.errors import (
    InvalidProjectFileError,
    UnsupportedProjectSchemaError,
)
from civil_toolbox.persistence.validation import (
    is_supported_schema_version,
    validate_project_file_type,
    validate_project_schema_version,
    validate_project_payload,
    validate_project_file_data,
)


class TestIsSupportedSchemaVersion:
    """Tests for is_supported_schema_version."""

    def test_current_version_is_supported(self):
        assert is_supported_schema_version(PROJECT_SCHEMA_VERSION) is True

    def test_future_version_not_supported(self):
        assert is_supported_schema_version("2.0.0") is False

    def test_old_version_not_supported(self):
        assert is_supported_schema_version("0.1.0") is False

    def test_invalid_version_not_supported(self):
        assert is_supported_schema_version("invalid") is False


class TestValidateProjectFileType:
    """Tests for validate_project_file_type."""

    def test_valid_file_type_passes(self):
        data = {"file_type": PROJECT_FILE_TYPE}
        validate_project_file_type(data)  # Should not raise

    def test_missing_file_type_raises(self):
        data = {}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_type(data)
        assert exc_info.value.field == "file_type"
        assert "Missing" in str(exc_info.value)

    def test_wrong_file_type_raises(self):
        data = {"file_type": "wrong_type"}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_type(data)
        assert exc_info.value.field == "file_type"
        assert "Invalid file_type" in str(exc_info.value)


class TestValidateProjectSchemaVersion:
    """Tests for validate_project_schema_version."""

    def test_current_version_passes(self):
        data = {"schema_version": PROJECT_SCHEMA_VERSION}
        validate_project_schema_version(data)  # Should not raise

    def test_missing_schema_version_raises(self):
        data = {}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_schema_version(data)
        assert exc_info.value.field == "schema_version"
        assert "Missing" in str(exc_info.value)

    def test_unsupported_version_raises(self):
        data = {"schema_version": "99.0.0"}
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            validate_project_schema_version(data)
        assert exc_info.value.version == "99.0.0"
        assert "Unsupported" in str(exc_info.value)


class TestValidateProjectPayload:
    """Tests for validate_project_payload."""

    def test_valid_payload_passes(self):
        data = {"project": {"name": "Test"}}
        validate_project_payload(data)  # Should not raise

    def test_empty_payload_passes(self):
        data = {"project": {}}
        validate_project_payload(data)  # Should not raise

    def test_missing_project_raises(self):
        data = {}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_payload(data)
        assert exc_info.value.field == "project"
        assert "Missing" in str(exc_info.value)

    def test_non_dict_project_raises(self):
        data = {"project": "not a dict"}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_payload(data)
        assert exc_info.value.field == "project"
        assert "must be a dictionary" in str(exc_info.value)

    def test_list_project_raises(self):
        data = {"project": []}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_payload(data)
        assert "must be a dictionary" in str(exc_info.value)

    def test_null_project_raises(self):
        data = {"project": None}
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_payload(data)
        assert "must be a dictionary" in str(exc_info.value)


class TestValidateProjectFileData:
    """Tests for validate_project_file_data (full envelope)."""

    def test_valid_envelope_passes(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {"name": "Test Project"},
        }
        validate_project_file_data(data)  # Should not raise

    def test_minimal_valid_envelope_passes(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {},
        }
        validate_project_file_data(data)  # Should not raise

    def test_non_dict_data_raises(self):
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data("not a dict")
        assert "must be a dictionary" in str(exc_info.value)

    def test_list_data_raises(self):
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data([])
        assert "must be a dictionary" in str(exc_info.value)

    def test_none_data_raises(self):
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data(None)
        assert "must be a dictionary" in str(exc_info.value)

    def test_missing_file_type_raises(self):
        data = {
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {},
        }
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data(data)
        assert exc_info.value.field == "file_type"

    def test_wrong_file_type_raises(self):
        data = {
            "file_type": "wrong",
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": {},
        }
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data(data)
        assert exc_info.value.field == "file_type"

    def test_missing_schema_version_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "project": {},
        }
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data(data)
        assert exc_info.value.field == "schema_version"

    def test_unsupported_schema_version_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": "0.0.1",
            "project": {},
        }
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            validate_project_file_data(data)
        assert exc_info.value.version == "0.0.1"

    def test_missing_project_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
        }
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data(data)
        assert exc_info.value.field == "project"

    def test_non_dict_project_raises(self):
        data = {
            "file_type": PROJECT_FILE_TYPE,
            "schema_version": PROJECT_SCHEMA_VERSION,
            "project": "invalid",
        }
        with pytest.raises(InvalidProjectFileError) as exc_info:
            validate_project_file_data(data)
        assert exc_info.value.field == "project"
