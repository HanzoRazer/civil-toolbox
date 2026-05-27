"""IDF curve data models for rainfall lookup and storm generation.

Provides structured IDF (Intensity-Duration-Frequency) curve support
for deterministic rainfall intensity lookup and StormEvent generation.

Example:
    >>> from civil_toolbox.rainfall.idf import IDFCurve, IDFPoint
    >>> curve = IDFCurve(
    ...     id="harris-county",
    ...     name="Harris County IDF",
    ...     points=[
    ...         IDFPoint(return_period_years=10, duration_minutes=15, rainfall_intensity_in_per_hr=5.1),
    ...         IDFPoint(return_period_years=100, duration_minutes=15, rainfall_intensity_in_per_hr=8.0),
    ...     ],
    ... )
    >>> intensity = curve.lookup_intensity(return_period_years=10, duration_minutes=15)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.rainfall.errors import (
    InvalidIDFDataError,
    IDFLookupError,
    IDFInterpolationError,
)
from civil_toolbox.rainfall.validation import (
    validate_return_period,
    validate_duration_minutes,
    validate_intensity_in_per_hr,
    validate_depth_in,
)
from civil_toolbox.rainfall.interpolation import interpolate_from_points


@dataclass
class IDFPoint:
    """A single point in an IDF curve.

    Represents rainfall intensity (and optionally depth) for a specific
    return period and duration combination.

    Attributes:
        return_period_years: Return period in years (e.g., 10, 25, 100).
        duration_minutes: Storm duration in minutes.
        rainfall_intensity_in_per_hr: Rainfall intensity in inches per hour.
        rainfall_depth_in: Optional rainfall depth in inches.
        metadata: Optional additional metadata.
    """

    return_period_years: int
    duration_minutes: float
    rainfall_intensity_in_per_hr: float
    rainfall_depth_in: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_return_period(self.return_period_years)
        self.duration_minutes = validate_duration_minutes(self.duration_minutes)
        self.rainfall_intensity_in_per_hr = validate_intensity_in_per_hr(
            self.rainfall_intensity_in_per_hr
        )
        self.rainfall_depth_in = validate_depth_in(self.rainfall_depth_in)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "return_period_years": self.return_period_years,
            "duration_minutes": self.duration_minutes,
            "rainfall_intensity_in_per_hr": self.rainfall_intensity_in_per_hr,
            "rainfall_depth_in": self.rainfall_depth_in,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IDFPoint:
        """Deserialize from dictionary."""
        return cls(
            return_period_years=data["return_period_years"],
            duration_minutes=data["duration_minutes"],
            rainfall_intensity_in_per_hr=data["rainfall_intensity_in_per_hr"],
            rainfall_depth_in=data.get("rainfall_depth_in"),
            metadata=data.get("metadata", {}),
        )


def _format_duration(duration_minutes: float) -> str:
    """Format duration for storm name, omitting decimal if whole number."""
    if duration_minutes == int(duration_minutes):
        return str(int(duration_minutes))
    return str(duration_minutes)


@dataclass
class IDFCurve:
    """An IDF (Intensity-Duration-Frequency) curve.

    Contains rainfall intensity data for multiple return periods and durations.
    Supports deterministic lookup with optional duration interpolation.

    Attributes:
        id: Unique curve identifier.
        name: Human-readable curve name.
        source: Optional data source (e.g., "NOAA Atlas 14").
        location: Optional location description.
        station_id: Optional rainfall station identifier.
        units: Unit metadata (documentation only, no conversion).
        points: List of IDF data points.
        metadata: Additional configuration.
    """

    id: str
    name: str
    source: str | None = None
    location: str | None = None
    station_id: str | None = None
    units: dict[str, str] = field(default_factory=lambda: {
        "duration": "minutes",
        "rainfall_intensity": "in/hr",
        "rainfall_depth": "in",
    })
    points: list[IDFPoint] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidIDFDataError("IDFCurve id is required")
        if not self.name:
            raise InvalidIDFDataError("IDFCurve name is required")
        if not self.points:
            raise InvalidIDFDataError("IDFCurve must have at least one point")

        seen = set()
        for point in self.points:
            key = (point.return_period_years, point.duration_minutes)
            if key in seen:
                raise InvalidIDFDataError(
                    f"Duplicate point: return_period={point.return_period_years}, "
                    f"duration={point.duration_minutes}"
                )
            seen.add(key)

    def get_return_periods(self) -> list[int]:
        """Get all return periods in the curve, sorted ascending."""
        return sorted(set(p.return_period_years for p in self.points))

    def get_durations(self, return_period_years: int | None = None) -> list[float]:
        """Get all durations in the curve, optionally filtered by return period.

        Args:
            return_period_years: If provided, only return durations for this
                return period. If None, return all unique durations.

        Returns:
            Sorted list of durations in minutes.
        """
        if return_period_years is None:
            return sorted(set(p.duration_minutes for p in self.points))

        return sorted(
            p.duration_minutes
            for p in self.points
            if p.return_period_years == return_period_years
        )

    def _points_for_return_period(
        self, return_period_years: int
    ) -> dict[float, IDFPoint]:
        """Get points indexed by duration for a specific return period."""
        return {
            p.duration_minutes: p
            for p in self.points
            if p.return_period_years == return_period_years
        }

    def lookup_intensity(
        self,
        return_period_years: int,
        duration_minutes: float,
        interpolate_duration: bool = True,
        interpolate_return_period: bool = False,
    ) -> float:
        """Look up rainfall intensity from the IDF curve.

        Args:
            return_period_years: Return period in years.
            duration_minutes: Storm duration in minutes.
            interpolate_duration: If True, interpolate between durations.
            interpolate_return_period: If True, interpolate between return periods.
                Not implemented yet.

        Returns:
            Rainfall intensity in inches per hour.

        Raises:
            IDFLookupError: If return period is not in curve.
            IDFInterpolationError: If interpolation cannot be performed
                or is requested but not supported.
        """
        if interpolate_return_period:
            raise IDFInterpolationError(
                "Return-period interpolation is not implemented yet."
            )

        duration_points = self._points_for_return_period(return_period_years)
        if not duration_points:
            available = self.get_return_periods()
            raise IDFLookupError(
                f"Return period {return_period_years} not in curve '{self.name}'. "
                f"Available: {available}"
            )

        intensity_by_duration = {
            d: p.rainfall_intensity_in_per_hr for d, p in duration_points.items()
        }

        if duration_minutes in intensity_by_duration:
            return intensity_by_duration[duration_minutes]

        if not interpolate_duration:
            available = sorted(intensity_by_duration.keys())
            raise IDFLookupError(
                f"Duration {duration_minutes} min not in curve for "
                f"return period {return_period_years}. "
                f"Available: {available}. Enable interpolate_duration=True."
            )

        try:
            return interpolate_from_points(duration_minutes, intensity_by_duration)
        except IDFInterpolationError as e:
            available = sorted(intensity_by_duration.keys())
            raise IDFInterpolationError(
                f"Cannot interpolate duration {duration_minutes} min for "
                f"return period {return_period_years} in curve '{self.name}'. "
                f"Available durations: {available}. {e}"
            ) from e

    def lookup_depth(
        self,
        return_period_years: int,
        duration_minutes: float,
        interpolate_duration: bool = True,
        interpolate_return_period: bool = False,
    ) -> float:
        """Look up or derive rainfall depth from the IDF curve.

        If depth values are stored, returns the stored value (with optional
        interpolation). If not stored, derives depth from intensity:

            depth_in = intensity_in_per_hr * duration_minutes / 60

        Args:
            return_period_years: Return period in years.
            duration_minutes: Storm duration in minutes.
            interpolate_duration: If True, interpolate between durations.
            interpolate_return_period: If True, interpolate between return periods.
                Not implemented yet.

        Returns:
            Rainfall depth in inches.

        Raises:
            IDFLookupError: If return period is not in curve.
            IDFInterpolationError: If interpolation cannot be performed.
        """
        if interpolate_return_period:
            raise IDFInterpolationError(
                "Return-period interpolation is not implemented yet."
            )

        duration_points = self._points_for_return_period(return_period_years)
        if not duration_points:
            available = self.get_return_periods()
            raise IDFLookupError(
                f"Return period {return_period_years} not in curve '{self.name}'. "
                f"Available: {available}"
            )

        has_stored_depth = any(
            p.rainfall_depth_in is not None for p in duration_points.values()
        )

        if has_stored_depth:
            depth_by_duration = {
                d: p.rainfall_depth_in
                for d, p in duration_points.items()
                if p.rainfall_depth_in is not None
            }

            if duration_minutes in depth_by_duration:
                return depth_by_duration[duration_minutes]

            if not interpolate_duration:
                available = sorted(depth_by_duration.keys())
                raise IDFLookupError(
                    f"Duration {duration_minutes} min not in curve for "
                    f"return period {return_period_years}. "
                    f"Available: {available}. Enable interpolate_duration=True."
                )

            if depth_by_duration:
                try:
                    return interpolate_from_points(duration_minutes, depth_by_duration)
                except IDFInterpolationError:
                    pass

        intensity = self.lookup_intensity(
            return_period_years=return_period_years,
            duration_minutes=duration_minutes,
            interpolate_duration=interpolate_duration,
            interpolate_return_period=False,
        )
        return intensity * duration_minutes / 60.0

    def to_storm_event(
        self,
        return_period_years: int,
        duration_minutes: float,
        name: str | None = None,
        interpolate_duration: bool = True,
        extra_metadata: dict[str, Any] | None = None,
    ):
        """Generate a StormEvent from this IDF curve.

        Args:
            return_period_years: Return period in years.
            duration_minutes: Storm duration in minutes.
            name: Optional storm name. If not provided, generates a
                default name like "100-year 15-minute storm".
            interpolate_duration: If True, interpolate between durations.
            extra_metadata: Optional additional metadata to merge into
                the storm event's metadata.

        Returns:
            StormEvent with intensity and depth from this curve.

        Raises:
            IDFLookupError: If lookup fails.
        """
        from civil_toolbox.domain.storm import StormEvent

        intensity = self.lookup_intensity(
            return_period_years=return_period_years,
            duration_minutes=duration_minutes,
            interpolate_duration=interpolate_duration,
        )
        depth = self.lookup_depth(
            return_period_years=return_period_years,
            duration_minutes=duration_minutes,
            interpolate_duration=interpolate_duration,
        )

        if name is None:
            dur_str = _format_duration(duration_minutes)
            name = f"{return_period_years}-year {dur_str}-minute storm"

        storm_metadata: dict[str, Any] = {
            "idf_curve_id": self.id,
            "idf_curve_name": self.name,
        }
        if extra_metadata:
            storm_metadata.update(extra_metadata)

        return StormEvent(
            name=name,
            return_period_years=return_period_years,
            duration_hours=duration_minutes / 60.0,
            rainfall_intensity_in_per_hr=intensity,
            rainfall_depth_in=depth,
            description=f"Generated from IDF curve: {self.name}",
            metadata=storm_metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "location": self.location,
            "station_id": self.station_id,
            "units": self.units,
            "points": [p.to_dict() for p in self.points],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IDFCurve:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            source=data.get("source"),
            location=data.get("location"),
            station_id=data.get("station_id"),
            units=data.get("units", {
                "duration": "minutes",
                "rainfall_intensity": "in/hr",
                "rainfall_depth": "in",
            }),
            points=[IDFPoint.from_dict(p) for p in data.get("points", [])],
            metadata=data.get("metadata", {}),
        )
