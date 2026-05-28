"""Tests for report template context."""

import pytest

from civil_toolbox.reporting.template_context import ReportTemplateContext


class TestReportTemplateContext:
    """Tests for ReportTemplateContext."""

    def test_empty_context_is_valid(self):
        """Empty context with no data is valid."""
        context = ReportTemplateContext()
        assert context.project is None
        assert context.scenario is None
        assert context.comparison is None
        assert context.metadata == {}
        assert context.custom_sections == {}

    def test_has_project_false_when_none(self):
        """has_project returns False when project is None."""
        context = ReportTemplateContext()
        assert context.has_project() is False

    def test_has_scenario_false_when_none(self):
        """has_scenario returns False when scenario is None."""
        context = ReportTemplateContext()
        assert context.has_scenario() is False

    def test_has_comparison_false_when_none(self):
        """has_comparison returns False when comparison is None."""
        context = ReportTemplateContext()
        assert context.has_comparison() is False

    def test_metadata_preserved(self):
        """Metadata dictionary is preserved."""
        context = ReportTemplateContext(
            metadata={"author": "Test Author", "organization": "Test Org"},
        )
        assert context.metadata["author"] == "Test Author"
        assert context.metadata["organization"] == "Test Org"

    def test_custom_section_lookup(self):
        """Custom section text can be retrieved by ID."""
        context = ReportTemplateContext(
            custom_sections={
                "intro": "Introduction text here.",
                "notes": "Additional notes.",
            },
        )
        assert context.get_custom_section("intro") == "Introduction text here."
        assert context.get_custom_section("notes") == "Additional notes."

    def test_missing_custom_section_returns_none(self):
        """Missing custom section returns None."""
        context = ReportTemplateContext(
            custom_sections={"intro": "Text"},
        )
        assert context.get_custom_section("nonexistent") is None

    def test_assumptions_list(self):
        """Assumptions list is accessible."""
        context = ReportTemplateContext(
            assumptions=["Steady state conditions", "Uniform rainfall"],
        )
        assert len(context.assumptions) == 2

    def test_warnings_list(self):
        """Warnings list is accessible."""
        context = ReportTemplateContext(
            warnings=["Area exceeds limit", "Check input values"],
        )
        assert len(context.warnings) == 2

    def test_references_list(self):
        """References list is accessible."""
        context = ReportTemplateContext(
            references=[
                {"title": "TR-55", "source": "NRCS", "year": "1986"},
            ],
        )
        assert len(context.references) == 1
        assert context.references[0]["title"] == "TR-55"

    def test_get_all_assumptions_without_scenario(self):
        """get_all_assumptions returns context assumptions when no scenario."""
        context = ReportTemplateContext(
            assumptions=["Assumption 1", "Assumption 2"],
        )
        assumptions = context.get_all_assumptions()
        assert "Assumption 1" in assumptions
        assert "Assumption 2" in assumptions

    def test_get_all_warnings_without_scenario(self):
        """get_all_warnings returns context warnings when no scenario."""
        context = ReportTemplateContext(
            warnings=["Warning 1"],
        )
        warnings = context.get_all_warnings()
        assert "Warning 1" in warnings

    def test_get_all_references_without_scenario(self):
        """get_all_references returns context references when no scenario."""
        context = ReportTemplateContext(
            references=[{"title": "Manual", "source": "Publisher"}],
        )
        references = context.get_all_references()
        assert len(references) == 1
        assert references[0]["title"] == "Manual"

    def test_get_all_references_deduplicates(self):
        """get_all_references removes duplicates."""
        context = ReportTemplateContext(
            references=[
                {"title": "Manual", "source": "Publisher"},
                {"title": "Manual", "source": "Publisher"},
            ],
        )
        references = context.get_all_references()
        assert len(references) == 1


class TestContextWithDomainObjects:
    """Tests for context with domain objects."""

    @pytest.fixture
    def sample_project(self):
        """Create a sample project for testing."""
        from civil_toolbox.domain.project import Project
        return Project(name="Test Project")

    @pytest.fixture
    def sample_scenario(self):
        """Create a sample scenario for testing."""
        from civil_toolbox.domain.scenario import Scenario
        return Scenario(name="Test Scenario")

    def test_has_project_true_when_set(self, sample_project):
        """has_project returns True when project is set."""
        context = ReportTemplateContext(project=sample_project)
        assert context.has_project() is True

    def test_has_scenario_true_when_set(self, sample_scenario):
        """has_scenario returns True when scenario is set."""
        context = ReportTemplateContext(scenario=sample_scenario)
        assert context.has_scenario() is True

    def test_project_not_mutated(self, sample_project):
        """Context does not mutate project."""
        original_name = sample_project.name
        context = ReportTemplateContext(project=sample_project)
        _ = context.has_project()
        assert sample_project.name == original_name

    def test_scenario_not_mutated(self, sample_scenario):
        """Context does not mutate scenario."""
        original_name = sample_scenario.name
        context = ReportTemplateContext(scenario=sample_scenario)
        _ = context.has_scenario()
        assert sample_scenario.name == original_name
