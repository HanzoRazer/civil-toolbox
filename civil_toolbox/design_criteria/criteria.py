"""Design criteria data models.

Provides structured models for runoff coefficients, curve numbers,
design storms, and complete design criteria sets.

Example:
    >>> from civil_toolbox.design_criteria import DesignCriteria
    >>> criteria = DesignCriteria(
    ...     id="example",
    ...     name="Example Criteria",
    ...     jurisdiction="Example County",
    ... )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from civil_toolbox.design_criteria.errors import (
    InvalidDesignCriteriaError,
    DesignCriteriaLookupError,
)
from civil_toolbox.design_criteria.validation import (
    validate_runoff_coefficient,
    validate_curve_number,
    validate_soil_group,
    validate_return_period,
    validate_duration_minutes,
    normalize_land_use_key,
    VALID_SOIL_GROUPS,
)

if TYPE_CHECKING:
    from civil_toolbox.rainfall.idf import IDFCurve
    from civil_toolbox.domain.storm import StormEvent


@dataclass
class RunoffCoefficientEntry:
    """A single entry in a runoff coefficient table.

    Attributes:
        land_use: Land use category identifier.
        min: Minimum coefficient value.
        max: Maximum coefficient value.
        typical: Typical/default coefficient value.
        description: Optional description of the land use.
    """

    land_use: str
    min: float
    max: float
    typical: float
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.land_use:
            raise InvalidDesignCriteriaError("land_use is required")
        validate_runoff_coefficient(self.min, "min")
        validate_runoff_coefficient(self.max, "max")
        validate_runoff_coefficient(self.typical, "typical")
        if self.min > self.max:
            raise InvalidDesignCriteriaError(
                f"min ({self.min}) cannot be greater than max ({self.max})"
            )
        if self.typical < self.min or self.typical > self.max:
            raise InvalidDesignCriteriaError(
                f"typical ({self.typical}) must be between min ({self.min}) "
                f"and max ({self.max})"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "land_use": self.land_use,
            "min": self.min,
            "max": self.max,
            "typical": self.typical,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunoffCoefficientEntry:
        """Deserialize from dictionary."""
        return cls(
            land_use=data["land_use"],
            min=data["min"],
            max=data["max"],
            typical=data["typical"],
            description=data.get("description"),
        )


@dataclass
class RunoffCoefficientTable:
    """Table of runoff coefficients by land use.

    Attributes:
        entries: List of coefficient entries.
        source: Optional data source reference.
        metadata: Additional metadata.
    """

    entries: list[RunoffCoefficientEntry] = field(default_factory=list)
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        land_uses = [e.land_use for e in self.entries]
        if len(land_uses) != len(set(land_uses)):
            raise InvalidDesignCriteriaError("Duplicate land_use entries")

    def get_land_uses(self) -> list[str]:
        """Get all land use categories."""
        return sorted(e.land_use for e in self.entries)

    def lookup(self, land_use: str) -> float:
        """Look up the typical runoff coefficient for a land use.

        Land use lookup is case-insensitive and normalizes whitespace.

        Args:
            land_use: Land use category.

        Returns:
            Typical runoff coefficient.

        Raises:
            DesignCriteriaLookupError: If land use not found.
        """
        normalized_key = normalize_land_use_key(land_use)
        for entry in self.entries:
            if normalize_land_use_key(entry.land_use) == normalized_key:
                return entry.typical
        available = self.get_land_uses()
        raise DesignCriteriaLookupError(
            f"Land use '{land_use}' not found. Available: {available}"
        )

    def lookup_entry(self, land_use: str) -> RunoffCoefficientEntry:
        """Look up the full coefficient entry for a land use.

        Land use lookup is case-insensitive and normalizes whitespace.

        Args:
            land_use: Land use category.

        Returns:
            Full coefficient entry with min/max/typical.

        Raises:
            DesignCriteriaLookupError: If land use not found.
        """
        normalized_key = normalize_land_use_key(land_use)
        for entry in self.entries:
            if normalize_land_use_key(entry.land_use) == normalized_key:
                return entry
        available = self.get_land_uses()
        raise DesignCriteriaLookupError(
            f"Land use '{land_use}' not found. Available: {available}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "source": self.source,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunoffCoefficientTable:
        """Deserialize from dictionary."""
        return cls(
            entries=[
                RunoffCoefficientEntry.from_dict(e)
                for e in data.get("entries", [])
            ],
            source=data.get("source"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CurveNumberEntry:
    """A single entry in a curve number table.

    Attributes:
        land_use: Land use category identifier.
        soil_groups: Dictionary mapping soil group to curve number.
        description: Optional description of the land use.
    """

    land_use: str
    soil_groups: dict[str, int] = field(default_factory=dict)
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.land_use:
            raise InvalidDesignCriteriaError("land_use is required")
        for soil_group, cn in self.soil_groups.items():
            validate_soil_group(soil_group)
            validate_curve_number(cn, f"CN for soil group {soil_group}")

    def get_cn(self, soil_group: str) -> int:
        """Get curve number for a soil group.

        Args:
            soil_group: Hydrologic soil group (A, B, C, or D).

        Returns:
            Curve number for the soil group.

        Raises:
            DesignCriteriaLookupError: If soil group not found.
        """
        normalized = soil_group.upper().strip()
        if normalized not in self.soil_groups:
            available = sorted(self.soil_groups.keys())
            raise DesignCriteriaLookupError(
                f"Soil group '{soil_group}' not found for land use '{self.land_use}'. "
                f"Available: {available}"
            )
        return self.soil_groups[normalized]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "land_use": self.land_use,
            "soil_groups": self.soil_groups,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CurveNumberEntry:
        """Deserialize from dictionary."""
        return cls(
            land_use=data["land_use"],
            soil_groups=data.get("soil_groups", {}),
            description=data.get("description"),
        )


@dataclass
class CurveNumberTable:
    """Table of curve numbers by land use and soil group.

    Attributes:
        entries: List of curve number entries.
        source: Optional data source reference.
        metadata: Additional metadata.
    """

    entries: list[CurveNumberEntry] = field(default_factory=list)
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        land_uses = [e.land_use for e in self.entries]
        if len(land_uses) != len(set(land_uses)):
            raise InvalidDesignCriteriaError("Duplicate land_use entries")

    def get_land_uses(self) -> list[str]:
        """Get all land use categories."""
        return sorted(e.land_use for e in self.entries)

    def lookup(self, land_use: str, soil_group: str) -> int:
        """Look up curve number for a land use and soil group.

        Land use lookup is case-insensitive and normalizes whitespace.

        Args:
            land_use: Land use category.
            soil_group: Hydrologic soil group (A, B, C, or D).

        Returns:
            Curve number.

        Raises:
            DesignCriteriaLookupError: If land use or soil group not found.
        """
        normalized_key = normalize_land_use_key(land_use)
        for entry in self.entries:
            if normalize_land_use_key(entry.land_use) == normalized_key:
                return entry.get_cn(soil_group)
        available = self.get_land_uses()
        raise DesignCriteriaLookupError(
            f"Land use '{land_use}' not found. Available: {available}"
        )

    def lookup_entry(self, land_use: str) -> CurveNumberEntry:
        """Look up the full curve number entry for a land use.

        Land use lookup is case-insensitive and normalizes whitespace.

        Args:
            land_use: Land use category.

        Returns:
            Full curve number entry with all soil groups.

        Raises:
            DesignCriteriaLookupError: If land use not found.
        """
        normalized_key = normalize_land_use_key(land_use)
        for entry in self.entries:
            if normalize_land_use_key(entry.land_use) == normalized_key:
                return entry
        available = self.get_land_uses()
        raise DesignCriteriaLookupError(
            f"Land use '{land_use}' not found. Available: {available}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "source": self.source,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CurveNumberTable:
        """Deserialize from dictionary."""
        return cls(
            entries=[
                CurveNumberEntry.from_dict(e)
                for e in data.get("entries", [])
            ],
            source=data.get("source"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DesignStormDefinition:
    """Definition of a design storm.

    Does not store precomputed intensity/depth — these are derived
    from the linked IDF curve when generating StormEvent objects.

    Attributes:
        name: Storm name (e.g., "100-year 24-hour").
        return_period_years: Return period in years.
        duration_minutes: Storm duration in minutes.
        description: Optional description.
        metadata: Additional metadata.
    """

    name: str
    return_period_years: int
    duration_minutes: float
    description: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise InvalidDesignCriteriaError("name is required")
        validate_return_period(self.return_period_years)
        validate_duration_minutes(self.duration_minutes)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "return_period_years": self.return_period_years,
            "duration_minutes": self.duration_minutes,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DesignStormDefinition:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            return_period_years=data["return_period_years"],
            duration_minutes=data["duration_minutes"],
            description=data.get("description"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DesignCriteria:
    """Complete design criteria set for a jurisdiction or project.

    Attributes:
        id: Unique criteria identifier.
        name: Human-readable criteria name.
        jurisdiction: Jurisdiction or project name.
        source: Data source reference.
        idf_curve: Optional embedded IDF curve.
        idf_curve_id: Optional IDF curve ID reference.
        runoff_coefficients: Optional runoff coefficient table.
        curve_numbers: Optional curve number table.
        design_storms: List of design storm definitions.
        metadata: Additional metadata.
    """

    id: str
    name: str
    jurisdiction: str | None = None
    source: str | None = None
    idf_curve: IDFCurve | None = None
    idf_curve_id: str | None = None
    runoff_coefficients: RunoffCoefficientTable | None = None
    curve_numbers: CurveNumberTable | None = None
    design_storms: list[DesignStormDefinition] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidDesignCriteriaError("id is required")
        if not self.name:
            raise InvalidDesignCriteriaError("name is required")

        storm_names = [s.name for s in self.design_storms]
        if len(storm_names) != len(set(storm_names)):
            raise InvalidDesignCriteriaError("Duplicate design storm names")

    def get_idf_curve(self) -> IDFCurve | None:
        """Get the IDF curve, if available.

        Returns embedded curve if present, otherwise None.
        To resolve idf_curve_id, use a library registry.
        """
        return self.idf_curve

    def lookup_runoff_coefficient(self, land_use: str) -> float:
        """Look up typical runoff coefficient for a land use.

        Args:
            land_use: Land use category.

        Returns:
            Typical runoff coefficient.

        Raises:
            DesignCriteriaLookupError: If table not defined or land use not found.
        """
        if self.runoff_coefficients is None:
            raise DesignCriteriaLookupError(
                "Runoff coefficient table not defined for this criteria"
            )
        return self.runoff_coefficients.lookup(land_use)

    def lookup_curve_number(self, land_use: str, soil_group: str) -> int:
        """Look up curve number for a land use and soil group.

        Args:
            land_use: Land use category.
            soil_group: Hydrologic soil group (A, B, C, or D).

        Returns:
            Curve number.

        Raises:
            DesignCriteriaLookupError: If table not defined or lookup fails.
        """
        if self.curve_numbers is None:
            raise DesignCriteriaLookupError(
                "Curve number table not defined for this criteria"
            )
        return self.curve_numbers.lookup(land_use, soil_group)

    def get_design_storm(self, name: str) -> DesignStormDefinition:
        """Get a design storm definition by name.

        Args:
            name: Design storm name.

        Returns:
            Design storm definition.

        Raises:
            DesignCriteriaLookupError: If storm not found.
        """
        for storm in self.design_storms:
            if storm.name == name:
                return storm
        available = [s.name for s in self.design_storms]
        raise DesignCriteriaLookupError(
            f"Design storm '{name}' not found. Available: {available}"
        )

    def get_design_storm_names(self) -> list[str]:
        """Get all design storm names."""
        return [s.name for s in self.design_storms]

    def generate_storm_event(self, storm_name: str) -> StormEvent:
        """Generate a StormEvent from a design storm definition.

        Requires an embedded IDF curve to derive intensity and depth.
        Includes criteria metadata for audit trails.

        Args:
            storm_name: Name of the design storm.

        Returns:
            StormEvent with intensity and depth from IDF curve,
            plus metadata linking back to criteria and storm definition.

        Raises:
            DesignCriteriaLookupError: If storm not found or IDF curve missing.
        """
        if self.idf_curve is None:
            raise DesignCriteriaLookupError(
                "Cannot generate storm event: no embedded IDF curve. "
                "Set idf_curve or use idf_curve_id with a registry."
            )

        storm_def = self.get_design_storm(storm_name)
        return self.idf_curve.to_storm_event(
            return_period_years=storm_def.return_period_years,
            duration_minutes=storm_def.duration_minutes,
            name=storm_def.name,
            extra_metadata={
                "design_criteria_id": self.id,
                "design_criteria_name": self.name,
                "design_storm_name": storm_def.name,
            },
        )

    def generate_all_storm_events(self) -> list[StormEvent]:
        """Generate StormEvents for all defined design storms.

        Requires an embedded IDF curve.

        Returns:
            List of StormEvents for all design storms.

        Raises:
            DesignCriteriaLookupError: If IDF curve missing.
        """
        return [
            self.generate_storm_event(storm.name)
            for storm in self.design_storms
        ]

    def lookup_runoff_coefficient_range(
        self, land_use: str
    ) -> tuple[float, float]:
        """Look up runoff coefficient min/max range for a land use.

        Args:
            land_use: Land use category.

        Returns:
            Tuple of (min, max) coefficients.

        Raises:
            DesignCriteriaLookupError: If table not defined or land use not found.
        """
        if self.runoff_coefficients is None:
            raise DesignCriteriaLookupError(
                "Runoff coefficient table not defined for this criteria"
            )
        entry = self.runoff_coefficients.lookup_entry(land_use)
        return (entry.min, entry.max)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "jurisdiction": self.jurisdiction,
            "source": self.source,
            "idf_curve": self.idf_curve.to_dict() if self.idf_curve else None,
            "idf_curve_id": self.idf_curve_id,
            "runoff_coefficients": (
                self.runoff_coefficients.to_dict()
                if self.runoff_coefficients
                else None
            ),
            "curve_numbers": (
                self.curve_numbers.to_dict() if self.curve_numbers else None
            ),
            "design_storms": [s.to_dict() for s in self.design_storms],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DesignCriteria:
        """Deserialize from dictionary."""
        from civil_toolbox.rainfall.idf import IDFCurve

        idf_data = data.get("idf_curve")
        rc_data = data.get("runoff_coefficients")
        cn_data = data.get("curve_numbers")

        return cls(
            id=data["id"],
            name=data["name"],
            jurisdiction=data.get("jurisdiction"),
            source=data.get("source"),
            idf_curve=IDFCurve.from_dict(idf_data) if idf_data else None,
            idf_curve_id=data.get("idf_curve_id"),
            runoff_coefficients=(
                RunoffCoefficientTable.from_dict(rc_data) if rc_data else None
            ),
            curve_numbers=(
                CurveNumberTable.from_dict(cn_data) if cn_data else None
            ),
            design_storms=[
                DesignStormDefinition.from_dict(s)
                for s in data.get("design_storms", [])
            ],
            metadata=data.get("metadata", {}),
        )
