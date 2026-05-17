"""Entity matching strategies for scenario comparison."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from civil_toolbox.comparison.models import MatchStrategy

if TYPE_CHECKING:
    from civil_toolbox.domain.scenario import Scenario


def _normalize_name(name: str) -> str:
    """Normalize entity name for comparison.

    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse multiple spaces to single space
    - Remove non-alphanumeric characters except spaces
    """
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"[^a-z0-9 ]", "", name)
    return name


@dataclass
class EntityMatch:
    """A matched pair of entities between scenarios."""

    baseline_id: str
    comparison_id: str
    baseline_name: str
    comparison_name: str
    entity_type: str
    match_method: str


@dataclass
class MatchResult:
    """Result of entity matching between two scenarios."""

    matches: list[EntityMatch]
    unmatched_baseline_ids: list[str]
    unmatched_comparison_ids: list[str]
    strategy_used: MatchStrategy


def match_by_id(
    baseline_entities: list[tuple[str, str, str]],
    comparison_entities: list[tuple[str, str, str]],
) -> MatchResult:
    """Match entities by ID.

    Args:
        baseline_entities: List of (id, name, entity_type) tuples.
        comparison_entities: List of (id, name, entity_type) tuples.

    Returns:
        MatchResult with matched pairs and unmatched IDs.
    """
    comparison_by_id = {e[0]: e for e in comparison_entities}
    matches = []
    unmatched_baseline = []

    for b_id, b_name, b_type in baseline_entities:
        if b_id in comparison_by_id:
            c_id, c_name, c_type = comparison_by_id[b_id]
            matches.append(
                EntityMatch(
                    baseline_id=b_id,
                    comparison_id=c_id,
                    baseline_name=b_name,
                    comparison_name=c_name,
                    entity_type=b_type,
                    match_method="id",
                )
            )
        else:
            unmatched_baseline.append(b_id)

    matched_comparison_ids = {m.comparison_id for m in matches}
    unmatched_comparison = [
        e[0] for e in comparison_entities if e[0] not in matched_comparison_ids
    ]

    return MatchResult(
        matches=matches,
        unmatched_baseline_ids=unmatched_baseline,
        unmatched_comparison_ids=unmatched_comparison,
        strategy_used=MatchStrategy.ID,
    )


def match_by_name(
    baseline_entities: list[tuple[str, str, str]],
    comparison_entities: list[tuple[str, str, str]],
) -> MatchResult:
    """Match entities by normalized name.

    Args:
        baseline_entities: List of (id, name, entity_type) tuples.
        comparison_entities: List of (id, name, entity_type) tuples.

    Returns:
        MatchResult with matched pairs and unmatched IDs.
    """
    comparison_by_name = {}
    for c_id, c_name, c_type in comparison_entities:
        normalized = _normalize_name(c_name)
        if normalized not in comparison_by_name:
            comparison_by_name[normalized] = (c_id, c_name, c_type)

    matches = []
    unmatched_baseline = []
    matched_comparison_ids = set()

    for b_id, b_name, b_type in baseline_entities:
        normalized = _normalize_name(b_name)
        if normalized in comparison_by_name:
            c_id, c_name, c_type = comparison_by_name[normalized]
            if c_id not in matched_comparison_ids:
                matches.append(
                    EntityMatch(
                        baseline_id=b_id,
                        comparison_id=c_id,
                        baseline_name=b_name,
                        comparison_name=c_name,
                        entity_type=b_type,
                        match_method="name",
                    )
                )
                matched_comparison_ids.add(c_id)
            else:
                unmatched_baseline.append(b_id)
        else:
            unmatched_baseline.append(b_id)

    unmatched_comparison = [
        e[0] for e in comparison_entities if e[0] not in matched_comparison_ids
    ]

    return MatchResult(
        matches=matches,
        unmatched_baseline_ids=unmatched_baseline,
        unmatched_comparison_ids=unmatched_comparison,
        strategy_used=MatchStrategy.NAME,
    )


def match_by_explicit_map(
    baseline_entities: list[tuple[str, str, str]],
    comparison_entities: list[tuple[str, str, str]],
    explicit_map: dict[str, str],
) -> MatchResult:
    """Match entities using explicit ID mapping.

    Args:
        baseline_entities: List of (id, name, entity_type) tuples.
        comparison_entities: List of (id, name, entity_type) tuples.
        explicit_map: Dict mapping baseline_id -> comparison_id.

    Returns:
        MatchResult with matched pairs and unmatched IDs.
    """
    comparison_by_id = {e[0]: e for e in comparison_entities}
    baseline_by_id = {e[0]: e for e in baseline_entities}

    matches = []
    matched_baseline_ids = set()
    matched_comparison_ids = set()

    for b_id, c_id in explicit_map.items():
        if b_id in baseline_by_id and c_id in comparison_by_id:
            b_id_, b_name, b_type = baseline_by_id[b_id]
            c_id_, c_name, c_type = comparison_by_id[c_id]
            matches.append(
                EntityMatch(
                    baseline_id=b_id,
                    comparison_id=c_id,
                    baseline_name=b_name,
                    comparison_name=c_name,
                    entity_type=b_type,
                    match_method="explicit",
                )
            )
            matched_baseline_ids.add(b_id)
            matched_comparison_ids.add(c_id)

    unmatched_baseline = [
        e[0] for e in baseline_entities if e[0] not in matched_baseline_ids
    ]
    unmatched_comparison = [
        e[0] for e in comparison_entities if e[0] not in matched_comparison_ids
    ]

    return MatchResult(
        matches=matches,
        unmatched_baseline_ids=unmatched_baseline,
        unmatched_comparison_ids=unmatched_comparison,
        strategy_used=MatchStrategy.EXPLICIT,
    )


def match_auto(
    baseline_entities: list[tuple[str, str, str]],
    comparison_entities: list[tuple[str, str, str]],
    explicit_map: dict[str, str] | None = None,
) -> MatchResult:
    """Match entities using auto strategy (explicit > ID > name).

    Priority order:
    1. Explicit mapping (if provided)
    2. ID matching
    3. Name matching (for remaining unmatched)

    Args:
        baseline_entities: List of (id, name, entity_type) tuples.
        comparison_entities: List of (id, name, entity_type) tuples.
        explicit_map: Optional explicit ID mapping.

    Returns:
        MatchResult with matched pairs and unmatched IDs.
    """
    all_matches = []
    matched_baseline_ids = set()
    matched_comparison_ids = set()

    if explicit_map:
        explicit_result = match_by_explicit_map(
            baseline_entities, comparison_entities, explicit_map
        )
        for match in explicit_result.matches:
            all_matches.append(match)
            matched_baseline_ids.add(match.baseline_id)
            matched_comparison_ids.add(match.comparison_id)

    remaining_baseline = [
        e for e in baseline_entities if e[0] not in matched_baseline_ids
    ]
    remaining_comparison = [
        e for e in comparison_entities if e[0] not in matched_comparison_ids
    ]

    if remaining_baseline and remaining_comparison:
        id_result = match_by_id(remaining_baseline, remaining_comparison)
        for match in id_result.matches:
            all_matches.append(match)
            matched_baseline_ids.add(match.baseline_id)
            matched_comparison_ids.add(match.comparison_id)

    remaining_baseline = [
        e for e in baseline_entities if e[0] not in matched_baseline_ids
    ]
    remaining_comparison = [
        e for e in comparison_entities if e[0] not in matched_comparison_ids
    ]

    if remaining_baseline and remaining_comparison:
        name_result = match_by_name(remaining_baseline, remaining_comparison)
        for match in name_result.matches:
            all_matches.append(match)
            matched_baseline_ids.add(match.baseline_id)
            matched_comparison_ids.add(match.comparison_id)

    unmatched_baseline = [
        e[0] for e in baseline_entities if e[0] not in matched_baseline_ids
    ]
    unmatched_comparison = [
        e[0] for e in comparison_entities if e[0] not in matched_comparison_ids
    ]

    return MatchResult(
        matches=all_matches,
        unmatched_baseline_ids=unmatched_baseline,
        unmatched_comparison_ids=unmatched_comparison,
        strategy_used=MatchStrategy.AUTO,
    )


def match_entities(
    baseline: Scenario,
    comparison: Scenario,
    strategy: MatchStrategy = MatchStrategy.AUTO,
    explicit_map: dict[str, str] | None = None,
    entity_type: str = "DrainageArea",
) -> MatchResult:
    """Match entities between two scenarios.

    Args:
        baseline: Baseline scenario.
        comparison: Comparison scenario.
        strategy: Matching strategy to use.
        explicit_map: Explicit ID mapping (for EXPLICIT or AUTO strategies).
        entity_type: Type of entity to match (default: DrainageArea).

    Returns:
        MatchResult with matched pairs and unmatched IDs.

    Raises:
        ValueError: If explicit strategy used without explicit_map.
    """

    def get_entities(scenario: Scenario) -> list[tuple[str, str, str]]:
        if entity_type == "DrainageArea":
            return [(a.id, a.name, "DrainageArea") for a in scenario.drainage_areas]
        elif entity_type == "FlowPath":
            return [(p.id, p.name, "FlowPath") for p in scenario.flow_paths]
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")

    baseline_entities = get_entities(baseline)
    comparison_entities = get_entities(comparison)

    if strategy == MatchStrategy.EXPLICIT:
        if not explicit_map:
            raise ValueError("Explicit strategy requires explicit_map")
        return match_by_explicit_map(
            baseline_entities, comparison_entities, explicit_map
        )
    elif strategy == MatchStrategy.ID:
        return match_by_id(baseline_entities, comparison_entities)
    elif strategy == MatchStrategy.NAME:
        return match_by_name(baseline_entities, comparison_entities)
    else:
        return match_auto(baseline_entities, comparison_entities, explicit_map)
