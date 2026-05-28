"""Template context for report assembly.

The context provides all data needed to build a report from a template
without making template builders depend on global state.

Example:
    >>> from civil_toolbox.reporting.template_context import ReportTemplateContext
    >>> context = ReportTemplateContext(
    ...     project=my_project,
    ...     scenario=my_scenario,
    ... )
    >>> context.has_project()
    True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from civil_toolbox.domain.project import Project
    from civil_toolbox.domain.scenario import Scenario
    from civil_toolbox.comparison.models import ScenarioComparisonResult
    from civil_toolbox.comparison.storm_sensitivity import StormSensitivityResult
    from civil_toolbox.infrastructure import InfrastructureNetwork
    from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult


@dataclass
class ReportTemplateContext:
    """Context for building reports from templates.

    Holds all data needed to populate template sections.
    Does not mutate any supplied domain objects.

    Attributes:
        project: Optional project for project-related sections.
        scenario: Optional scenario for scenario-related sections.
        comparison: Optional comparison result for comparison sections.
        storm_sensitivity: Optional storm sensitivity result for sensitivity sections.
        infrastructure_network: Optional infrastructure network for infrastructure sections.
        infrastructure_check_results: Optional list of sizing check results.
        metadata: Additional metadata for the report.
        custom_sections: Custom text content keyed by section ID.
        assumptions: Global assumptions to include.
        warnings: Global warnings to include.
        references: Global references to include.
    """

    project: Project | None = None
    scenario: Scenario | None = None
    comparison: ScenarioComparisonResult | None = None
    storm_sensitivity: StormSensitivityResult | None = None
    infrastructure_network: InfrastructureNetwork | None = None
    infrastructure_check_results: list[InfrastructureCheckResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    custom_sections: dict[str, str] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    references: list[dict[str, str]] = field(default_factory=list)

    def has_project(self) -> bool:
        """Check if project data is available."""
        return self.project is not None

    def has_scenario(self) -> bool:
        """Check if scenario data is available."""
        return self.scenario is not None

    def has_comparison(self) -> bool:
        """Check if comparison data is available."""
        return self.comparison is not None

    def has_storm_sensitivity(self) -> bool:
        """Check if storm sensitivity data is available."""
        return self.storm_sensitivity is not None

    def has_infrastructure_network(self) -> bool:
        """Check if infrastructure network data is available."""
        return self.infrastructure_network is not None

    def has_infrastructure_check_results(self) -> bool:
        """Check if infrastructure check results are available."""
        return len(self.infrastructure_check_results) > 0

    def get_custom_section(self, section_id: str) -> str | None:
        """Get custom section text by ID.

        Args:
            section_id: The section identifier.

        Returns:
            Custom text if available, None otherwise.
        """
        return self.custom_sections.get(section_id)

    def get_all_assumptions(self) -> list[str]:
        """Collect all assumptions from context and scenario.

        Returns:
            Deduplicated list of assumption strings.
        """
        all_assumptions = set(self.assumptions)

        if self.scenario:
            for result in self.scenario.calculation_results:
                for assumption in result.assumptions:
                    all_assumptions.add(assumption.description)

        return sorted(all_assumptions)

    def get_all_warnings(self) -> list[str]:
        """Collect all warnings from context and scenario.

        Returns:
            Deduplicated list of warning strings.
        """
        all_warnings = set(self.warnings)

        if self.scenario:
            for result in self.scenario.calculation_results:
                for warning in result.warnings:
                    all_warnings.add(warning.message)

        return sorted(all_warnings)

    def get_all_references(self) -> list[dict[str, str]]:
        """Collect all references from context and scenario.

        Returns:
            Deduplicated list of reference dictionaries.
        """
        seen_refs = set()
        all_refs = []

        for ref in self.references:
            ref_key = (ref.get("title", ""), ref.get("source", ""))
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                all_refs.append(ref)

        if self.scenario:
            for result in self.scenario.calculation_results:
                for ref in result.references:
                    ref_key = (ref.title, ref.source)
                    if ref_key not in seen_refs:
                        seen_refs.add(ref_key)
                        all_refs.append({
                            "title": ref.title,
                            "source": ref.source,
                            "year": str(ref.year) if ref.year else None,
                        })

        return all_refs
