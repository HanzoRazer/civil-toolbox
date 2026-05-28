"""Design criteria library (registry) for managing criteria sets.

Provides in-memory storage and lookup for design criteria sets.

Example:
    >>> from civil_toolbox.design_criteria import (
    ...     DesignCriteriaLibrary,
    ...     DesignCriteria,
    ... )
    >>> library = DesignCriteriaLibrary()
    >>> library.register(my_criteria)
    >>> criteria = library.get("my-criteria-id")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from civil_toolbox.design_criteria.criteria import DesignCriteria
from civil_toolbox.design_criteria.errors import (
    CriteriaNotFoundError,
    InvalidDesignCriteriaError,
)


@dataclass
class DesignCriteriaLibrary:
    """Registry of design criteria sets.

    Provides named lookup and management for criteria sets from
    multiple jurisdictions or projects.

    Attributes:
        name: Optional library name.
        metadata: Additional metadata.
    """

    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    _criteria: dict[str, DesignCriteria] = field(
        default_factory=dict, repr=False
    )

    def register(
        self,
        criteria: DesignCriteria,
        overwrite: bool = False,
    ) -> None:
        """Register a criteria set in the library.

        Args:
            criteria: The criteria set to register.
            overwrite: If True, overwrite existing criteria with same ID.

        Raises:
            InvalidDesignCriteriaError: If criteria ID already exists
                and overwrite is False.
        """
        if criteria.id in self._criteria and not overwrite:
            raise InvalidDesignCriteriaError(
                f"Criteria '{criteria.id}' already registered. "
                "Use overwrite=True to replace."
            )
        self._criteria[criteria.id] = criteria

    def unregister(self, criteria_id: str) -> None:
        """Remove a criteria set from the library.

        Args:
            criteria_id: ID of criteria to remove.

        Raises:
            CriteriaNotFoundError: If criteria ID not found.
        """
        if criteria_id not in self._criteria:
            raise CriteriaNotFoundError(
                f"Criteria '{criteria_id}' not found in library"
            )
        del self._criteria[criteria_id]

    def get(self, criteria_id: str) -> DesignCriteria:
        """Get a criteria set by ID.

        Args:
            criteria_id: ID of criteria to retrieve.

        Returns:
            The criteria set.

        Raises:
            CriteriaNotFoundError: If criteria ID not found.
        """
        if criteria_id not in self._criteria:
            available = self.list_ids()
            raise CriteriaNotFoundError(
                f"Criteria '{criteria_id}' not found. Available: {available}"
            )
        return self._criteria[criteria_id]

    def has(self, criteria_id: str) -> bool:
        """Check if criteria ID exists in library.

        Args:
            criteria_id: ID to check.

        Returns:
            True if criteria exists.
        """
        return criteria_id in self._criteria

    def list_ids(self) -> list[str]:
        """Get all registered criteria IDs.

        Returns:
            Sorted list of criteria IDs.
        """
        return sorted(self._criteria.keys())

    def list_criteria(self) -> list[DesignCriteria]:
        """Get all registered criteria sets.

        Returns:
            List of criteria sets sorted by ID.
        """
        return [self._criteria[k] for k in self.list_ids()]

    def find_by_jurisdiction(self, jurisdiction: str) -> list[DesignCriteria]:
        """Find criteria sets by jurisdiction name.

        Args:
            jurisdiction: Jurisdiction name to search for.

        Returns:
            List of matching criteria sets.
        """
        return [
            c for c in self._criteria.values()
            if c.jurisdiction and jurisdiction.lower() in c.jurisdiction.lower()
        ]

    def clear(self) -> None:
        """Remove all criteria from the library."""
        self._criteria.clear()

    def __len__(self) -> int:
        """Return number of registered criteria."""
        return len(self._criteria)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "metadata": self.metadata,
            "criteria": [c.to_dict() for c in self.list_criteria()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DesignCriteriaLibrary:
        """Deserialize from dictionary."""
        library = cls(
            name=data.get("name"),
            metadata=data.get("metadata", {}),
        )
        for criteria_data in data.get("criteria", []):
            library.register(DesignCriteria.from_dict(criteria_data))
        return library
