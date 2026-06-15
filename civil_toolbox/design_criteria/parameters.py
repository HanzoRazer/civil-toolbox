"""Parameter schema and context contracts (Phase A).

Pure, headless, kernel-side. ``ParameterSchema`` describes a registered parameter
(type, units, whether required); ``PHASE_A_PARAMETERS`` is the in-code schema set
that the namespace-registry CI test cross-checks against
``docs/PARAMETER_NAMESPACE.md`` §4.1.

Every ``ParameterSchema.parameter_id`` MUST be a registered, well-formed ID.
"""

from __future__ import annotations

from dataclasses import dataclass

from civil_toolbox.design_criteria.parameter_registry import is_valid_parameter_id


@dataclass(frozen=True)
class ParameterContext:
    """Context that may influence default resolution.

    Phase A carries petition type and drainage area; both optional. Extended in
    later phases without breaking the ``default_for`` signature.
    """

    petition_type: str | None = None
    drainage_area_ac: float | None = None


@dataclass(frozen=True)
class ParameterSchema:
    """Schema for a single registered parameter.

    Attributes:
        parameter_id: Registered parameter ID (must pass namespace format rules).
        value_type: Logical type label (e.g. "str", "float", "tuple[int]", "enum").
        units: Units string when material to the value, else None.
        required: Whether the parameter is always required (jurisdiction may add more).
        description: Human-readable description.
    """

    parameter_id: str
    value_type: str
    units: str | None = None
    required: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not is_valid_parameter_id(self.parameter_id):
            raise ValueError(
                f"Invalid parameter_id '{self.parameter_id}': must match the "
                "namespace format and a canonical domain prefix "
                "(see PARAMETER_NAMESPACE.md)."
            )


# Phase A schemas — one per registry row in PARAMETER_NAMESPACE.md §4.1.
PHASE_A_PARAMETERS: tuple[ParameterSchema, ...] = (
    ParameterSchema("project_name", "str", required=True, description="Project name"),
    ParameterSchema("project_site_name", "str", description="Site / development name"),
    ParameterSchema("project_site_address", "str", description="Site address"),
    ParameterSchema("project_parcel_id", "str", description="Parcel identifier (HCAD)"),
    ParameterSchema(
        "project_latitude_deg", "float", units="deg",
        description="WGS84 latitude (decimal degrees)",
    ),
    ParameterSchema(
        "project_longitude_deg", "float", units="deg",
        description="WGS84 longitude (decimal degrees)",
    ),
    ParameterSchema(
        "project_jurisdiction_id", "enum", required=True,
        description="Registered jurisdiction ID",
    ),
    ParameterSchema(
        "project_design_storms_years", "tuple[int]", units="years", required=True,
        description="Return periods to analyze",
    ),
    ParameterSchema(
        "project_freeboard_ft", "float", units="ft",
        description="Freeboard above design WSE",
    ),
    ParameterSchema(
        "project_status", "enum",
        description="Lifecycle status (system-managed)",
    ),
)
