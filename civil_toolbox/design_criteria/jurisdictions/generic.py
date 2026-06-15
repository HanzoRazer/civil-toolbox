"""Generic (default) jurisdiction authority (Phase A).

Pure, headless. Provides conservative cross-jurisdiction defaults. Future-scope
sections (validations, reports, calc methods) return empty tuples per SPEC §4.2.
"""

from __future__ import annotations

from civil_toolbox.design_criteria.defaults import DefaultValue
from civil_toolbox.design_criteria.jurisdiction_authority import (
    ReportSection,
    ValidationRule,
)
from civil_toolbox.design_criteria.parameters import ParameterContext

# Generic analyzes a minimal storm set.
_GENERIC_DESIGN_STORMS: tuple[int, ...] = (10, 100)

# Always-required project parameters (PARAMETER_NAMESPACE.md §4.1, "Always").
_GENERIC_REQUIRED: tuple[str, ...] = (
    "project_name",
    "project_jurisdiction_id",
    "project_design_storms_years",
)


class GenericAuthority:
    """Default authority used when no jurisdiction-specific rules apply."""

    jurisdiction_id: str = "generic"
    display_name: str = "Generic / Default"

    def default_for(
        self,
        parameter_id: str,
        context: ParameterContext | None = None,
    ) -> DefaultValue | None:
        if parameter_id == "project_design_storms_years":
            return DefaultValue(
                parameter_id=parameter_id,
                value=_GENERIC_DESIGN_STORMS,
                source_jurisdiction_id=self.jurisdiction_id,
                units="years",
            )
        return None

    def default_parameter_ids(self) -> tuple[str, ...]:
        """Parameter IDs for which this authority supplies a default."""
        return ("project_design_storms_years",)

    def parameters_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[str, ...]:
        return _GENERIC_REQUIRED

    def design_storms_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[int, ...]:
        return _GENERIC_DESIGN_STORMS

    # --- Future-scope sections (Phase B+): empty in Phase A ---
    def validations_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[ValidationRule, ...]:
        return ()

    def reports_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[ReportSection, ...]:
        return ()

    def calculation_methods_allowed(
        self,
        calc_type: str,
        drainage_area_ac: float,
    ) -> tuple[str, ...]:
        return ()
