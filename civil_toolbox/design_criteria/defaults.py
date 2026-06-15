"""Default value contract for jurisdiction-driven defaults (Phase A).

Pure, headless, kernel-side. A ``DefaultValue`` is what a ``JurisdictionAuthority``
returns from ``default_for(parameter_id, ...)``: the resolved value plus its
provenance (which jurisdiction, what units, optional citation).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DefaultValue:
    """A jurisdiction-resolved default for a registered parameter.

    Attributes:
        parameter_id: Registered parameter ID (see PARAMETER_NAMESPACE.md).
        value: The default value (type per the parameter's schema).
        source_jurisdiction_id: ID of the jurisdiction that supplied this default.
        units: Units string, if material (e.g. "ft", "years").
        citation: Optional source citation (manual section, etc.).
    """

    parameter_id: str
    value: Any
    source_jurisdiction_id: str
    units: str | None = None
    citation: str | None = None
