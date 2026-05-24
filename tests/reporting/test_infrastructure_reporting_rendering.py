"""Tests for infrastructure reporting rendering (Markdown and PDF compatibility)."""

import pytest

from civil_toolbox.infrastructure import (
    InfrastructureNetwork,
    InfrastructureNode,
    Pipe,
    Inlet,
    DetentionFacility,
    StageStoragePoint,
)
from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult
from civil_toolbox.reporting import (
    ReportTemplate,
    SectionTemplate,
    ReportTemplateContext,
    build_report_from_template,
    render_full_report_markdown,
    get_default_template_registry,
)
from civil_toolbox.reporting.templates import render_report_html, render_report_to_html_document


class TestInfrastructureMarkdownRendering:
    """Tests for infrastructure report Markdown rendering."""

    @pytest.fixture
    def sample_network(self):
        """Create a comprehensive sample network."""
        network = InfrastructureNetwork(id="net1", name="Downtown Drainage")

        network.add_node(InfrastructureNode(id="n1", name="MH-1"))
        network.add_node(InfrastructureNode(id="n2", name="MH-2"))
        network.add_node(InfrastructureNode(id="n3", name="Outfall"))

        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=250.0,
            slope_ft_per_ft=0.005,
            mannings_n=0.013,
            material="RCP",
            upstream_node_id="n1",
            downstream_node_id="n2",
            metadata={"status": "existing"},
        ))
        network.add_element(Pipe(
            id="p2", name="P-2",
            diameter_in=24.0, length_ft=180.0,
            slope_ft_per_ft=0.008,
            mannings_n=0.013,
            material="RCP",
            upstream_node_id="n2",
            downstream_node_id="n3",
            metadata={"status": "proposed"},
        ))
        network.add_element(Inlet(
            id="i1", name="I-1",
            inlet_type="grate",
            node_id="n1",
            metadata={"status": "existing"},
        ))
        network.add_element(DetentionFacility(
            id="d1", name="DP-1",
            facility_type="detention",
            stage_storage=[
                StageStoragePoint(stage_ft=0.0, storage_cuft=0),
                StageStoragePoint(stage_ft=4.0, storage_cuft=40000),
            ],
            outlet_node_id="n3",
            metadata={"status": "proposed"},
        ))

        return network

    @pytest.fixture
    def sample_check_results(self):
        """Create sample check results."""
        results = []

        r1 = InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
            capacity_cfs=12.5, design_flow_cfs=8.0,
            velocity_fps=4.2,
            method="Manning's equation (full flow)",
        )
        r1.add_assumption("Full-flow capacity assumed")
        r1.add_assumption("No inlet/outlet losses")
        results.append(r1)

        r2 = InfrastructureCheckResult(
            element_id="p2", element_name="P-2",
            element_type="pipe", passes=False,
            capacity_cfs=18.0, design_flow_cfs=22.0,
            velocity_fps=6.8,
            method="Manning's equation (full flow)",
        )
        r2.add_warning("OVERCAPACITY", "Design flow exceeds capacity")
        r2.add_assumption("Full-flow capacity assumed")
        results.append(r2)

        r3 = InfrastructureCheckResult(
            element_id="d1", element_name="DP-1",
            element_type="detention", passes=True,
            storage_cuft=40000, required_storage_cuft=35000,
            method="Volume comparison",
        )
        r3.add_assumption("Routing not performed")
        r3.add_warning("ROUTING_REQUIRED", "Detailed routing analysis recommended")
        results.append(r3)

        return results

    def test_infrastructure_summary_renders_to_markdown(self, sample_network):
        """Infrastructure summary renders to Markdown."""
        template = ReportTemplate(
            id="test", name="Test", version="1.0",
            sections=[
                SectionTemplate(
                    id="summary", title="Infrastructure Summary",
                    section_type="infrastructure_summary",
                ),
            ],
        )
        context = ReportTemplateContext(infrastructure_network=sample_network)
        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert "Infrastructure Summary" in markdown
        assert "Pipes" in markdown

    def test_pipe_schedule_renders_to_markdown(self, sample_network):
        """Pipe schedule renders to Markdown table."""
        template = ReportTemplate(
            id="test", name="Test", version="1.0",
            sections=[
                SectionTemplate(
                    id="pipes", title="Pipe Schedule",
                    section_type="pipe_schedule",
                ),
            ],
        )
        context = ReportTemplateContext(infrastructure_network=sample_network)
        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert "P-1" in markdown
        assert "P-2" in markdown
        assert "18" in markdown or "18.0" in markdown
        assert "RCP" in markdown

    def test_check_summary_renders_to_markdown(self, sample_network, sample_check_results):
        """Check summary renders to Markdown."""
        template = ReportTemplate(
            id="test", name="Test", version="1.0",
            sections=[
                SectionTemplate(
                    id="checks", title="Sizing Checks",
                    section_type="infrastructure_check_summary",
                ),
            ],
        )
        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )
        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert "PASS" in markdown
        assert "FAIL" in markdown

    def test_warnings_render_to_markdown(self, sample_network, sample_check_results):
        """Warnings render to Markdown list."""
        template = ReportTemplate(
            id="test", name="Test", version="1.0",
            sections=[
                SectionTemplate(
                    id="warnings", title="Warnings",
                    section_type="infrastructure_warnings",
                ),
            ],
        )
        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )
        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert "OVERCAPACITY" in markdown or "ROUTING_REQUIRED" in markdown

    def test_assumptions_render_to_markdown(self, sample_network, sample_check_results):
        """Assumptions render to Markdown list."""
        template = ReportTemplate(
            id="test", name="Test", version="1.0",
            sections=[
                SectionTemplate(
                    id="assumptions", title="Assumptions",
                    section_type="infrastructure_assumptions",
                ),
            ],
        )
        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )
        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert "Full-flow" in markdown

    def test_full_infrastructure_report_renders(self, sample_network, sample_check_results):
        """Full infrastructure report renders successfully."""
        registry = get_default_template_registry()
        template = registry.get("infrastructure_summary_report")

        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )

        report = build_report_from_template(template, context)
        markdown = render_full_report_markdown(report)

        assert len(markdown) > 100
        assert "Infrastructure Summary" in markdown


class TestInfrastructureHtmlRendering:
    """Tests for infrastructure report HTML rendering."""

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
        return [InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
            capacity_cfs=15.0, design_flow_cfs=10.0,
        )]

    def test_infrastructure_report_renders_to_html(self, sample_network, sample_check_results):
        """Infrastructure report renders to HTML."""
        template = ReportTemplate(
            id="test", name="Test", version="1.0",
            sections=[
                SectionTemplate(
                    id="summary", title="Infrastructure Summary",
                    section_type="infrastructure_summary",
                ),
                SectionTemplate(
                    id="checks", title="Sizing Checks",
                    section_type="infrastructure_check_summary",
                ),
            ],
        )
        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )
        report = build_report_from_template(template, context)
        html = render_report_html(report)

        assert "<" in html
        assert "p1" in html or "Pipes" in html

    def test_infrastructure_report_renders_to_html_document(
        self, sample_network, sample_check_results
    ):
        """Infrastructure report renders to complete HTML document."""
        template = ReportTemplate(
            id="test", name="Test Infrastructure Report", version="1.0",
            sections=[
                SectionTemplate(
                    id="summary", title="Infrastructure Summary",
                    section_type="infrastructure_summary",
                ),
            ],
        )
        context = ReportTemplateContext(
            infrastructure_network=sample_network,
            infrastructure_check_results=sample_check_results,
        )
        report = build_report_from_template(template, context)
        html_doc = render_report_to_html_document(report)

        assert "<!DOCTYPE html>" in html_doc or "<html" in html_doc
        assert "Test Infrastructure Report" in html_doc


class TestTableFormattingRules:
    """Tests for table formatting rules."""

    @pytest.fixture
    def network_with_missing_values(self):
        """Create network with missing optional values."""
        network = InfrastructureNetwork(id="net1", name="Test")
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))
        return network

    def test_missing_values_render_as_dash(self, network_with_missing_values):
        """Missing optional values render as dash."""
        from civil_toolbox.reporting.infrastructure_tables import build_pipe_schedule_table

        table = build_pipe_schedule_table(network_with_missing_values)
        row = table.rows[0]

        assert "—" in row

    def test_deterministic_row_ordering(self):
        """Rows are ordered deterministically."""
        network = InfrastructureNetwork(id="net1", name="Test")

        network.add_element(Pipe(
            id="z", name="Z-Pipe",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))
        network.add_element(Pipe(
            id="a", name="A-Pipe",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))

        from civil_toolbox.reporting.infrastructure_tables import build_pipe_schedule_table

        table1 = build_pipe_schedule_table(network)
        table2 = build_pipe_schedule_table(network)

        assert table1.rows == table2.rows
        assert table1.rows[0][1] == "A-Pipe"

    def test_empty_table_still_renders_headers(self):
        """Empty table still renders headers."""
        empty_network = InfrastructureNetwork(id="net1", name="Empty")

        from civil_toolbox.reporting.infrastructure_tables import build_pipe_schedule_table

        table = build_pipe_schedule_table(empty_network)
        assert len(table.headers) > 0
        assert len(table.rows) == 0


class TestNumericPrecision:
    """Tests for numeric precision in tables."""

    def test_flow_values_have_one_decimal(self):
        """Flow values display with one decimal place."""
        results = [InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
            capacity_cfs=12.567, design_flow_cfs=8.234,
        )]

        from civil_toolbox.reporting.infrastructure_tables import (
            build_infrastructure_check_summary_table
        )

        table = build_infrastructure_check_summary_table(results)
        capacity_cell = table.rows[0][4]

        assert "12.6" in capacity_cell

    def test_slope_values_have_four_decimals(self):
        """Slope values display with four decimal places."""
        network = InfrastructureNetwork(id="net1", name="Test")
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.00512,
        ))

        from civil_toolbox.reporting.infrastructure_tables import build_pipe_schedule_table

        table = build_pipe_schedule_table(network)
        slope_cell = table.rows[0][8]

        assert "0051" in slope_cell or "0.0051" in slope_cell
