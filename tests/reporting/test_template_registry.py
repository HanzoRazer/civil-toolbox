"""Tests for report template registry."""

import pytest

from civil_toolbox.reporting.report_templates import (
    ReportTemplate,
    SectionTemplate,
)
from civil_toolbox.reporting.template_registry import (
    ReportTemplateRegistry,
    TemplateNotFoundError,
)


@pytest.fixture
def sample_template():
    """Create a sample template for testing."""
    return ReportTemplate(
        id="sample_template",
        name="Sample Template",
        version="1.0",
        sections=[
            SectionTemplate(
                id="section1",
                title="Section 1",
                section_type="project_summary",
            ),
        ],
    )


@pytest.fixture
def another_template():
    """Create another template for testing."""
    return ReportTemplate(
        id="another_template",
        name="Another Template",
        version="1.0",
        sections=[
            SectionTemplate(
                id="section1",
                title="Section 1",
                section_type="scenario_summary",
            ),
        ],
    )


class TestReportTemplateRegistry:
    """Tests for ReportTemplateRegistry."""

    def test_empty_registry(self):
        """New registry is empty."""
        registry = ReportTemplateRegistry()
        assert len(registry) == 0
        assert registry.list_templates() == []

    def test_register_template(self, sample_template):
        """Template can be registered."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        assert len(registry) == 1
        assert registry.has_template("sample_template")

    def test_get_template(self, sample_template):
        """Registered template can be retrieved."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        retrieved = registry.get("sample_template")
        assert retrieved.id == "sample_template"
        assert retrieved.name == "Sample Template"

    def test_get_missing_template_raises(self):
        """Getting missing template raises TemplateNotFoundError."""
        registry = ReportTemplateRegistry()
        with pytest.raises(TemplateNotFoundError) as exc_info:
            registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.template_id == "nonexistent"

    def test_list_templates(self, sample_template, another_template):
        """list_templates returns all templates sorted by ID."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        registry.register(another_template)
        templates = registry.list_templates()
        assert len(templates) == 2
        assert templates[0].id == "another_template"
        assert templates[1].id == "sample_template"

    def test_duplicate_registration_fails(self, sample_template):
        """Registering duplicate ID without overwrite fails."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(sample_template)

    def test_overwrite_registration_succeeds(self, sample_template):
        """Registering duplicate ID with overwrite succeeds."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)

        updated = ReportTemplate(
            id="sample_template",
            name="Updated Template",
            version="2.0",
            sections=[
                SectionTemplate(
                    id="section1",
                    title="Section 1",
                    section_type="project_summary",
                ),
            ],
        )
        registry.register(updated, overwrite=True)

        retrieved = registry.get("sample_template")
        assert retrieved.name == "Updated Template"
        assert retrieved.version == "2.0"

    def test_has_template_true(self, sample_template):
        """has_template returns True for registered template."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        assert registry.has_template("sample_template") is True

    def test_has_template_false(self):
        """has_template returns False for missing template."""
        registry = ReportTemplateRegistry()
        assert registry.has_template("nonexistent") is False

    def test_unregister_template(self, sample_template):
        """Template can be unregistered."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        assert len(registry) == 1

        registry.unregister("sample_template")
        assert len(registry) == 0
        assert not registry.has_template("sample_template")

    def test_unregister_missing_raises(self):
        """Unregistering missing template raises TemplateNotFoundError."""
        registry = ReportTemplateRegistry()
        with pytest.raises(TemplateNotFoundError):
            registry.unregister("nonexistent")

    def test_clear_registry(self, sample_template, another_template):
        """clear removes all templates."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        registry.register(another_template)
        assert len(registry) == 2

        registry.clear()
        assert len(registry) == 0

    def test_contains_operator(self, sample_template):
        """'in' operator works for checking template existence."""
        registry = ReportTemplateRegistry()
        registry.register(sample_template)
        assert "sample_template" in registry
        assert "nonexistent" not in registry

    def test_len_operator(self, sample_template, another_template):
        """len() returns number of registered templates."""
        registry = ReportTemplateRegistry()
        assert len(registry) == 0

        registry.register(sample_template)
        assert len(registry) == 1

        registry.register(another_template)
        assert len(registry) == 2


class TestTemplateNotFoundError:
    """Tests for TemplateNotFoundError."""

    def test_error_message(self):
        """Error includes template ID in message."""
        error = TemplateNotFoundError("my_template")
        assert "my_template" in str(error)

    def test_error_template_id_attribute(self):
        """Error has template_id attribute."""
        error = TemplateNotFoundError("my_template")
        assert error.template_id == "my_template"

    def test_is_key_error(self):
        """TemplateNotFoundError is a KeyError subclass."""
        error = TemplateNotFoundError("my_template")
        assert isinstance(error, KeyError)
