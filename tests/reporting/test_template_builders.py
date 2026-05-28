"""Tests for template-based report builders."""

import pytest

from civil_toolbox.reporting.report_templates import (
    ReportTemplate,
    SectionTemplate,
)
from civil_toolbox.reporting.template_context import ReportTemplateContext
from civil_toolbox.reporting.template_builders import (
    build_report_from_template,
    TemplateBuildError,
)
from civil_toolbox.reporting.models import Report, ReportType
from civil_toolbox.reporting.markdown import render_full_report_markdown


class TestBuildReportFromTemplate:
    """Tests for build_report_from_template."""

    @pytest.fixture
    def sample_project(self):
        """Create a sample project."""
        from civil_toolbox.domain.project import Project
        return Project(name="Test Project", description="A test project")

    @pytest.fixture
    def sample_scenario(self):
        """Create a sample scenario."""
        from civil_toolbox.domain.scenario import Scenario
        return Scenario(name="Test Scenario", description="A test scenario")

    @pytest.fixture
    def simple_template(self):
        """Create a simple template."""
        return ReportTemplate(
            id="simple",
            name="Simple Report",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project Information",
                    section_type="project_summary",
                ),
            ],
        )

    def test_build_simple_report(self, simple_template, sample_project):
        """Build a simple report from template."""
        context = ReportTemplateContext(project=sample_project)
        report = build_report_from_template(simple_template, context)

        assert isinstance(report, Report)
        assert report.metadata.title == "Simple Report"
        assert report.metadata.project_name == "Test Project"
        assert len(report.sections) > 0

    def test_report_type_is_project_summary_default(self, simple_template, sample_project):
        """Default report type is PROJECT_SUMMARY."""
        context = ReportTemplateContext(project=sample_project)
        report = build_report_from_template(simple_template, context)

        assert report.metadata.report_type == ReportType.PROJECT_SUMMARY

    def test_report_type_is_scenario_comparison(self):
        """Report type is SCENARIO_COMPARISON when comparison section present."""
        from civil_toolbox.domain.scenario import Scenario
        from civil_toolbox.comparison.models import (
            ScenarioComparisonResult,
            MatchStrategy,
        )

        template = ReportTemplate(
            id="comparison",
            name="Comparison Report",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="comp",
                    title="Comparison",
                    section_type="comparison_summary",
                ),
            ],
        )

        comparison = ScenarioComparisonResult(
            baseline_scenario_id="baseline-id",
            baseline_scenario_name="Baseline",
            comparison_scenario_id="comparison-id",
            comparison_scenario_name="Comparison",
            storm_event_name=None,
            match_strategy=MatchStrategy.AUTO,
            entity_comparisons=[],
        )

        context = ReportTemplateContext(comparison=comparison)
        report = build_report_from_template(template, context)

        assert report.metadata.report_type == ReportType.SCENARIO_COMPARISON

    def test_build_with_optional_sections(self, sample_project):
        """Optional sections are skipped when data is missing."""
        template = ReportTemplate(
            id="optional",
            name="Optional Sections",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                ),
                SectionTemplate(
                    id="scen",
                    title="Scenario",
                    section_type="scenario_summary",
                    required=False,
                ),
            ],
        )

        context = ReportTemplateContext(project=sample_project)
        report = build_report_from_template(template, context)

        section_titles = [s.title for s in report.sections if s.title]
        assert "Project" in section_titles
        assert "Scenario" not in section_titles

    def test_build_with_required_missing_raises(self):
        """Required section with missing data raises error."""
        template = ReportTemplate(
            id="required",
            name="Required Section",
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

        with pytest.raises(Exception):
            build_report_from_template(template, context)

    def test_sections_ordered_correctly(self, sample_project, sample_scenario):
        """Sections appear in order specified by template."""
        template = ReportTemplate(
            id="ordered",
            name="Ordered Report",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="c",
                    title="Third",
                    section_type="assumptions",
                    order=30,
                    required=False,
                ),
                SectionTemplate(
                    id="a",
                    title="First",
                    section_type="project_summary",
                    order=10,
                ),
                SectionTemplate(
                    id="b",
                    title="Second",
                    section_type="scenario_summary",
                    order=20,
                ),
            ],
        )

        context = ReportTemplateContext(
            project=sample_project,
            scenario=sample_scenario,
            assumptions=["Test assumption"],
        )
        report = build_report_from_template(template, context)

        heading_titles = [
            s.title for s in report.sections
            if s.section_type.value == "heading" and s.title
        ]
        assert heading_titles.index("First") < heading_titles.index("Second")
        assert heading_titles.index("Second") < heading_titles.index("Third")

    def test_output_renders_to_markdown(self, simple_template, sample_project):
        """Report can be rendered to Markdown."""
        context = ReportTemplateContext(project=sample_project)
        report = build_report_from_template(simple_template, context)

        markdown = render_full_report_markdown(report)
        assert "Simple Report" in markdown
        assert "Test Project" in markdown

    def test_build_with_appendices(self, sample_scenario):
        """Template with appendices includes appendix sections."""
        template = ReportTemplate(
            id="with_appendix",
            name="Report with Appendix",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="calc_summary",
                    title="Calculation Summary",
                    section_type="calculation_summary",
                ),
            ],
            appendices=[
                SectionTemplate(
                    id="calc_appendix",
                    title="Calculation Details",
                    section_type="calculation_appendix",
                ),
            ],
        )

        context = ReportTemplateContext(scenario=sample_scenario)
        report = build_report_from_template(template, context)

        section_titles = [s.title for s in report.sections if s.title]
        assert "Appendices" in section_titles
        assert "Calculation Details" in section_titles

    def test_custom_text_section(self, sample_project):
        """Custom text section uses content from context."""
        template = ReportTemplate(
            id="custom",
            name="Custom Report",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="intro",
                    title="Introduction",
                    section_type="custom_text",
                ),
            ],
        )

        context = ReportTemplateContext(
            project=sample_project,
            custom_sections={"intro": "This is the introduction text."},
        )
        report = build_report_from_template(template, context)

        markdown = render_full_report_markdown(report)
        assert "Introduction" in markdown
        assert "This is the introduction text." in markdown

    def test_assumptions_aggregated(self, sample_scenario):
        """Assumptions are aggregated from context."""
        template = ReportTemplate(
            id="assumptions",
            name="Report with Assumptions",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="calc_summary",
                    title="Calculation Summary",
                    section_type="calculation_summary",
                ),
                SectionTemplate(
                    id="assumptions",
                    title="Assumptions",
                    section_type="assumptions",
                ),
            ],
        )

        context = ReportTemplateContext(
            scenario=sample_scenario,
            assumptions=["Steady state", "Uniform rainfall"],
        )
        report = build_report_from_template(template, context)

        markdown = render_full_report_markdown(report)
        assert "Assumptions" in markdown
        assert "Steady state" in markdown

    def test_metadata_includes_author(self, simple_template, sample_project):
        """Report metadata includes author from context."""
        context = ReportTemplateContext(
            project=sample_project,
            metadata={"author": "Test Author", "organization": "Test Org"},
        )
        report = build_report_from_template(simple_template, context)

        assert report.metadata.author == "Test Author"
        assert report.metadata.organization == "Test Org"


class TestTemplateBuildError:
    """Tests for TemplateBuildError."""

    def test_error_message(self):
        """Error includes message."""
        error = TemplateBuildError("Build failed")
        assert "Build failed" in str(error)

    def test_error_section_id_attribute(self):
        """Error has section_id attribute."""
        error = TemplateBuildError("Build failed", section_id="section1")
        assert error.section_id == "section1"

    def test_error_section_id_none(self):
        """Error section_id can be None."""
        error = TemplateBuildError("Build failed")
        assert error.section_id is None


class TestBuiltInSectionBuilders:
    """Tests for individual section builders."""

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

    def test_project_summary_builder(self, sample_project):
        """project_summary builder creates project info."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project Information",
                    section_type="project_summary",
                ),
            ],
        )
        context = ReportTemplateContext(project=sample_project)
        report = build_report_from_template(template, context)

        markdown = render_full_report_markdown(report)
        assert "Test Project" in markdown

    def test_scenario_summary_builder(self, sample_scenario):
        """scenario_summary builder creates scenario info."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="scen",
                    title="Scenario Overview",
                    section_type="scenario_summary",
                ),
            ],
        )
        context = ReportTemplateContext(scenario=sample_scenario)
        report = build_report_from_template(template, context)

        markdown = render_full_report_markdown(report)
        assert "Test Scenario" in markdown

    def test_warnings_builder_empty_skipped(self, sample_project):
        """warnings builder with no warnings skips section."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                ),
                SectionTemplate(
                    id="warnings",
                    title="Warnings",
                    section_type="warnings",
                    required=False,
                ),
            ],
        )
        context = ReportTemplateContext(
            project=sample_project,
            warnings=[],
        )
        report = build_report_from_template(template, context)

        section_titles = [s.title for s in report.sections if s.title]
        assert "Warnings" not in section_titles

    def test_warnings_builder_include_when_empty(self, sample_project):
        """warnings builder with include_when_empty shows section."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                ),
                SectionTemplate(
                    id="warnings",
                    title="Warnings",
                    section_type="warnings",
                    required=False,
                    include_when_empty=True,
                ),
            ],
        )
        context = ReportTemplateContext(project=sample_project)
        report = build_report_from_template(template, context)

        section_titles = [s.title for s in report.sections if s.title]
        assert "Warnings" in section_titles

    def test_references_builder(self, sample_project):
        """references builder creates reference list."""
        template = ReportTemplate(
            id="test",
            name="Test",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="proj",
                    title="Project",
                    section_type="project_summary",
                ),
                SectionTemplate(
                    id="refs",
                    title="References",
                    section_type="references",
                ),
            ],
        )
        context = ReportTemplateContext(
            project=sample_project,
            references=[
                {"title": "TR-55", "source": "NRCS", "year": "1986"},
            ],
        )
        report = build_report_from_template(template, context)

        markdown = render_full_report_markdown(report)
        assert "TR-55" in markdown
