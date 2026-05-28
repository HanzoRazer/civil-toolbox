"""Tests for report template models."""

import pytest

from civil_toolbox.reporting.report_templates import (
    SectionTemplate,
    ReportTemplate,
    SUPPORTED_SECTION_TYPES,
    SUPPORTED_FORMATTING_PROFILES,
)


class TestSectionTemplate:
    """Tests for SectionTemplate."""

    def test_create_minimal_section(self):
        """Create section with required fields only."""
        section = SectionTemplate(
            id="test",
            title="Test Section",
            section_type="project_summary",
        )
        assert section.id == "test"
        assert section.title == "Test Section"
        assert section.section_type == "project_summary"
        assert section.required is True
        assert section.include_when_empty is False
        assert section.order == 0
        assert section.metadata == {}

    def test_create_section_with_all_fields(self):
        """Create section with all fields specified."""
        section = SectionTemplate(
            id="test",
            title="Test Section",
            section_type="custom_text",
            required=False,
            include_when_empty=True,
            order=10,
            metadata={"custom_key": "value"},
        )
        assert section.required is False
        assert section.include_when_empty is True
        assert section.order == 10
        assert section.metadata == {"custom_key": "value"}

    def test_missing_id_raises(self):
        """Missing ID raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            SectionTemplate(
                id="",
                title="Test",
                section_type="project_summary",
            )

    def test_missing_title_raises(self):
        """Missing title raises ValueError."""
        with pytest.raises(ValueError, match="title is required"):
            SectionTemplate(
                id="test",
                title="",
                section_type="project_summary",
            )

    def test_missing_section_type_raises(self):
        """Missing section_type raises ValueError."""
        with pytest.raises(ValueError, match="section_type is required"):
            SectionTemplate(
                id="test",
                title="Test",
                section_type="",
            )

    def test_invalid_order_type_raises(self):
        """Non-integer order raises ValueError."""
        with pytest.raises(ValueError, match="order must be an integer"):
            SectionTemplate(
                id="test",
                title="Test",
                section_type="project_summary",
                order="10",  # type: ignore
            )

    def test_to_dict(self):
        """Serialize section to dictionary."""
        section = SectionTemplate(
            id="test",
            title="Test Section",
            section_type="project_summary",
            required=False,
            order=5,
        )
        data = section.to_dict()
        assert data["id"] == "test"
        assert data["title"] == "Test Section"
        assert data["section_type"] == "project_summary"
        assert data["required"] is False
        assert data["order"] == 5

    def test_from_dict(self):
        """Deserialize section from dictionary."""
        data = {
            "id": "test",
            "title": "Test Section",
            "section_type": "custom_text",
            "required": False,
            "include_when_empty": True,
            "order": 10,
            "metadata": {"key": "value"},
        }
        section = SectionTemplate.from_dict(data)
        assert section.id == "test"
        assert section.title == "Test Section"
        assert section.section_type == "custom_text"
        assert section.required is False
        assert section.include_when_empty is True
        assert section.order == 10
        assert section.metadata == {"key": "value"}

    def test_round_trip(self):
        """Section survives serialization round-trip."""
        original = SectionTemplate(
            id="test",
            title="Test Section",
            section_type="project_summary",
            required=False,
            include_when_empty=True,
            order=5,
            metadata={"nested": {"key": "value"}},
        )
        restored = SectionTemplate.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.section_type == original.section_type
        assert restored.required == original.required
        assert restored.include_when_empty == original.include_when_empty
        assert restored.order == original.order
        assert restored.metadata == original.metadata


class TestReportTemplate:
    """Tests for ReportTemplate."""

    def test_create_minimal_template(self):
        """Create template with minimal required fields."""
        template = ReportTemplate(
            id="test_template",
            name="Test Template",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="section1",
                    title="Section 1",
                    section_type="project_summary",
                ),
            ],
        )
        assert template.id == "test_template"
        assert template.name == "Test Template"
        assert template.version == "1.0"
        assert len(template.sections) == 1
        assert len(template.appendices) == 0
        assert template.formatting_profile == "standard"

    def test_create_template_with_appendices(self):
        """Create template with both sections and appendices."""
        template = ReportTemplate(
            id="test_template",
            name="Test Template",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="section1",
                    title="Section 1",
                    section_type="project_summary",
                ),
            ],
            appendices=[
                SectionTemplate(
                    id="appendix1",
                    title="Appendix A",
                    section_type="calculation_appendix",
                ),
            ],
        )
        assert len(template.sections) == 1
        assert len(template.appendices) == 1

    def test_create_template_with_appendices_only(self):
        """Template with only appendices is valid."""
        template = ReportTemplate(
            id="test_template",
            name="Test Template",
            version="1.0",
            appendices=[
                SectionTemplate(
                    id="appendix1",
                    title="Appendix A",
                    section_type="references",
                ),
            ],
        )
        assert len(template.sections) == 0
        assert len(template.appendices) == 1

    def test_missing_id_raises(self):
        """Missing ID raises ValueError."""
        with pytest.raises(ValueError, match="id is required"):
            ReportTemplate(
                id="",
                name="Test",
                version="1.0",
                sections=[
                    SectionTemplate(
                        id="s1",
                        title="S1",
                        section_type="project_summary",
                    ),
                ],
            )

    def test_missing_name_raises(self):
        """Missing name raises ValueError."""
        with pytest.raises(ValueError, match="name is required"):
            ReportTemplate(
                id="test",
                name="",
                version="1.0",
                sections=[
                    SectionTemplate(
                        id="s1",
                        title="S1",
                        section_type="project_summary",
                    ),
                ],
            )

    def test_missing_version_raises(self):
        """Missing version raises ValueError."""
        with pytest.raises(ValueError, match="version is required"):
            ReportTemplate(
                id="test",
                name="Test",
                version="",
                sections=[
                    SectionTemplate(
                        id="s1",
                        title="S1",
                        section_type="project_summary",
                    ),
                ],
            )

    def test_empty_template_raises(self):
        """Template with no sections or appendices raises ValueError."""
        with pytest.raises(ValueError, match="at least one section or appendix"):
            ReportTemplate(
                id="test",
                name="Test",
                version="1.0",
            )

    def test_duplicate_section_ids_raises(self):
        """Duplicate section IDs raise ValueError."""
        with pytest.raises(ValueError, match="unique"):
            ReportTemplate(
                id="test",
                name="Test",
                version="1.0",
                sections=[
                    SectionTemplate(
                        id="duplicate",
                        title="Section 1",
                        section_type="project_summary",
                    ),
                    SectionTemplate(
                        id="duplicate",
                        title="Section 2",
                        section_type="scenario_summary",
                    ),
                ],
            )

    def test_duplicate_across_sections_and_appendices_raises(self):
        """Duplicate ID between section and appendix raises ValueError."""
        with pytest.raises(ValueError, match="unique"):
            ReportTemplate(
                id="test",
                name="Test",
                version="1.0",
                sections=[
                    SectionTemplate(
                        id="duplicate",
                        title="Section 1",
                        section_type="project_summary",
                    ),
                ],
                appendices=[
                    SectionTemplate(
                        id="duplicate",
                        title="Appendix A",
                        section_type="references",
                    ),
                ],
            )

    def test_unsupported_formatting_profile_raises(self):
        """Unsupported formatting profile raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported formatting profile"):
            ReportTemplate(
                id="test",
                name="Test",
                version="1.0",
                sections=[
                    SectionTemplate(
                        id="s1",
                        title="S1",
                        section_type="project_summary",
                    ),
                ],
                formatting_profile="invalid_profile",
            )

    def test_supported_formatting_profiles(self):
        """All supported profiles are accepted."""
        for profile in SUPPORTED_FORMATTING_PROFILES:
            template = ReportTemplate(
                id="test",
                name="Test",
                version="1.0",
                sections=[
                    SectionTemplate(
                        id="s1",
                        title="S1",
                        section_type="project_summary",
                    ),
                ],
                formatting_profile=profile,
            )
            assert template.formatting_profile == profile

    def test_get_ordered_sections(self):
        """Sections are returned sorted by order then id."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(id="c", title="C", section_type="warnings", order=10),
                SectionTemplate(id="a", title="A", section_type="project_summary", order=5),
                SectionTemplate(id="b", title="B", section_type="assumptions", order=5),
            ],
        )
        ordered = template.get_ordered_sections()
        assert [s.id for s in ordered] == ["a", "b", "c"]

    def test_get_ordered_appendices(self):
        """Appendices are returned sorted by order then id."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            appendices=[
                SectionTemplate(id="z", title="Z", section_type="references", order=20),
                SectionTemplate(id="x", title="X", section_type="assumptions", order=10),
                SectionTemplate(id="y", title="Y", section_type="warnings", order=10),
            ],
        )
        ordered = template.get_ordered_appendices()
        assert [a.id for a in ordered] == ["x", "y", "z"]

    def test_to_dict(self):
        """Serialize template to dictionary."""
        template = ReportTemplate(
            id="test",
            name="Test Template",
            version="1.0",
            description="A test template",
            sections=[
                SectionTemplate(
                    id="s1",
                    title="Section 1",
                    section_type="project_summary",
                ),
            ],
            appendices=[
                SectionTemplate(
                    id="a1",
                    title="Appendix A",
                    section_type="references",
                ),
            ],
            formatting_profile="compact",
            metadata={"custom": "data"},
        )
        data = template.to_dict()
        assert data["id"] == "test"
        assert data["name"] == "Test Template"
        assert data["version"] == "1.0"
        assert data["description"] == "A test template"
        assert len(data["sections"]) == 1
        assert len(data["appendices"]) == 1
        assert data["formatting_profile"] == "compact"
        assert data["metadata"] == {"custom": "data"}

    def test_from_dict(self):
        """Deserialize template from dictionary."""
        data = {
            "id": "test",
            "name": "Test Template",
            "version": "2.0",
            "description": "Restored template",
            "sections": [
                {
                    "id": "s1",
                    "title": "Section 1",
                    "section_type": "project_summary",
                },
            ],
            "appendices": [
                {
                    "id": "a1",
                    "title": "Appendix A",
                    "section_type": "references",
                },
            ],
            "formatting_profile": "review",
            "metadata": {"restored": True},
        }
        template = ReportTemplate.from_dict(data)
        assert template.id == "test"
        assert template.name == "Test Template"
        assert template.version == "2.0"
        assert template.description == "Restored template"
        assert len(template.sections) == 1
        assert len(template.appendices) == 1
        assert template.formatting_profile == "review"
        assert template.metadata == {"restored": True}

    def test_round_trip(self):
        """Template survives serialization round-trip."""
        original = ReportTemplate(
            id="test",
            name="Test Template",
            version="1.0",
            description="Original description",
            sections=[
                SectionTemplate(
                    id="s1",
                    title="Section 1",
                    section_type="project_summary",
                    order=10,
                ),
                SectionTemplate(
                    id="s2",
                    title="Section 2",
                    section_type="scenario_summary",
                    required=False,
                    order=20,
                ),
            ],
            appendices=[
                SectionTemplate(
                    id="a1",
                    title="Appendix A",
                    section_type="references",
                ),
            ],
            formatting_profile="compact",
            metadata={"version_info": {"major": 1, "minor": 0}},
        )
        restored = ReportTemplate.from_dict(original.to_dict())
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.version == original.version
        assert restored.description == original.description
        assert len(restored.sections) == len(original.sections)
        assert len(restored.appendices) == len(original.appendices)
        assert restored.formatting_profile == original.formatting_profile
        assert restored.metadata == original.metadata


class TestSupportedTypes:
    """Tests for supported section types and profiles."""

    def test_supported_section_types_exist(self):
        """All expected section types are defined."""
        expected_types = {
            "project_summary",
            "scenario_summary",
            "comparison_summary",
            "comparison_table",
            "comparison_totals",
            "calculation_summary",
            "calculation_appendix",
            "assumptions",
            "warnings",
            "references",
            "custom_text",
            "heading",
        }
        assert expected_types.issubset(SUPPORTED_SECTION_TYPES)

    def test_supported_formatting_profiles_exist(self):
        """All expected formatting profiles are defined."""
        expected_profiles = {"standard", "compact", "review", "appendix_heavy"}
        assert expected_profiles == SUPPORTED_FORMATTING_PROFILES
