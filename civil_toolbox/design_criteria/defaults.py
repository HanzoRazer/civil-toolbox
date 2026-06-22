"""Default value contract for jurisdiction-driven defaults (Phase A).

Pure, headless, kernel-side. A ``DefaultValue`` is what a ``JurisdictionAuthority``
returns from ``default_for(parameter_id, ...)``: the resolved value plus its
provenance (which jurisdiction, what units, optional citation).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from civil_toolbox.design_criteria.parameters import ParameterContext


@dataclass(frozen=True)
class DefaultValue:
    """A jurisdiction-resolved default for a registered parameter.

    ``parameter_id`` and ``source_jurisdiction_id`` are retained (against the
    handoff's leaner shape) for auditability/traceability, consistent with the
    rest of the codebase. ``applicability_notes`` is added per the handoff.

    Attributes:
        parameter_id: Registered parameter ID (see PARAMETER_NAMESPACE.md).
        value: The default value (type per the parameter's schema).
        source_jurisdiction_id: ID of the jurisdiction that supplied this default.
        units: Units string, if material (e.g. "ft", "years").
        citation: Optional source citation (manual section, etc.).
        applicability_notes: Caveats / conditions under which the default applies.
    """

    parameter_id: str
    value: Any
    source_jurisdiction_id: str
    units: str | None = None
    citation: str | None = None
    applicability_notes: tuple[str, ...] = ()


def default_for(
    jurisdiction_id: str,
    parameter_id: str,
    context: "ParameterContext | None" = None,
) -> DefaultValue | None:
    """Resolve a default for a parameter under a jurisdiction.

    Convenience dispatch over the jurisdiction authorities. Returns ``None`` for
    an unknown jurisdiction or a parameter with no jurisdiction-specific default
    (never raises — see PARAMETER_NAMESPACE.md §5).
    """
    # Lazy import to avoid a cycle (jurisdictions import this module).
    from civil_toolbox.design_criteria.jurisdictions import get_authority

    authority = get_authority(jurisdiction_id)
    if authority is None:
        return None
    return authority.default_for(parameter_id, context)
