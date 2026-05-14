"""Tests for project persistence error types."""

import pytest

from civil_toolbox.persistence.errors import (
    ProjectPersistenceError,
    ProjectFileReadError,
    ProjectFileWriteError,
    InvalidProjectFileError,
    UnsupportedProjectSchemaError,
)


class TestPersistenceErrorInheritance:
    """Test error type inheritance."""

    def test_read_error_inherits_from_base(self):
        assert issubclass(ProjectFileReadError, ProjectPersistenceError)

    def test_write_error_inherits_from_base(self):
        assert issubclass(ProjectFileWriteError, ProjectPersistenceError)

    def test_invalid_file_error_inherits_from_base(self):
        assert issubclass(InvalidProjectFileError, ProjectPersistenceError)

    def test_unsupported_schema_error_inherits_from_base(self):
        assert issubclass(UnsupportedProjectSchemaError, ProjectPersistenceError)

    def test_base_error_inherits_from_exception(self):
        assert issubclass(ProjectPersistenceError, Exception)


class TestProjectFileReadError:
    """Tests for ProjectFileReadError."""

    def test_creates_with_message(self):
        error = ProjectFileReadError("Could not read file")
        assert str(error) == "Could not read file"

    def test_creates_with_path(self):
        error = ProjectFileReadError("File not found", path="/path/to/file.json")
        assert error.path == "/path/to/file.json"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(ProjectFileReadError) as exc_info:
            raise ProjectFileReadError("Test error", path="test.json")
        assert exc_info.value.path == "test.json"


class TestProjectFileWriteError:
    """Tests for ProjectFileWriteError."""

    def test_creates_with_message(self):
        error = ProjectFileWriteError("Could not write file")
        assert str(error) == "Could not write file"

    def test_creates_with_path(self):
        error = ProjectFileWriteError("Permission denied", path="/readonly/file.json")
        assert error.path == "/readonly/file.json"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(ProjectFileWriteError) as exc_info:
            raise ProjectFileWriteError("Test error", path="output.json")
        assert exc_info.value.path == "output.json"


class TestInvalidProjectFileError:
    """Tests for InvalidProjectFileError."""

    def test_creates_with_message(self):
        error = InvalidProjectFileError("Invalid project file")
        assert str(error) == "Invalid project file"

    def test_creates_with_field(self):
        error = InvalidProjectFileError("Missing required field", field="file_type")
        assert error.field == "file_type"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(InvalidProjectFileError) as exc_info:
            raise InvalidProjectFileError("Bad field", field="schema_version")
        assert exc_info.value.field == "schema_version"


class TestUnsupportedProjectSchemaError:
    """Tests for UnsupportedProjectSchemaError."""

    def test_creates_with_message(self):
        error = UnsupportedProjectSchemaError("Unsupported schema")
        assert str(error) == "Unsupported schema"

    def test_creates_with_version(self):
        error = UnsupportedProjectSchemaError(
            "Schema version 2.0.0 is not supported",
            version="2.0.0",
        )
        assert error.version == "2.0.0"

    def test_can_be_raised_and_caught(self):
        with pytest.raises(UnsupportedProjectSchemaError) as exc_info:
            raise UnsupportedProjectSchemaError("Old schema", version="0.1.0")
        assert exc_info.value.version == "0.1.0"


class TestErrorMessages:
    """Test that errors produce useful messages."""

    def test_read_error_message_includes_context(self):
        error = ProjectFileReadError(
            "Failed to read project file: permission denied",
            path="/protected/project.ctbx.json",
        )
        assert "permission denied" in str(error)
        assert error.path == "/protected/project.ctbx.json"

    def test_invalid_file_error_message_includes_field(self):
        error = InvalidProjectFileError(
            "Missing required field 'file_type' in project file",
            field="file_type",
        )
        assert "file_type" in str(error)
        assert error.field == "file_type"

    def test_unsupported_schema_error_includes_version(self):
        error = UnsupportedProjectSchemaError(
            "Project file uses schema version 99.0.0 which is not supported. "
            "Current supported version is 1.0.0.",
            version="99.0.0",
        )
        assert "99.0.0" in str(error)
        assert error.version == "99.0.0"
