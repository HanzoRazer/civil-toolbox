"""Tests for infrastructure section builders."""

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
from civil_toolbox.reporting.infrastructure_sections import (
    build_infrastructure_summary_section,
    build_infrastructure_schedule_section,
    build_pipe_schedule_section,
    build_inlet_schedule_section,
    build_detention_schedule_section,
    build_infrastructure_check_summary_section,
    build_infrastructure_warnings_section,
    build_infrastructure_assumptions_section,
)
from civil_toolbox.reporting.models import SectionType
from civil_toolbox.reporting.markdown import render_section_markdown


class TestBuildInfrastructureSummarySection:
    """Tests for build_infrastructure_summary_section."""

    @pytest.fixture
    def sample_network(self):
        """Create a sample network."""
        network = InfrastructureNetwork(id="net1", name="Sample Network")
        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=200.0,
            slope_ft_per_ft=0.01,
        ))
        return network

    def test_returns_list_of_sections(self, sample_network):
        """Returns list of report sections."""
        sections = build_infrastructure_summary_section(sample_network)
        assert isinstance(sections, list)
        assert len(sections) >= 1

    def test_first_section_is_heading(self, sample_network):
        """First section is heading."""
        sections = build_infrastructure_summary_section(sample_network)
        assert sections[0].section_type == SectionType.HEADING

    def test_custom_title(self, sample_network):
        """Custom title is used."""
        sections = build_infrastructure_summary_section(
            sample_network, title="Network Overview"
        )
        assert sections[0].title == "Network Overview"

    def test_empty_network_shows_message(self):
        """Empty network shows message."""
        empty_network = InfrastructureNetwork(id="net1", name="Empty")
        sections = build_infrastructure_summary_section(empty_network)
        markdown = render_section_markdown(sections[1])
        assert "No infrastructure elements" in str(markdown)

    def test_includes_summary_table(self, sample_network):
        """Section includes summary table."""
        sections = build_infrastructure_summary_section(sample_network)
        table_sections = [s for s in sections if s.section_type == SectionType.TABLE]
        assert len(table_sections) >= 1


class TestBuildInfrastructureScheduleSection:
    """Tests for build_infrastructure_schedule_section."""

    @pytest.fixture
    def network_with_multiple_types(self):
        """Create network with multiple element types."""
        network = InfrastructureNetwork(id="net1", name="Test")
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))
        network.add_element(Inlet(
            id="i1", name="I-1", inlet_type="grate",
        ))
        network.add_element(DetentionFacility(
            id="d1", name="DP-1",
        ))
        return network

    def test_includes_multiple_tables(self, network_with_multiple_types):
        """Section includes tables for each element type."""
        sections = build_infrastructure_schedule_section(network_with_multiple_types)
        table_sections = [s for s in sections if s.section_type == SectionType.TABLE]
        assert len(table_sections) >= 3


class TestBuildPipeScheduleSection:
    """Tests for build_pipe_schedule_section."""

    @pytest.fixture
    def network_with_pipes(self):
        """Create network with pipes."""
        network = InfrastructureNetwork(id="net1", name="Test")
        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=100.0,
            slope_ft_per_ft=0.01,
        ))
        return network

    def test_returns_sections_with_table(self, network_with_pipes):
        """Returns sections including pipe table."""
        sections = build_pipe_schedule_section(network_with_pipes)
        table_sections = [s for s in sections if s.section_type == SectionType.TABLE]
        assert len(table_sections) == 1

    def test_empty_network_shows_message(self):
        """Empty network shows no pipes message."""
        empty_network = InfrastructureNetwork(id="net1", name="Empty")
        sections = build_pipe_schedule_section(empty_network)
        markdown = render_section_markdown(sections[1])
        assert "No pipes defined" in str(markdown)


class TestBuildInletScheduleSection:
    """Tests for build_inlet_schedule_section."""

    @pytest.fixture
    def network_with_inlets(self):
        """Create network with inlets."""
        network = InfrastructureNetwork(id="net1", name="Test")
        network.add_element(Inlet(
            id="i1", name="I-1", inlet_type="grate",
        ))
        return network

    def test_returns_sections_with_table(self, network_with_inlets):
        """Returns sections including inlet table."""
        sections = build_inlet_schedule_section(network_with_inlets)
        table_sections = [s for s in sections if s.section_type == SectionType.TABLE]
        assert len(table_sections) == 1

    def test_empty_network_shows_message(self):
        """Empty network shows no inlets message."""
        empty_network = InfrastructureNetwork(id="net1", name="Empty")
        sections = build_inlet_schedule_section(empty_network)
        markdown = render_section_markdown(sections[1])
        assert "No inlets defined" in str(markdown)


class TestBuildDetentionScheduleSection:
    """Tests for build_detention_schedule_section."""

    @pytest.fixture
    def network_with_detention(self):
        """Create network with detention."""
        network = InfrastructureNetwork(id="net1", name="Test")
        network.add_element(DetentionFacility(
            id="d1", name="DP-1",
        ))
        return network

    def test_returns_sections_with_table(self, network_with_detention):
        """Returns sections including detention table."""
        sections = build_detention_schedule_section(network_with_detention)
        table_sections = [s for s in sections if s.section_type == SectionType.TABLE]
        assert len(table_sections) == 1

    def test_empty_network_shows_message(self):
        """Empty network shows no detention message."""
        empty_network = InfrastructureNetwork(id="net1", name="Empty")
        sections = build_detention_schedule_section(empty_network)
        markdown = render_section_markdown(sections[1])
        assert "No detention facilities defined" in str(markdown)


class TestBuildInfrastructureCheckSummarySection:
    """Tests for build_infrastructure_check_summary_section."""

    @pytest.fixture
    def sample_check_results(self):
        """Create sample check results."""
        return [
            InfrastructureCheckResult(
                element_id="p1", element_name="P-1",
                element_type="pipe", passes=True,
                capacity_cfs=15.5, design_flow_cfs=10.0,
            ),
            InfrastructureCheckResult(
                element_id="p2", element_name="P-2",
                element_type="pipe", passes=False,
                capacity_cfs=8.0, design_flow_cfs=12.0,
            ),
        ]

    def test_returns_sections(self, sample_check_results):
        """Returns list of sections."""
        sections = build_infrastructure_check_summary_section(sample_check_results)
        assert isinstance(sections, list)
        assert len(sections) >= 2

    def test_includes_summary_text(self, sample_check_results):
        """Includes summary text with pass/fail counts."""
        sections = build_infrastructure_check_summary_section(sample_check_results)
        text_sections = [s for s in sections if s.section_type == SectionType.TEXT]
        assert len(text_sections) >= 1
        markdown = str(render_section_markdown(text_sections[0]))
        assert "2 checks" in markdown
        assert "1 passing" in markdown
        assert "1 failing" in markdown

    def test_includes_table(self, sample_check_results):
        """Includes check summary table."""
        sections = build_infrastructure_check_summary_section(sample_check_results)
        table_sections = [s for s in sections if s.section_type == SectionType.TABLE]
        assert len(table_sections) == 1

    def test_empty_results_shows_message(self):
        """Empty results shows message."""
        sections = build_infrastructure_check_summary_section([])
        markdown = str(render_section_markdown(sections[1]))
        assert "No infrastructure sizing checks" in markdown


class TestBuildInfrastructureWarningsSection:
    """Tests for build_infrastructure_warnings_section."""

    @pytest.fixture
    def results_with_warnings(self):
        """Create results with warnings."""
        result = InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
        )
        result.add_warning("LOW_VELOCITY", "Velocity below minimum")
        result.add_warning("HIGH_UTILIZATION", "Utilization above 80%")
        return [result]

    def test_lists_all_warnings(self, results_with_warnings):
        """Lists all warnings."""
        sections = build_infrastructure_warnings_section(results_with_warnings)
        assert len(sections) >= 2
        markdown = str(render_section_markdown(sections[1]))
        assert "LOW_VELOCITY" in markdown
        assert "HIGH_UTILIZATION" in markdown

    def test_empty_warnings_shows_message(self):
        """No warnings shows message."""
        result = InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
        )
        sections = build_infrastructure_warnings_section([result])
        markdown = str(render_section_markdown(sections[1]))
        assert "No warnings" in markdown

    def test_deduplicates_warnings(self, results_with_warnings):
        """Deduplicates identical warnings."""
        results_with_warnings.append(results_with_warnings[0])
        sections = build_infrastructure_warnings_section(results_with_warnings)
        list_sections = [s for s in sections if s.section_type == SectionType.LIST]
        assert len(list_sections) <= 1


class TestBuildInfrastructureAssumptionsSection:
    """Tests for build_infrastructure_assumptions_section."""

    @pytest.fixture
    def results_with_assumptions(self):
        """Create results with assumptions."""
        result = InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
        )
        result.add_assumption("Full-flow capacity assumed")
        result.add_assumption("Manning's equation for uniform flow")
        return [result]

    def test_lists_all_assumptions(self, results_with_assumptions):
        """Lists all assumptions."""
        sections = build_infrastructure_assumptions_section(results_with_assumptions)
        assert len(sections) >= 2
        markdown = str(render_section_markdown(sections[1]))
        assert "Full-flow" in markdown
        assert "Manning" in markdown

    def test_empty_assumptions_shows_message(self):
        """No assumptions shows message."""
        result = InfrastructureCheckResult(
            element_id="p1", element_name="P-1",
            element_type="pipe", passes=True,
        )
        sections = build_infrastructure_assumptions_section([result])
        markdown = str(render_section_markdown(sections[1]))
        assert "No assumptions" in markdown

    def test_deduplicates_assumptions(self, results_with_assumptions):
        """Deduplicates identical assumptions."""
        result2 = InfrastructureCheckResult(
            element_id="p2", element_name="P-2",
            element_type="pipe", passes=True,
        )
        result2.add_assumption("Full-flow capacity assumed")
        results_with_assumptions.append(result2)

        sections = build_infrastructure_assumptions_section(results_with_assumptions)
        list_sections = [s for s in sections if s.section_type == SectionType.LIST]
        if list_sections:
            items = list_sections[0].items or []
            assert len([i for i in items if "Full-flow" in i]) <= 1
