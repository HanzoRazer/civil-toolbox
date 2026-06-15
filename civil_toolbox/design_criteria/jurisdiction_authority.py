"""JurisdictionAuthority protocol (SPEC v0.2.1 §4.1).

Pure, headless, kernel-side. One Protocol in Phase A. The objective compound
split trigger (Decision D14) is recorded in the docstring; Phase A fires none of
its conditions, so the split is deferred.

``ValidationRule`` and ``ReportSection`` here are Phase B+ requirement
placeholders (a jurisdiction's required validations / required report sections).
They are intentionally distinct from the delivery-layer
``civil_toolbox.reporting.ReportSection`` — design_criteria is kernel and must not
import the reporting layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from civil_toolbox.design_criteria.defaults import DefaultValue
from civil_toolbox.design_criteria.parameters import ParameterContext


@dataclass(frozen=True)
class ValidationRule:
    """Phase B+ placeholder: a jurisdiction-required validation rule."""

    rule_id: str
    description: str = ""


@dataclass(frozen=True)
class ReportSection:
    """Phase B+ placeholder: a jurisdiction-required report section.

    Distinct from civil_toolbox.reporting.ReportSection (delivery layer).
    """

    section_id: str
    title: str = ""


@runtime_checkable
class JurisdictionAuthority(Protocol):
    """Canonical source of truth for everything a jurisdiction requires.

    Phase A uses default_for(), parameters_required(), and design_storms_required()
    with real behavior. The remaining methods are declared so the contract is
    honest about future scope; Phase A implementations return empty tuples.

    SPLIT TRIGGER (Decision D14): split into DefaultsProvider,
    RequirementsProvider, and DeliverablesProvider (composed via a facade) when
    ANY of:
      1. METHOD COUNT — any one section accumulates >= 4 public methods.
      2. IMPLEMENTATION COUNT — >= 3 JurisdictionAuthority implementations exist.
      3. CALLER SPECIFICITY — >= 2 caller modules each consume only one section.

    Phase A status (locked):
      Section 1 (Values & Defaults):   1 method (default_for)
      Section 2 (Requirements):        3 methods (mostly empty implementations)
      Section 3 (Deliverables):        2 methods (mostly empty implementations)
      Implementations:                 2 (HCFCD, Generic)
      Caller modules:                  1 (validation_ui only)
      Triggers fired:                  NONE  -> split deferred.
    """

    jurisdiction_id: str
    display_name: str

    # === Section 1: Values & Defaults  (future: DefaultsProvider) ===
    def default_for(
        self,
        parameter_id: str,
        context: ParameterContext | None = None,
    ) -> DefaultValue | None: ...

    # === Section 2: Requirements & Validation  (future: RequirementsProvider) ===
    def parameters_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[str, ...]: ...

    def design_storms_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[int, ...]: ...

    def validations_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[ValidationRule, ...]: ...

    # === Section 3: Deliverables  (future: DeliverablesProvider) ===
    def reports_required(
        self,
        petition_type: str | None = None,
    ) -> tuple[ReportSection, ...]: ...

    def calculation_methods_allowed(
        self,
        calc_type: str,
        drainage_area_ac: float,
    ) -> tuple[str, ...]: ...
