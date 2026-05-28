"""Tests for report template validation."""

import pytest

from civil_toolbox.reporting.report_templates import (
    ReportTemplate,
    SectionTemplate,
)
from civil_toolbox.reporting.template_context import ReportTemplateContext
from civil_toolbox.reporting.template_validation import (
    validate_template,
    validate_section_template,
    validate_template_context,
    can_build_section,
    TemplateValidationError,
    ContextValidationError,
    SECTION_REQUIREMENTS,
)


class TestValidateSectionTemplate:
    """Tests for validate_section_template."""

    def test_valid_section_passes(self):
        """Valid section passes validation."""
        section = SectionTemplate(
            id="test",
            title="Test Section",
            section_type="project_summary",
        )
        validate_section_template(section)

    def test_unknown_section_type_fails(self):
        """Unknown section type raises TemplateValidationError."""
        section = SectionTemplate(
            id="test",
            title="Test",
            section_type="invalid_type",
        )
        with pytest.raises(TemplateValidationError, match="Unknown section type"):
            validate_section_template(section)


class TestValidateTemplate:
    """Tests for validate_template."""

    def test_valid_template_passes(self):
        """Valid template passes validation."""
        template = ReportTemplate(
            id="test",
            name="Test Template",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="s1",
                    title="Section 1",
                    section_type="project_summary",
                ),
            ],
        )
        validate_template(template)

    def test_template_with_all_valid_section_types(self):
        """Template with various valid section types passes."""
        template = ReportTemplate(
            id="test",
            name="Test Template",
            version="1.0",
            sections=[
                SectionTemplate(id="s1", title="S1", section_type="project_summary"),
                SectionTemplate(id="s2", title="S2", section_type="scenario_summary"),
                SectionTemplate(id="s3", title="S3", section_type="comparison_summary"),
                SectionTemplate(id="s4", title="S4", section_type="assumptions"),
                SectionTemplate(id="s5", title="S5", section_type="warnings"),
                SectionTemplate(id="s6", title="S6", section_type="references"),
            ],
        )
        validate_template(template)


class TestValidateTemplateContext:
    """Tests for validate_template_context."""

    @pytest.fixture
    def sample_project(self):
        """Create a sample project."""
        from civil_toolbox.domain.project import Project
        return Project(name="Test Project")

    @pytest.fixture
    def sample_scenario(self):
        """Create a sample scenario."""
        from civil_toolbox.domain.scenario import Scenario
        return Scenario(name="Test Scenario")

    def test_project_summary_without_project_required_raises(self):
        """Required project_summary without project raises error."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext()

        with pytest.raises(ContextValidationError) as exc_info:
            validate_template_context(template, context)

        assert exc_info.value.section_id == "proj"
        assert exc_info.value.requirement == "project"

    def test_project_summary_without_project_optional_warns(self):
        """Optional project_summary without project returns warning."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                    required=False,
                ),
            ],
        )
        context = ReportTemplateContext()

        warnings = validate_template_context(template, context)
        assert len(warnings) == 1
        assert "proj" in warnings[0]

    def test_project_summary_with_project_passes(self, sample_project):
        """project_summary with project passes."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext(project=sample_project)

        warnings = validate_template_context(template, context)
        assert len(warnings) == 0

    def test_scenario_summary_without_scenario_required_raises(self):
        """Required scenario_summary without scenario raises error."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="scen",
                    title="Scenario",
                    section_type="scenario_summary",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext()

        with pytest.raises(ContextValidationError) as exc_info:
            validate_template_context(template, context)

        assert exc_info.value.requirement == "scenario"

    def test_scenario_summary_with_scenario_passes(self, sample_scenario):
        """scenario_summary with scenario passes."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="scen",
                    title="Scenario",
                    section_type="scenario_summary",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext(scenario=sample_scenario)

        warnings = validate_template_context(template, context)
        assert len(warnings) == 0

    def test_comparison_section_without_comparison_required_raises(self):
        """Required comparison section without comparison raises error."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="comp",
                    title="Comparison",
                    section_type="comparison_summary",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext()

        with pytest.raises(ContextValidationError) as exc_info:
            validate_template_context(template, context)

        assert exc_info.value.requirement == "comparison"

    def test_custom_text_without_content_required_raises(self):
        """Required custom_text without content raises error."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="custom",
                    title="Custom Section",
                    section_type="custom_text",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext()

        with pytest.raises(ContextValidationError) as exc_info:
            validate_template_context(template, context)

        assert exc_info.value.section_id == "custom"

    def test_custom_text_with_content_passes(self):
        """custom_text with content passes."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="custom",
                    title="Custom Section",
                    section_type="custom_text",
                    required=True,
                ),
            ],
        )
        context = ReportTemplateContext(
            custom_sections={"custom": "Custom content here."},
        )

        warnings = validate_template_context(template, context)
        assert len(warnings) == 0

    def test_custom_text_include_when_empty_passes(self):
        """custom_text with include_when_empty passes without content."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="custom",
                    title="Custom Section",
                    section_type="custom_text",
                    required=True,
                    include_when_empty=True,
                ),
            ],
        )
        context = ReportTemplateContext()

        warnings = validate_template_context(template, context)
        assert len(warnings) == 0

    def test_assumptions_section_no_data_optional_warns(self):
        """Optional assumptions section without data returns warning."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                    required=False,
                ),
            ],
        )
        context = ReportTemplateContext()

        warnings = validate_template_context(template, context)
        assert len(warnings) == 1


class TestCanBuildSection:
    """Tests for can_build_section."""

    @pytest.fixture
    def sample_project(self):
        """Create a sample project."""
        from civil_toolbox.domain.project import Project
        return Project(name="Test Project")

    def test_project_summary_with_project(self, sample_project):
        """project_summary can build with project."""
        section = SectionTemplate(
            id="proj",
            title="Project",
            section_type="project_summary",
        )
        context = ReportTemplateContext(project=sample_project)
        assert can_build_section(section, context) is True

    def test_project_summary_without_project(self):
        """project_summary cannot build without project."""
        section = SectionTemplate(
            id="proj",
            title="Project",
            section_type="project_summary",
        )
        context = ReportTemplateContext()
        assert can_build_section(section, context) is False

    def test_custom_text_with_content(self):
        """custom_text can build with content."""
        section = SectionTemplate(
            id="custom",
            title="Custom",
            section_type="custom_text",
        )
        context = ReportTemplateContext(
            custom_sections={"custom": "Content"},
        )
        assert can_build_section(section, context) is True

    def test_custom_text_without_content(self):
        """custom_text cannot build without content."""
        section = SectionTemplate(
            id="custom",
            title="Custom",
            section_type="custom_text",
        )
        context = ReportTemplateContext()
        assert can_build_section(section, context) is False

    def test_custom_text_include_when_empty(self):
        """custom_text with include_when_empty can build without content."""
        section = SectionTemplate(
            id="custom",
            title="Custom",
            section_type="custom_text",
            include_when_empty=True,
        )
        context = ReportTemplateContext()
        assert can_build_section(section, context) is True

    def test_assumptions_always_buildable(self):
        """assumptions section is always buildable."""
        section = SectionTemplate(
            id="assumptions",
            title="Assumptions",
            section_type="assumptions",
        )
        context = ReportTemplateContext()
        assert can_build_section(section, context) is True


class TestSectionRequirements:
    """Tests for SECTION_REQUIREMENTS mapping."""

    def test_project_sections_require_project(self):
        """Project-related sections require project."""
        assert SECTION_REQUIREMENTS.get("project_summary") == "project"

    def test_scenario_sections_require_scenario(self):
        """Scenario-related sections require scenario."""
        assert SECTION_REQUIREMENTS.get("scenario_summary") == "scenario"
        assert SECTION_REQUIREMENTS.get("calculation_summary") == "scenario"
        assert SECTION_REQUIREMENTS.get("calculation_appendix") == "scenario"

    def test_comparison_sections_require_comparison(self):
        """Comparison-related sections require comparison."""
        assert SECTION_REQUIREMENTS.get("comparison_summary") == "comparison"
        assert SECTION_REQUIREMENTS.get("comparison_table") == "comparison"
        assert SECTION_REQUIREMENTS.get("comparison_totals") == "comparison"

    def test_utility_sections_no_requirements(self):
        """Utility sections have no requirements."""
        assert SECTION_REQUIREMENTS.get("assumptions") is None
        assert SECTION_REQUIREMENTS.get("warnings") is None
        assert SECTION_REQUIREMENTS.get("references") is None
