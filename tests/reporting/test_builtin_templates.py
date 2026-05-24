"""Tests for built-in report templates."""

import pytest

from civil_toolbox.reporting.builtins import (
    get_builtin_templates,
    get_default_template_registry,
)
from civil_toolbox.reporting.report_templates import ReportTemplate
from civil_toolbox.reporting.template_validation import validate_template


class TestGetBuiltinTemplates:
    """Tests for get_builtin_templates."""

    def test_returns_list_of_templates(self):
        """Returns a list of ReportTemplate objects."""
        templates = get_builtin_templates()
        assert isinstance(templates, list)
        assert len(templates) > 0
        for template in templates:
            assert isinstance(template, ReportTemplate)

    def test_all_builtin_ids_unique(self):
        """All built-in templates have unique IDs."""
        templates = get_builtin_templates()
        ids = [t.id for t in templates]
        assert len(ids) == len(set(ids))

    def test_all_builtins_validate(self):
        """All built-in templates pass validation."""
        templates = get_builtin_templates()
        for template in templates:
            validate_template(template)

    def test_expected_templates_present(self):
        """Expected built-in templates are present."""
        templates = get_builtin_templates()
        ids = {t.id for t in templates}

        assert "project_summary" in ids
        assert "scenario_comparison" in ids
        assert "drainage_calculation_appendix" in ids
        assert "combined_drainage_report" in ids

    def test_templates_are_serializable(self):
        """All built-in templates serialize and deserialize."""
        templates = get_builtin_templates()
        for template in templates:
            data = template.to_dict()
            restored = ReportTemplate.from_dict(data)
            assert restored.id == template.id
            assert restored.name == template.name

    def test_returns_fresh_list(self):
        """Returns a fresh list each time."""
        templates1 = get_builtin_templates()
        templates2 = get_builtin_templates()
        assert templates1 is not templates2


class TestGetDefaultTemplateRegistry:
    """Tests for get_default_template_registry."""

    def test_returns_populated_registry(self):
        """Returns a registry with built-in templates."""
        registry = get_default_template_registry()
        assert len(registry) > 0

    def test_contains_all_builtins(self):
        """Registry contains all built-in templates."""
        registry = get_default_template_registry()
        templates = get_builtin_templates()

        for template in templates:
            assert registry.has_template(template.id)

    def test_returns_fresh_registry(self):
        """Returns a fresh registry each time."""
        registry1 = get_default_template_registry()
        registry2 = get_default_template_registry()
        assert registry1 is not registry2

    def test_modifications_dont_affect_new_registries(self):
        """Modifying one registry doesn't affect new ones."""
        registry1 = get_default_template_registry()
        original_count = len(registry1)
        registry1.clear()

        registry2 = get_default_template_registry()
        assert len(registry2) == original_count


class TestProjectSummaryTemplate:
    """Tests for the project_summary built-in template."""

    @pytest.fixture
    def template(self):
        """Get the project_summary template."""
        registry = get_default_template_registry()
        return registry.get("project_summary")

    def test_has_project_summary_section(self, template):
        """Template has a project_summary section."""
        section_types = {s.section_type for s in template.sections}
        assert "project_summary" in section_types

    def test_formatting_profile_is_standard(self, template):
        """Uses standard formatting profile."""
        assert template.formatting_profile == "standard"

    def test_sections_are_ordered(self, template):
        """Sections have explicit ordering."""
        ordered = template.get_ordered_sections()
        assert len(ordered) == len(template.sections)


class TestScenarioComparisonTemplate:
    """Tests for the scenario_comparison built-in template."""

    @pytest.fixture
    def template(self):
        """Get the scenario_comparison template."""
        registry = get_default_template_registry()
        return registry.get("scenario_comparison")

    def test_has_comparison_sections(self, template):
        """Template has comparison-related sections."""
        section_types = {s.section_type for s in template.sections}
        assert "comparison_summary" in section_types
        assert "comparison_table" in section_types

    def test_project_info_is_optional(self, template):
        """Project info section is optional."""
        for section in template.sections:
            if section.section_type == "project_summary":
                assert section.required is False


class TestDrainageCalculationAppendixTemplate:
    """Tests for the drainage_calculation_appendix built-in template."""

    @pytest.fixture
    def template(self):
        """Get the drainage_calculation_appendix template."""
        registry = get_default_template_registry()
        return registry.get("drainage_calculation_appendix")

    def test_has_calculation_sections(self, template):
        """Template has calculation-related sections."""
        section_types = {s.section_type for s in template.sections}
        assert "calculation_summary" in section_types
        assert "calculation_appendix" in section_types

    def test_formatting_profile_is_appendix_heavy(self, template):
        """Uses appendix_heavy formatting profile."""
        assert template.formatting_profile == "appendix_heavy"


class TestCombinedDrainageReportTemplate:
    """Tests for the combined_drainage_report built-in template."""

    @pytest.fixture
    def template(self):
        """Get the combined_drainage_report template."""
        registry = get_default_template_registry()
        return registry.get("combined_drainage_report")

    def test_has_both_sections_and_appendices(self, template):
        """Template has both sections and appendices."""
        assert len(template.sections) > 0
        assert len(template.appendices) > 0

    def test_most_sections_are_optional(self, template):
        """Most sections are optional for flexibility."""
        optional_count = sum(
            1 for s in template.sections + template.appendices
            if not s.required
        )
        total_count = len(template.sections) + len(template.appendices)
        assert optional_count > total_count / 2

    def test_appendix_sections_include_calculations(self, template):
        """Appendices include calculation details."""
        appendix_types = {a.section_type for a in template.appendices}
        assert "calculation_appendix" in appendix_types


class TestBuiltinTemplateConsistency:
    """Tests for consistency across built-in templates."""

    def test_all_have_version(self):
        """All built-in templates have a version."""
        for template in get_builtin_templates():
            assert template.version
            assert template.version.strip() != ""

    def test_all_have_description(self):
        """All built-in templates have a description."""
        for template in get_builtin_templates():
            assert template.description is not None

    def test_section_ids_unique_within_each_template(self):
        """Section IDs are unique within each template."""
        for template in get_builtin_templates():
            all_ids = [s.id for s in template.sections + template.appendices]
            assert len(all_ids) == len(set(all_ids)), f"Duplicate IDs in {template.id}"

    def test_section_orders_are_deterministic(self):
        """Section ordering is deterministic across calls."""
        templates1 = get_builtin_templates()
        templates2 = get_builtin_templates()

        for t1, t2 in zip(templates1, templates2):
            ordered1 = [s.id for s in t1.get_ordered_sections()]
            ordered2 = [s.id for s in t2.get_ordered_sections()]
            assert ordered1 == ordered2
