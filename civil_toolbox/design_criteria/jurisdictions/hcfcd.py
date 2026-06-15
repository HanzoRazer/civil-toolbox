"""Harris County Flood Control District (HCFCD) jurisdiction authority (Phase A).

Pure, headless. Defaults per PARAMETER_NAMESPACE.md §4.1. Future-scope sections
return empty tuples per SPEC §4.2.
"""

from __future__ import annotations

from civil_toolbox.design_criteria.defaults import DefaultValue
from civil_toolbox.design_criteria.jurisdiction_authority import (
    ReportSection,
    ValidationRule,
)
from civil_toolbox.design_criteria.parameters import ParameterContext

_HCFCD_DESIGN_STORMS: tuple[int, ...] = (2, 5, 10, 25, 100)
_HCFCD_FREEBOARD_FT: float = 1.0
_HCFCD_CITATION = "HCFCD Hydrology and Hydraulics Guidance Manual (current revision)"

# HCFCD requires the always-required set plus freeboard.
_HCFCD_REQUIRED: tuple[str, ...] = (
    "project_name",
    "project_jurisdiction_id",
    "project_design_storms_years",
    "project_freeboard_ft",
)


class HCFCDAuthority:
    """Authority encoding HCFCD's Phase A design defaults and requirements."""

    jurisdiction_id: str = "hcfcd"
    display_name: str = "Harris County Flood Control District"

    def default_for(
        self,
        parameter_id: str,
        context: ParameterContext | None = None,
    ) -> DefaultValue | None:
        if parameter_id == "project_design_storms_years":
            return DefaultValue(
                parameter_id=parameter_id,
                value=_HCFCD_DESIGN_STORMS,
                source_jurisdiction_id=self.jurisdiction_id,
                units="years",
                citation=_HCFCD_CITATION,
            )
        if parameter_id == "project_freeboard_ft":
            return DefaultValue(
                parameter_id=parameter_id,
                value=_HCFCD_FREEBOARD_FT,
                source_jurisdiction_id=self.jurisdiction_id,
                units="ft",
                citation=_HCFCD_CITATION,
            )
        return None

    def default_parameter_ids(self) -> tuple[str, ...]:
        """Parameter IDs for which this authority supplies a default."""
        return ("project_design_storms_years", "project_freeboard_ft")

    def parameters_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[str, ...]:
        return _HCFCD_REQUIRED

    def design_storms_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[int, ...]:
        return _HCFCD_DESIGN_STORMS

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
