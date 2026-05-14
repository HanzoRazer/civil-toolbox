"""Tests for base domain entities."""

import pytest
from datetime import datetime

from civil_toolbox.domain.base import (
    BaseEntity,
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)


class TestBaseEntity:
    """Tests for BaseEntity."""

    def test_creates_with_auto_id(self):
        entity = BaseEntity()
        assert entity.id is not None
        assert len(entity.id) == 36  # UUID format

    def test_creates_with_timestamps(self):
        entity = BaseEntity()
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)

    def test_touch_updates_timestamp(self):
        entity = BaseEntity()
        original = entity.updated_at
        entity.touch()
        assert entity.updated_at >= original

    def test_to_dict_serialization(self):
        entity = BaseEntity(id="test-123")
        data = entity.to_dict()
        assert data["id"] == "test-123"
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict_deserialization(self):
        data = {
            "id": "test-456",
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
        }
        entity = BaseEntity.from_dict(data)
        assert entity.id == "test-456"
        assert entity.created_at.year == 2026


class TestEngineeringReference:
    """Tests for EngineeringReference."""

    def test_creates_with_required_fields(self):
        ref = EngineeringReference(
            title="Urban Hydrology for Small Watersheds",
            source="NRCS TR-55",
        )
        assert ref.title == "Urban Hydrology for Small Watersheds"
        assert ref.source == "NRCS TR-55"

    def test_creates_with_optional_fields(self):
        ref = EngineeringReference(
            title="Urban Drainage Design Manual",
            source="FHWA HEC-22",
            year=2009,
            section="Chapter 3",
            url="https://www.fhwa.dot.gov/engineering/hydraulics/pubs/10009/",
        )
        assert ref.year == 2009
        assert ref.section == "Chapter 3"
        assert ref.url is not None

    def test_raises_on_missing_title(self):
        with pytest.raises(ValueError, match="requires a title"):
            EngineeringReference(title="", source="NRCS")

    def test_raises_on_missing_source(self):
        with pytest.raises(ValueError, match="requires a source"):
            EngineeringReference(title="Test", source="")

    def test_round_trip_serialization(self):
        ref = EngineeringReference(
            title="Test Reference",
            source="Test Source",
            year=2025,
        )
        data = ref.to_dict()
        restored = EngineeringReference.from_dict(data)
        assert restored.title == ref.title
        assert restored.source == ref.source
        assert restored.year == ref.year


class TestEngineeringAssumption:
    """Tests for EngineeringAssumption."""

    def test_creates_with_description(self):
        assumption = EngineeringAssumption(
            description="Steady-state flow conditions"
        )
        assert assumption.description == "Steady-state flow conditions"

    def test_creates_with_category(self):
        assumption = EngineeringAssumption(
            description="Uniform land use",
            category="hydrology",
        )
        assert assumption.category == "hydrology"

    def test_creates_with_reference(self):
        ref = EngineeringReference(title="TR-55", source="NRCS")
        assumption = EngineeringAssumption(
            description="CN method applicable",
            reference=ref,
        )
        assert assumption.reference is not None
        assert assumption.reference.title == "TR-55"

    def test_raises_on_empty_description(self):
        with pytest.raises(ValueError, match="requires a description"):
            EngineeringAssumption(description="")

    def test_round_trip_serialization(self):
        assumption = EngineeringAssumption(
            description="Test assumption",
            category="test",
        )
        data = assumption.to_dict()
        restored = EngineeringAssumption.from_dict(data)
        assert restored.description == assumption.description
        assert restored.category == assumption.category

    def test_round_trip_with_reference(self):
        ref = EngineeringReference(title="Test", source="Source")
        assumption = EngineeringAssumption(
            description="With reference",
            reference=ref,
        )
        data = assumption.to_dict()
        restored = EngineeringAssumption.from_dict(data)
        assert restored.reference is not None
        assert restored.reference.title == "Test"


class TestValidationWarning:
    """Tests for ValidationWarning."""

    def test_creates_with_message(self):
        warning = ValidationWarning(message="Value exceeds typical range")
        assert warning.message == "Value exceeds typical range"
        assert warning.severity == "warning"

    def test_creates_with_field(self):
        warning = ValidationWarning(
            message="High runoff coefficient",
            field="runoff_coefficient",
        )
        assert warning.field == "runoff_coefficient"

    def test_creates_with_severity(self):
        warning = ValidationWarning(
            message="Info message",
            severity="info",
        )
        assert warning.severity == "info"

    def test_raises_on_empty_message(self):
        with pytest.raises(ValueError, match="requires a message"):
            ValidationWarning(message="")

    def test_raises_on_invalid_severity(self):
        with pytest.raises(ValueError, match="must be 'info', 'warning', or 'error'"):
            ValidationWarning(message="Test", severity="critical")

    def test_valid_severities(self):
        for severity in ("info", "warning", "error"):
            warning = ValidationWarning(message="Test", severity=severity)
            assert warning.severity == severity

    def test_round_trip_serialization(self):
        warning = ValidationWarning(
            message="Test warning",
            field="test_field",
            severity="error",
        )
        data = warning.to_dict()
        restored = ValidationWarning.from_dict(data)
        assert restored.message == warning.message
        assert restored.field == warning.field
        assert restored.severity == warning.severity
