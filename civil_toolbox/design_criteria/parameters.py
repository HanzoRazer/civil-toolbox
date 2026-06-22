"""Parameter schema and context contracts (Phase A).

Pure, headless, kernel-side. ``ParameterSchema`` describes a registered parameter;
``PHASE_A_PARAMETERS`` is the in-code schema set that the namespace-registry CI
test cross-checks against ``docs/PARAMETER_NAMESPACE.md`` §4.1.

Every ``ParameterSchema.parameter_id`` MUST be a registered, well-formed ID.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from civil_toolbox.design_criteria.parameter_registry import is_valid_parameter_id


@dataclass(frozen=True)
class ParameterContext:
    """Context that may influence default resolution.

    Optional fields, all defaulted, so the ``default_for`` signature stays stable
    as later phases add context.
    """

    project_type: str | None = None
    petition_type: str | None = None
    drainage_area_ac: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParameterSchema:
    """Schema for a single registered parameter.

    Field order keeps ``parameter_id`` and ``value_type`` positional; everything
    else is keyword/defaulted. The richer presentation fields (name, help_text,
    valid_range, citation) feed the Phase A validation/UI layer (later slices).

    Attributes:
        parameter_id: Registered parameter ID (must pass namespace format rules).
        value_type: Logical type label ("str", "float", "tuple[int]", "enum").
        units: Units string when material, else None.
        required: Whether the parameter is always required.
        description: Short technical description.
        name: Human-friendly label (for UI).
        help_text: Longer plain-language help (for UI tooltips).
        valid_range: Optional inclusive (min, max) numeric range.
        citation: Optional source citation.
    """

    parameter_id: str
    value_type: str
    units: str | None = None
    required: bool = False
    description: str = ""
    name: str = ""
    help_text: str = ""
    valid_range: tuple[float, float] | None = None
    citation: str | None = None

    def __post_init__(self) -> None:
        if not is_valid_parameter_id(self.parameter_id):
            raise ValueError(
                f"Invalid parameter_id '{self.parameter_id}': must match the "
                "namespace format and a canonical domain prefix "
                "(see PARAMETER_NAMESPACE.md)."
            )


# Phase A schemas — one per registry row in PARAMETER_NAMESPACE.md §4.1.
PHASE_A_PARAMETERS: tuple[ParameterSchema, ...] = (
    ParameterSchema(
        "project_name", "str", required=True, description="Project name",
        name="Project Name", help_text="The name of this drainage project.",
    ),
    ParameterSchema(
        "project_site_name", "str", description="Site / development name",
        name="Site Name", help_text="Development or site name, if applicable.",
    ),
    ParameterSchema(
        "project_site_address", "str", description="Site address",
        name="Site Address",
    ),
    ParameterSchema(
        "project_parcel_id", "str", description="Parcel identifier (HCAD)",
        name="Parcel ID", help_text="Harris County Appraisal District parcel ID.",
    ),
    ParameterSchema(
        "project_latitude_deg", "float", units="deg",
        description="WGS84 latitude (decimal degrees)",
        name="Latitude", help_text="WGS84 decimal degrees.",
        valid_range=(-90.0, 90.0),
    ),
    ParameterSchema(
        "project_longitude_deg", "float", units="deg",
        description="WGS84 longitude (decimal degrees)",
        name="Longitude", help_text="WGS84 decimal degrees.",
        valid_range=(-180.0, 180.0),
    ),
    ParameterSchema(
        "project_jurisdiction_id", "enum", required=True,
        description="Registered jurisdiction ID",
        name="Jurisdiction", help_text="The governing jurisdiction for design criteria.",
    ),
    ParameterSchema(
        "project_design_storms_years", "tuple[int]", units="years", required=True,
        description="Return periods to analyze",
        name="Design Storms", help_text="Return periods (years) to analyze.",
    ),
    ParameterSchema(
        "project_freeboard_ft", "float", units="ft",
        description="Freeboard above design WSE",
        name="Freeboard", help_text="Vertical margin above the design water surface.",
        valid_range=(0.0, 100.0),
    ),
    ParameterSchema(
        "project_status", "enum",
        description="Lifecycle status (system-managed)",
        name="Status", help_text="Project lifecycle status; managed by the system.",
    ),
)

_SCHEMA_BY_ID: dict[str, ParameterSchema] = {s.parameter_id: s for s in PHASE_A_PARAMETERS}


def get_parameter_schema(parameter_id: str) -> ParameterSchema | None:
    """Return the schema for a parameter ID, or None if not defined."""
    return _SCHEMA_BY_ID.get(parameter_id)


def parameters_required_by(jurisdiction_id: str) -> tuple[str, ...]:
    """Return the required parameter IDs for a jurisdiction (empty if unknown)."""
    # Lazy import to avoid a cycle (jurisdictions import this module).
    from civil_toolbox.design_criteria.jurisdictions import get_authority

    authority = get_authority(jurisdiction_id)
    return authority.parameters_required() if authority is not None else ()
