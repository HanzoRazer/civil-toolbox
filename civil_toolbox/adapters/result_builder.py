"""Result builder utilities for adapters.

Helpers for constructing CalculationResult objects with consistent
structure, inputs, outputs, units, and engineering references.
"""

from typing import Any, Optional

from civil_toolbox.domain.base import (
    EngineeringAssumption,
    EngineeringReference,
    ValidationWarning,
)
from civil_toolbox.domain.calculation import CalculationResult


class ResultBuilder:
    """Builder for constructing CalculationResult objects.

    Provides a fluent interface for building auditable calculation
    results with all required metadata.
    """

    def __init__(self, method: str):
        """Initialize builder with calculation method name.

        Args:
            method: Name of the calculation method (e.g., "rational_method")
        """
        self._method = method
        self._entity_id: Optional[str] = None
        self._entity_type: Optional[str] = None
        self._inputs: dict[str, Any] = {}
        self._outputs: dict[str, Any] = {}
        self._units: dict[str, str] = {}
        self._assumptions: list[EngineeringAssumption] = []
        self._warnings: list[ValidationWarning] = []
        self._references: list[EngineeringReference] = []
        self._metadata: dict[str, Any] = {}

    def for_entity(
        self,
        entity_id: str,
        entity_type: str,
    ) -> "ResultBuilder":
        """Set the source entity for this calculation.

        Args:
            entity_id: ID of the domain entity
            entity_type: Type name (e.g., "DrainageArea")

        Returns:
            Self for method chaining
        """
        self._entity_id = entity_id
        self._entity_type = entity_type
        return self

    def with_input(
        self,
        name: str,
        value: Any,
        unit: Optional[str] = None,
    ) -> "ResultBuilder":
        """Add an input parameter.

        Args:
            name: Parameter name
            value: Parameter value
            unit: Optional unit string

        Returns:
            Self for method chaining
        """
        self._inputs[name] = value
        if unit:
            self._units[name] = unit
        return self

    def with_output(
        self,
        name: str,
        value: Any,
        unit: Optional[str] = None,
    ) -> "ResultBuilder":
        """Add an output value.

        Args:
            name: Output name
            value: Output value
            unit: Optional unit string

        Returns:
            Self for method chaining
        """
        self._outputs[name] = value
        if unit:
            self._units[name] = unit
        return self

    def with_assumption(
        self,
        description: str,
        category: Optional[str] = None,
    ) -> "ResultBuilder":
        """Add an engineering assumption.

        Args:
            description: Description of the assumption
            category: Optional category for grouping

        Returns:
            Self for method chaining
        """
        self._assumptions.append(
            EngineeringAssumption(description=description, category=category)
        )
        return self

    def with_warning(
        self,
        message: str,
        field: Optional[str] = None,
        severity: str = "warning",
    ) -> "ResultBuilder":
        """Add a validation warning.

        Args:
            message: Warning message
            field: Optional field name
            severity: Severity level (info, warning, error)

        Returns:
            Self for method chaining
        """
        self._warnings.append(
            ValidationWarning(message=message, field=field, severity=severity)
        )
        return self

    def with_reference(
        self,
        title: str,
        source: str,
        year: Optional[int] = None,
        section: Optional[str] = None,
    ) -> "ResultBuilder":
        """Add an engineering reference.

        Args:
            title: Reference title
            source: Source name (e.g., "NRCS")
            year: Publication year
            section: Section or page reference

        Returns:
            Self for method chaining
        """
        self._references.append(
            EngineeringReference(
                title=title,
                source=source,
                year=year,
                section=section,
            )
        )
        return self

    def with_metadata(self, key: str, value: Any) -> "ResultBuilder":
        """Add metadata.

        Args:
            key: Metadata key
            value: Metadata value

        Returns:
            Self for method chaining
        """
        self._metadata[key] = value
        return self

    def build(self) -> CalculationResult:
        """Build the CalculationResult.

        Returns:
            Fully constructed CalculationResult
        """
        result = CalculationResult(
            method=self._method,
            entity_id=self._entity_id,
            entity_type=self._entity_type,
            inputs=self._inputs.copy(),
            outputs=self._outputs.copy(),
            units=self._units.copy(),
            metadata=self._metadata.copy(),
        )

        for assumption in self._assumptions:
            result.add_assumption(assumption)

        for warning in self._warnings:
            result.add_warning(warning)

        for reference in self._references:
            result.add_reference(reference)

        return result


# Standard engineering references for common methods

RATIONAL_METHOD_REFERENCE = EngineeringReference(
    title="Urban Drainage Design Manual",
    source="FHWA HEC-22",
    year=2009,
    section="Chapter 3",
)

TR55_REFERENCE = EngineeringReference(
    title="Urban Hydrology for Small Watersheds",
    source="NRCS TR-55",
    year=1986,
    section="Chapter 2",
)

KIRPICH_REFERENCE = EngineeringReference(
    title="Time of concentration of small agricultural watersheds",
    source="Civil Engineering",
    year=1940,
    section="Kirpich, Z.P.",
)

KERBY_REFERENCE = EngineeringReference(
    title="Time of concentration for overland flow",
    source="Civil Engineering",
    year=1959,
    section="Kerby, W.S.",
)

KINEMATIC_WAVE_REFERENCE = EngineeringReference(
    title="Urban Hydrology for Small Watersheds",
    source="NRCS TR-55",
    year=1986,
    section="Chapter 3, Exhibit 3-1",
)
