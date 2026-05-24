"""Tests for infrastructure template integration."""

import pytest

from civil_toolbox.infrastructure import (
    InfrastructureNetwork,
    InfrastructureNode,
    Pipe,
    Inlet,
    DetentionFacility,
)
from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult
from civil_toolbox.reporting import (
    ReportTemplate,
    SectionTemplate,
    ReportTemplateContext,
    build_report_from_template,
    validate_template,
    validate_template_context,
    can_build_section,
    get_default_template_registry,
    render_full_report_markdown,
)


class TestInfrastructureContextHelpers:
    """Tests for infrastructure context helper methods."""

    @pytest.fixture
    def sample_network(self):
        """Create a sample network."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))
        return network

    @pytest.fixture
    def sample_check_results(self):
        """Create sample check results."""
        return [
            InfrastructureCheckResult(
                element_id="p1", element_name="P-1",
                element_type="pipe", passes=True,
            )
        ]

    def test_has_infrastructure_network_true(self, sample_network):
        """has_infrastructure_network returns True when set."""
        context = ReportTemplateContext(infrastructure_network=sample_network)
        assert context.has_infrastructure_network() is True

    def test_has_infrastructure_network_false(self):
        """has_infrastructure_network returns False when not set."""
        context = ReportTemplateContext()
        assert context.has_infrastructure_network() is False

    def test_has_infrastructure_check_results_true(self, sample_check_results):
        """has_infrastructure_check_results returns True when set."""
        context = ReportTemplateContext(infrastructure_check_results=sample_check_results)
        assert context.has_infrastructure_check_results() is True

    def test_has_infrastructure_check_results_false(self):
        """has_infrastructure_check_results returns False when empty."""
        context = ReportTemplateContext()
        assert context.has_infrastructure_check_results() is False


class TestInfrastructureSectionTypes:
    """Tests for infrastructure section type validation."""

    def test_infrastructure_summary_in_supported_types(self):
        """infrastructure_summary is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "infrastructure_summary" in SUPPORTED_SECTION_TYPES

    def test_infrastructure_schedule_in_supported_types(self):
        """infrastructure_schedule is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "infrastructure_schedule" in SUPPORTED_SECTION_TYPES

    def test_pipe_schedule_in_supported_types(self):
        """pipe_schedule is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "pipe_schedule" in SUPPORTED_SECTION_TYPES

    def test_inlet_schedule_in_supported_types(self):
        """inlet_schedule is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "inlet_schedule" in SUPPORTED_SECTION_TYPES

    def test_detention_schedule_in_supported_types(self):
        """detention_schedule is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "detention_schedule" in SUPPORTED_SECTION_TYPES

    def test_infrastructure_check_summary_in_supported_types(self):
        """infrastructure_check_summary is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "infrastructure_check_summary" in SUPPORTED_SECTION_TYPES

    def test_infrastructure_warnings_in_supported_types(self):
        """infrastructure_warnings is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "infrastructure_warnings" in SUPPORTED_SECTION_TYPES

    def test_infrastructure_assumptions_in_supported_types(self):
        """infrastructure_assumptions is a supported section type."""
        from civil_toolbox.reporting.report_templates import SUPPORTED_SECTION_TYPES
        assert "infrastructure_assumptions" in SUPPORTED_SECTION_TYPES


class TestCanBuildInfrastructureSections:
    """Tests for can_build_section with infrastructure sections."""

    @pytest.fixture
    def sample_network(self):
        """Create a sample network."""
        return InfrastructureNetwork(id="net1", name="Test")

    @pytest.fixture
    def sample_check_results(self):
        """Create sample check results."""
        return [InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
        )]

    def test_infrastructure_summary_with_network(self, sample_network):
        """infrastructure_summary can build with network."""
        section = SectionTemplate(
            id="infra", title="Infrastructure",
            section_type="infrastructure_summary",
        )
        context = ReportTemplateContext(infrastructure_network=sample_network)
        assert can_build_section(section, context) is True

    def test_infrastructure_summary_without_network(self):
        """infrastructure_summary cannot build without network."""
        section = SectionTemplate(
            id="infra", title="Infrastructure",
            section_type="infrastructure_summary",
        )
        context = ReportTemplateContext()
        assert can_build_section(section, context) is False

    def test_infrastructure_check_summary_with_results(self, sample_check_results):
        """infrastructure_check_summary can build with results."""
        section = SectionTemplate(
            id="checks", title="Checks",
            section_type="infrastructure_check_summary",
        )
        context = ReportTemplateContext(
            infrastructure_check_results=sample_check_results
        )
        assert can_build_section(section, context) is True

    def test_infrastructure_check_summary_without_results(self):
        """infrastructure_check_summary cannot build without results."""
        section = SectionTemplate(
            id="checks", title="Checks",
            section_type="infrastructure_check_summary",
        )
        context = ReportTemplateContext()
        assert can_build_section(section, context) is False


class TestBuildReportWithInfrastructureSections:
    """Tests for building reports with infrastructure sections."""

    @pytest.fixture
    def sample_network(self):
        """Create a sample network."""
        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=200.0,
            slope_ft_per_ft=0.01,
            upstream_node_id="n1",
        ))
        network.add_element(Inlet(
            id="i1", name="I-1", inlet_type="grate", node_id="n1",
        ))
        return network

    @pytest.fixture
    def sample_check_results(self):
        """Create sample check results."""
        result = InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
            capacity_cfs=15.5, design_flow_cfs=10.0,
            method="Manning's equation",
        )
        result.add_assumption("Full-flow capacity assumed")
        result.add_warning("LOW_VELOCITY", "Velocity below 2.0 fps")
        return [result]

    def test_build_infrastructure_summary_report(self, sample_network, sample_check_results):
        """Build report with infrastructure summary section."""
        template = ReportTemplate(
            id="test_infra",
            name="Infrastructure Test Report",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="summary",
                    title="Infrastructure Summary",
                    section_type="infrastructure_summary",
                ),
            ],
        )

        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )

        report = build_report_from_template(template, context)
        assert report is not None
        assert len(report.sections) >= 2

    def test_build_with_all_infrastructure_sections(self, sample_network, sample_check_results):
        """Build report with all infrastructure section types."""
        template = ReportTemplate(
            id="full_infra",
            name="Full Infrastructure Report",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="summary", title="Summary",
                    section_type="infrastructure_summary", order=10,
                ),
                SectionTemplate(
                    id="schedule", title="Schedule",
                    section_type="infrastructure_schedule", order=20,
                ),
                SectionTemplate(
                    id="checks", title="Sizing Checks",
                    section_type="infrastructure_check_summary", order=30,
                ),
                SectionTemplate(
                    id="warnings", title="Warnings",
                    section_type="infrastructure_warnings", order=40,
                ),
                SectionTemplate(
                    id="assumptions", title="Assumptions",
                    section_type="infrastructure_assumptions", order=50,
                ),
            ],
            appendices=[
                SectionTemplate(
                    id="pipes", title="Pipe Schedule",
                    section_type="pipe_schedule", order=10,
                ),
                SectionTemplate(
                    id="inlets", title="Inlet Schedule",
                    section_type="inlet_schedule", order=20,
                ),
            ],
        )

        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )

        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert "Infrastructure Summary" in markdown or "Summary" in markdown
        assert "P-1" in markdown

    def test_optional_infrastructure_sections_skip_when_missing(self):
        """Optional infrastructure sections are skipped when data missing."""
        template = ReportTemplate(
            id="optional_infra",
            name="Optional Infrastructure",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="summary",
                    title="Infrastructure Summary",
                    section_type="infrastructure_summary",
                    required=False,
                ),
                SectionTemplate(
                    id="checks",
                    title="Sizing Checks",
                    section_type="infrastructure_check_summary",
                    required=False,
                ),
                SectionTemplate(
                    id="heading",
                    title="End",
                    section_type="heading",
                ),
            ],
        )

        context = ReportTemplateContext()

        report = build_report_from_template(template, context)
        section_titles = [s.title for s in report.sections if s.title]
        assert "Infrastructure Summary" not in section_titles
        assert "Sizing Checks" not in section_titles

    def test_required_infrastructure_section_raises_when_missing(self):
        """Required infrastructure section raises when data missing."""
        template = ReportTemplate(
            id="required_infra",
            name="Required Infrastructure",
            version="1.0",
            sections=[
                SectionTemplate(
                    id="summary",
                    title="Infrastructure Summary",
                    section_type="infrastructure_summary",
                    required=True,
                ),
            ],
        )

        context = ReportTemplateContext()

        with pytest.raises(Exception):
            build_report_from_template(template, context)


class TestInfrastructureSummaryReportBuiltin:
    """Tests for the infrastructure_summary_report builtin template."""

    def test_infrastructure_summary_report_in_registry(self):
        """infrastructure_summary_report is in default registry."""
        registry = get_default_template_registry()
        assert "infrastructure_summary_report" in registry

    def test_infrastructure_summary_report_validates(self):
        """infrastructure_summary_report validates successfully."""
        registry = get_default_template_registry()
        template = registry.get("infrastructure_summary_report")
        validate_template(template)

    def test_infrastructure_summary_report_has_expected_sections(self):
        """infrastructure_summary_report has expected sections."""
        registry = get_default_template_registry()
        template = registry.get("infrastructure_summary_report")

        section_types = {s.section_type for s in template.sections}
        assert "infrastructure_summary" in section_types

    def test_infrastructure_summary_report_has_appendices(self):
        """infrastructure_summary_report has appendices."""
        registry = get_default_template_registry()
        template = registry.get("infrastructure_summary_report")

        assert len(template.appendices) >= 1
        appendix_types = {a.section_type for a in template.appendices}
        assert "pipe_schedule" in appendix_types

    def test_build_infrastructure_summary_report(self):
        """Build infrastructure_summary_report with data."""
        registry = get_default_template_registry()
        template = registry.get("infrastructure_summary_report")

        network = InfrastructureNetwork(id="net1", name="Test Network")
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))

        context = ReportTemplateContext(infrastructure_network=network)

        report = build_report_from_template(template, context)
        assert report is not None

        markdown = render_full_report_markdown(report)
        assert "Infrastructure Summary" in markdown
