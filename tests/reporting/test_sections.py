"""Tests for section building utilities."""

import pytest

from civil_toolbox.reporting.sections import (
    create_heading,
    create_text,
    create_list,
    create_table_section,
    create_figure_placeholder,
    create_project_metadata_section,
    create_scenario_summary_section,
    create_comparison_summary_section,
    create_comparison_totals_section,
    create_assumptions_section,
    create_warnings_section,
    create_references_section,
)
from civil_toolbox.reporting.models import (
    ReportTable,
    SectionType,
)
from civil_toolbox.domain.project import Project
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.comparison.models import (
    ScenarioComparisonResult,
    MatchStrategy,
    ComparisonMetric,
    ScenarioTotals,
    PercentDeltaStatus,
)


class TestCreateHeading:
    """Tests for create_heading."""

    def test_creates_heading_section(self):
        """Creates a heading section."""
        section = create_heading("Introduction", level=2)

        assert section.section_type == SectionType.HEADING
        assert section.title == "Introduction"
        assert section.level == 2

    def test_default_level(self):
        """Default level is 2."""
        section = create_heading("Test")
        assert section.level == 2

    def test_custom_level(self):
        """Supports custom level."""
        section = create_heading("Deep", level=4)
        assert section.level == 4


class TestCreateText:
    """Tests for create_text."""

    def test_creates_text_section(self):
        """Creates a text section."""
        section = create_text("This is a paragraph.")

        assert section.section_type == SectionType.TEXT
        assert section.content == "This is a paragraph."


class TestCreateList:
    """Tests for create_list."""

    def test_creates_list_section(self):
        """Creates a list section."""
        section = create_list(["Item 1", "Item 2", "Item 3"])

        assert section.section_type == SectionType.LIST
        assert len(section.items) == 3

    def test_with_title(self):
        """Supports optional title."""
        section = create_list(["A", "B"], title="Options")
        assert section.title == "Options"


class TestCreateTableSection:
    """Tests for create_table_section."""

    def test_creates_table_section(self):
        """Creates a table section."""
        table = ReportTable(headers=["A"], rows=[["1"]])
        section = create_table_section(table)

        assert section.section_type == SectionType.TABLE
        assert section.table is not None
        assert section.table.headers == ["A"]


class TestCreateFigurePlaceholder:
    """Tests for create_figure_placeholder."""

    def test_creates_figure_section(self):
        """Creates a figure placeholder section."""
        section = create_figure_placeholder(
            figure_id="fig-1",
            caption="Site Plan",
            description="Shows drainage boundaries",
        )

        assert section.section_type == SectionType.FIGURE_PLACEHOLDER
        assert section.figure is not None
        assert section.figure.figure_id == "fig-1"
        assert section.figure.caption == "Site Plan"


class TestCreateProjectMetadataSection:
    """Tests for create_project_metadata_section."""

    def test_creates_metadata_section(self):
        """Creates project metadata section."""
        project = Project(name="Test Project")
        section = create_project_metadata_section(project)

        assert section.section_type == SectionType.METADATA
        assert section.table is not None
        assert section.table.title == "Project Information"

    def test_includes_project_name(self):
        """Includes project name in table."""
        project = Project(name="My Project")
        section = create_project_metadata_section(project)

        rows = section.table.rows
        name_row = [r for r in rows if r[0] == "Project Name"][0]
        assert name_row[1] == "My Project"


class TestCreateScenarioSummarySection:
    """Tests for create_scenario_summary_section."""

    def test_creates_summary_section(self):
        """Creates scenario summary section."""
        scenario = Scenario(name="Existing")
        section = create_scenario_summary_section(scenario)

        assert section.section_type == SectionType.SUMMARY
        assert section.table is not None

    def test_includes_entity_counts(self):
        """Includes counts of entities."""
        scenario = Scenario(name="Test")
        scenario.add_drainage_area(DrainageArea(name="Area A"))
        scenario.add_drainage_area(DrainageArea(name="Area B"))

        section = create_scenario_summary_section(scenario)
        rows = section.table.rows

        areas_row = [r for r in rows if r[0] == "Drainage Areas"][0]
        assert areas_row[1] == "2"


class TestCreateComparisonSummarySection:
    """Tests for create_comparison_summary_section."""

    def test_creates_comparison_summary(self):
        """Creates comparison summary section."""
        comparison = ScenarioComparisonResult(
            baseline_scenario_id="s1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="s2",
            comparison_scenario_name="Proposed",
            storm_event_name="100-year",
            match_strategy=MatchStrategy.AUTO,
            entity_comparisons=[],
            unmatched_baseline_ids=["orphan-1"],
            unmatched_comparison_ids=[],
        )
        section = create_comparison_summary_section(comparison)

        assert section.section_type == SectionType.SUMMARY
        assert section.table is not None

    def test_includes_scenario_names(self):
        """Includes scenario names."""
        comparison = ScenarioComparisonResult(
            baseline_scenario_id="s1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="s2",
            comparison_scenario_name="Proposed",
            storm_event_name=None,
            match_strategy=MatchStrategy.AUTO,
        )
        section = create_comparison_summary_section(comparison)
        rows = section.table.rows

        baseline_row = [r for r in rows if r[0] == "Baseline Scenario"][0]
        assert baseline_row[1] == "Existing"


class TestCreateComparisonTotalsSection:
    """Tests for create_comparison_totals_section."""

    def test_creates_totals_section(self):
        """Creates totals section."""
        comparison = ScenarioComparisonResult(
            baseline_scenario_id="s1",
            baseline_scenario_name="Existing",
            comparison_scenario_id="s2",
            comparison_scenario_name="Proposed",
            storm_event_name=None,
            match_strategy=MatchStrategy.AUTO,
            totals={
                ComparisonMetric.PEAK_FLOW_CFS: ScenarioTotals(
                    metric=ComparisonMetric.PEAK_FLOW_CFS,
                    baseline_total=300.0,
                    comparison_total=370.0,
                    delta=70.0,
                    percent_delta=23.3,
                    unit="cfs",
                    entity_count=2,
                ),
            },
        )
        section = create_comparison_totals_section(comparison)

        assert section.section_type == SectionType.TABLE
        assert section.table is not None
        assert len(section.table.rows) == 1


class TestCreateAssumptionsSection:
    """Tests for create_assumptions_section."""

    def test_creates_assumptions_section(self):
        """Creates assumptions section."""
        assumptions = [
            "Steady-state conditions assumed",
            "Uniform rainfall distribution",
        ]
        section = create_assumptions_section(assumptions)

        assert section.section_type == SectionType.ASSUMPTIONS
        assert len(section.items) == 2

    def test_default_title(self):
        """Default title is 'Assumptions'."""
        section = create_assumptions_section(["Test"])
        assert section.title == "Assumptions"

    def test_custom_title(self):
        """Supports custom title."""
        section = create_assumptions_section(["Test"], title="Key Assumptions")
        assert section.title == "Key Assumptions"


class TestCreateWarningsSection:
    """Tests for create_warnings_section."""

    def test_creates_warnings_section(self):
        """Creates warnings section."""
        warnings = [
            "Area exceeds Rational Method limit",
            "CN estimated from generic land use",
        ]
        section = create_warnings_section(warnings)

        assert section.section_type == SectionType.WARNINGS
        assert len(section.items) == 2


class TestCreateReferencesSection:
    """Tests for create_references_section."""

    def test_creates_references_section(self):
        """Creates references section."""
        references = [
            {"title": "TR-55", "source": "NRCS", "year": "1986"},
            {"title": "HEC-22", "source": "FHWA", "year": "2009"},
        ]
        section = create_references_section(references)

        assert section.section_type == SectionType.REFERENCES
        assert len(section.items) == 2

    def test_formats_reference_string(self):
        """Formats reference as string."""
        references = [{"title": "TR-55", "source": "NRCS", "year": "1986"}]
        section = create_references_section(references)

        assert "TR-55" in section.items[0]
        assert "NRCS" in section.items[0]
        assert "1986" in section.items[0]
