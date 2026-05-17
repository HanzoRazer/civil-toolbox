"""Tests for entity matching strategies."""

import pytest

from civil_toolbox.comparison.matching import (
    _normalize_name,
    match_by_id,
    match_by_name,
    match_by_explicit_map,
    match_auto,
    match_entities,
    EntityMatch,
    MatchResult,
)
from civil_toolbox.comparison.models import MatchStrategy
from civil_toolbox.domain.scenario import Scenario
from civil_toolbox.domain.drainage import DrainageArea


class TestNormalizeName:
    """Tests for name normalization."""

    def test_lowercase(self):
        """Converts to lowercase."""
        assert _normalize_name("Area A") == "area a"

    def test_strip_whitespace(self):
        """Strips leading and trailing whitespace."""
        assert _normalize_name("  Area A  ") == "area a"

    def test_collapse_multiple_spaces(self):
        """Collapses multiple spaces to single space."""
        assert _normalize_name("Area   A") == "area a"

    def test_remove_special_characters(self):
        """Removes non-alphanumeric characters."""
        assert _normalize_name("Area-A (North)") == "areaa north"

    def test_preserve_numbers(self):
        """Preserves numbers."""
        assert _normalize_name("Area 123") == "area 123"


class TestMatchById:
    """Tests for ID-based matching."""

    def test_matches_same_ids(self):
        """Matches entities with same ID."""
        baseline = [("id-1", "Area A", "DrainageArea")]
        comparison = [("id-1", "Area A Proposed", "DrainageArea")]

        result = match_by_id(baseline, comparison)

        assert len(result.matches) == 1
        assert result.matches[0].baseline_id == "id-1"
        assert result.matches[0].comparison_id == "id-1"
        assert result.matches[0].match_method == "id"

    def test_tracks_unmatched_baseline(self):
        """Tracks baseline entities without match."""
        baseline = [("id-1", "Area A", "DrainageArea"), ("id-2", "Area B", "DrainageArea")]
        comparison = [("id-1", "Area A", "DrainageArea")]

        result = match_by_id(baseline, comparison)

        assert "id-2" in result.unmatched_baseline_ids

    def test_tracks_unmatched_comparison(self):
        """Tracks comparison entities without match."""
        baseline = [("id-1", "Area A", "DrainageArea")]
        comparison = [("id-1", "Area A", "DrainageArea"), ("id-3", "Area C", "DrainageArea")]

        result = match_by_id(baseline, comparison)

        assert "id-3" in result.unmatched_comparison_ids

    def test_empty_baseline(self):
        """Handles empty baseline."""
        baseline = []
        comparison = [("id-1", "Area A", "DrainageArea")]

        result = match_by_id(baseline, comparison)

        assert len(result.matches) == 0
        assert result.unmatched_comparison_ids == ["id-1"]

    def test_strategy_is_id(self):
        """Reports ID as strategy used."""
        result = match_by_id([], [])
        assert result.strategy_used == MatchStrategy.ID


class TestMatchByName:
    """Tests for name-based matching."""

    def test_matches_exact_names(self):
        """Matches entities with exact same name."""
        baseline = [("id-1", "Area A", "DrainageArea")]
        comparison = [("id-2", "Area A", "DrainageArea")]

        result = match_by_name(baseline, comparison)

        assert len(result.matches) == 1
        assert result.matches[0].baseline_id == "id-1"
        assert result.matches[0].comparison_id == "id-2"

    def test_matches_normalized_names(self):
        """Matches entities with equivalent normalized names."""
        baseline = [("id-1", "Area A", "DrainageArea")]
        comparison = [("id-2", "  area a  ", "DrainageArea")]

        result = match_by_name(baseline, comparison)

        assert len(result.matches) == 1

    def test_matches_names_with_different_case(self):
        """Matches names regardless of case."""
        baseline = [("id-1", "AREA A", "DrainageArea")]
        comparison = [("id-2", "area a", "DrainageArea")]

        result = match_by_name(baseline, comparison)

        assert len(result.matches) == 1

    def test_no_match_different_names(self):
        """Does not match different names."""
        baseline = [("id-1", "Area A", "DrainageArea")]
        comparison = [("id-2", "Area B", "DrainageArea")]

        result = match_by_name(baseline, comparison)

        assert len(result.matches) == 0
        assert "id-1" in result.unmatched_baseline_ids
        assert "id-2" in result.unmatched_comparison_ids

    def test_first_match_wins(self):
        """When multiple baseline entities have same normalized name, first wins."""
        baseline = [("id-1", "Area A", "DrainageArea"), ("id-2", "area a", "DrainageArea")]
        comparison = [("id-3", "Area A", "DrainageArea")]

        result = match_by_name(baseline, comparison)

        assert len(result.matches) == 1
        assert result.matches[0].baseline_id == "id-1"
        assert "id-2" in result.unmatched_baseline_ids

    def test_strategy_is_name(self):
        """Reports NAME as strategy used."""
        result = match_by_name([], [])
        assert result.strategy_used == MatchStrategy.NAME


class TestMatchByExplicitMap:
    """Tests for explicit mapping."""

    def test_matches_by_explicit_map(self):
        """Matches using explicit ID mapping."""
        baseline = [("b-1", "Area A", "DrainageArea")]
        comparison = [("c-1", "Area A Proposed", "DrainageArea")]
        explicit_map = {"b-1": "c-1"}

        result = match_by_explicit_map(baseline, comparison, explicit_map)

        assert len(result.matches) == 1
        assert result.matches[0].baseline_id == "b-1"
        assert result.matches[0].comparison_id == "c-1"
        assert result.matches[0].match_method == "explicit"

    def test_ignores_invalid_map_entries(self):
        """Ignores map entries for non-existent entities."""
        baseline = [("b-1", "Area A", "DrainageArea")]
        comparison = [("c-1", "Area A", "DrainageArea")]
        explicit_map = {"b-1": "c-1", "b-missing": "c-missing"}

        result = match_by_explicit_map(baseline, comparison, explicit_map)

        assert len(result.matches) == 1

    def test_unmatched_not_in_map(self):
        """Entities not in map are unmatched."""
        baseline = [("b-1", "Area A", "DrainageArea"), ("b-2", "Area B", "DrainageArea")]
        comparison = [("c-1", "Area A", "DrainageArea"), ("c-2", "Area B", "DrainageArea")]
        explicit_map = {"b-1": "c-1"}

        result = match_by_explicit_map(baseline, comparison, explicit_map)

        assert len(result.matches) == 1
        assert "b-2" in result.unmatched_baseline_ids
        assert "c-2" in result.unmatched_comparison_ids

    def test_strategy_is_explicit(self):
        """Reports EXPLICIT as strategy used."""
        result = match_by_explicit_map([], [], {})
        assert result.strategy_used == MatchStrategy.EXPLICIT


class TestMatchAuto:
    """Tests for auto matching strategy."""

    def test_explicit_map_first(self):
        """Explicit map takes priority over ID match."""
        baseline = [("b-1", "Area A", "DrainageArea")]
        comparison = [("b-1", "Area A", "DrainageArea"), ("c-1", "Area A Alt", "DrainageArea")]
        explicit_map = {"b-1": "c-1"}

        result = match_auto(baseline, comparison, explicit_map)

        assert len(result.matches) == 1
        assert result.matches[0].comparison_id == "c-1"
        assert result.matches[0].match_method == "explicit"

    def test_id_match_second(self):
        """ID matching used after explicit map."""
        baseline = [("id-1", "Area A", "DrainageArea"), ("id-2", "Area B", "DrainageArea")]
        comparison = [("id-1", "Area A", "DrainageArea"), ("id-2", "Area B", "DrainageArea")]

        result = match_auto(baseline, comparison)

        assert len(result.matches) == 2
        assert all(m.match_method == "id" for m in result.matches)

    def test_name_match_third(self):
        """Name matching used for remaining entities."""
        baseline = [("b-1", "Area A", "DrainageArea")]
        comparison = [("c-1", "Area A", "DrainageArea")]

        result = match_auto(baseline, comparison)

        assert len(result.matches) == 1
        assert result.matches[0].match_method == "name"

    def test_combined_strategies(self):
        """Combines all three strategies."""
        baseline = [
            ("shared-id", "Shared", "DrainageArea"),
            ("b-2", "Area B", "DrainageArea"),
            ("b-3", "Area C", "DrainageArea"),
        ]
        comparison = [
            ("shared-id", "Shared", "DrainageArea"),
            ("c-2", "Area B", "DrainageArea"),
            ("c-3", "Area C Mapped", "DrainageArea"),
        ]
        explicit_map = {"b-3": "c-3"}

        result = match_auto(baseline, comparison, explicit_map)

        assert len(result.matches) == 3

        methods = {m.baseline_id: m.match_method for m in result.matches}
        assert methods["b-3"] == "explicit"
        assert methods["shared-id"] == "id"
        assert methods["b-2"] == "name"

    def test_strategy_is_auto(self):
        """Reports AUTO as strategy used."""
        result = match_auto([], [])
        assert result.strategy_used == MatchStrategy.AUTO


class TestMatchEntities:
    """Tests for match_entities with Scenario objects."""

    def test_matches_drainage_areas(self):
        """Matches drainage areas between scenarios."""
        baseline = Scenario(name="Existing")
        baseline.add_drainage_area(DrainageArea(id="area-1", name="Area A"))
        baseline.add_drainage_area(DrainageArea(id="area-2", name="Area B"))

        comparison = Scenario(name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="area-1", name="Area A"))
        comparison.add_drainage_area(DrainageArea(id="area-2", name="Area B"))

        result = match_entities(baseline, comparison)

        assert len(result.matches) == 2
        assert result.unmatched_baseline_ids == []
        assert result.unmatched_comparison_ids == []

    def test_explicit_strategy_requires_map(self):
        """Explicit strategy raises without map."""
        baseline = Scenario(name="Existing")
        comparison = Scenario(name="Proposed")

        with pytest.raises(ValueError, match="explicit_map"):
            match_entities(baseline, comparison, strategy=MatchStrategy.EXPLICIT)

    def test_id_strategy(self):
        """ID strategy only matches by ID."""
        baseline = Scenario(name="Existing")
        baseline.add_drainage_area(DrainageArea(id="id-1", name="Area A"))

        comparison = Scenario(name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="id-2", name="Area A"))

        result = match_entities(baseline, comparison, strategy=MatchStrategy.ID)

        assert len(result.matches) == 0

    def test_name_strategy(self):
        """Name strategy matches by name."""
        baseline = Scenario(name="Existing")
        baseline.add_drainage_area(DrainageArea(id="id-1", name="Area A"))

        comparison = Scenario(name="Proposed")
        comparison.add_drainage_area(DrainageArea(id="id-2", name="Area A"))

        result = match_entities(baseline, comparison, strategy=MatchStrategy.NAME)

        assert len(result.matches) == 1

    def test_unsupported_entity_type_raises(self):
        """Unsupported entity type raises ValueError."""
        baseline = Scenario(name="Existing")
        comparison = Scenario(name="Proposed")

        with pytest.raises(ValueError, match="Unsupported entity type"):
            match_entities(baseline, comparison, entity_type="Unknown")

    def test_empty_scenarios(self):
        """Handles empty scenarios."""
        baseline = Scenario(name="Existing")
        comparison = Scenario(name="Proposed")

        result = match_entities(baseline, comparison)

        assert len(result.matches) == 0
        assert result.unmatched_baseline_ids == []
        assert result.unmatched_comparison_ids == []
