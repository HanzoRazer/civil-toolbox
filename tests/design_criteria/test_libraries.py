"""Tests for DesignCriteriaLibrary registry."""

import pytest

from civil_toolbox.design_criteria.criteria import DesignCriteria
from civil_toolbox.design_criteria.libraries import DesignCriteriaLibrary
from civil_toolbox.design_criteria.errors import (
    CriteriaNotFoundError,
    InvalidDesignCriteriaError,
)


class TestDesignCriteriaLibrary:
    """Tests for DesignCriteriaLibrary."""

    @pytest.fixture
    def sample_criteria(self):
        """Create sample criteria for testing."""
        return DesignCriteria(
            id="test-county",
            name="Test County Criteria",
            jurisdiction="Test County",
        )

    @pytest.fixture
    def another_criteria(self):
        """Create another criteria for testing."""
        return DesignCriteria(
            id="another-county",
            name="Another County Criteria",
            jurisdiction="Another County",
        )

    def test_create_empty_library(self):
        """Create empty library."""
        library = DesignCriteriaLibrary()
        assert len(library) == 0
        assert library.name is None

    def test_create_library_with_name(self):
        """Create library with name and metadata."""
        library = DesignCriteriaLibrary(
            name="Regional Standards",
            metadata={"region": "Southwest"},
        )
        assert library.name == "Regional Standards"
        assert library.metadata["region"] == "Southwest"

    def test_register_criteria(self, sample_criteria):
        """Register criteria in library."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        assert len(library) == 1
        assert library.has("test-county")

    def test_register_duplicate_raises(self, sample_criteria):
        """Register duplicate ID raises error."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        with pytest.raises(InvalidDesignCriteriaError, match="already registered"):
            library.register(sample_criteria)

    def test_register_overwrite(self, sample_criteria):
        """Register with overwrite replaces existing."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)

        updated = DesignCriteria(
            id="test-county",
            name="Updated Criteria",
            jurisdiction="Test County Updated",
        )
        library.register(updated, overwrite=True)

        assert len(library) == 1
        retrieved = library.get("test-county")
        assert retrieved.name == "Updated Criteria"

    def test_unregister(self, sample_criteria):
        """Unregister removes criteria."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        assert library.has("test-county")

        library.unregister("test-county")
        assert not library.has("test-county")
        assert len(library) == 0

    def test_unregister_not_found_raises(self):
        """Unregister unknown ID raises error."""
        library = DesignCriteriaLibrary()
        with pytest.raises(CriteriaNotFoundError, match="not found"):
            library.unregister("unknown")

    def test_get(self, sample_criteria):
        """Get retrieves criteria by ID."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)

        retrieved = library.get("test-county")
        assert retrieved.id == "test-county"
        assert retrieved.name == "Test County Criteria"

    def test_get_not_found_raises(self):
        """Get unknown ID raises error."""
        library = DesignCriteriaLibrary()
        with pytest.raises(CriteriaNotFoundError, match="not found"):
            library.get("unknown")

    def test_get_error_shows_available(self, sample_criteria, another_criteria):
        """Get error shows available IDs."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        library.register(another_criteria)

        with pytest.raises(CriteriaNotFoundError, match="test-county"):
            library.get("unknown")

    def test_has(self, sample_criteria):
        """has returns boolean."""
        library = DesignCriteriaLibrary()
        assert not library.has("test-county")

        library.register(sample_criteria)
        assert library.has("test-county")

    def test_list_ids(self, sample_criteria, another_criteria):
        """list_ids returns sorted IDs."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        library.register(another_criteria)

        ids = library.list_ids()
        assert ids == ["another-county", "test-county"]

    def test_list_ids_empty(self):
        """list_ids returns empty list when empty."""
        library = DesignCriteriaLibrary()
        assert library.list_ids() == []

    def test_list_criteria(self, sample_criteria, another_criteria):
        """list_criteria returns all criteria sorted by ID."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        library.register(another_criteria)

        criteria_list = library.list_criteria()
        assert len(criteria_list) == 2
        assert criteria_list[0].id == "another-county"
        assert criteria_list[1].id == "test-county"

    def test_find_by_jurisdiction(self, sample_criteria, another_criteria):
        """find_by_jurisdiction finds by partial match."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        library.register(another_criteria)

        results = library.find_by_jurisdiction("Test")
        assert len(results) == 1
        assert results[0].id == "test-county"

    def test_find_by_jurisdiction_case_insensitive(self, sample_criteria):
        """find_by_jurisdiction is case insensitive."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)

        results = library.find_by_jurisdiction("test county")
        assert len(results) == 1

        results = library.find_by_jurisdiction("TEST COUNTY")
        assert len(results) == 1

    def test_find_by_jurisdiction_partial_match(self, sample_criteria, another_criteria):
        """find_by_jurisdiction matches partial strings."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        library.register(another_criteria)

        results = library.find_by_jurisdiction("County")
        assert len(results) == 2

    def test_find_by_jurisdiction_no_match(self, sample_criteria):
        """find_by_jurisdiction returns empty for no match."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)

        results = library.find_by_jurisdiction("Nonexistent")
        assert results == []

    def test_find_by_jurisdiction_none_skipped(self):
        """find_by_jurisdiction skips criteria with None jurisdiction."""
        library = DesignCriteriaLibrary()
        library.register(DesignCriteria(id="no-jurisdiction", name="No Jurisdiction"))

        results = library.find_by_jurisdiction("Test")
        assert results == []

    def test_clear(self, sample_criteria, another_criteria):
        """clear removes all criteria."""
        library = DesignCriteriaLibrary()
        library.register(sample_criteria)
        library.register(another_criteria)
        assert len(library) == 2

        library.clear()
        assert len(library) == 0
        assert library.list_ids() == []

    def test_len(self, sample_criteria, another_criteria):
        """len returns count of criteria."""
        library = DesignCriteriaLibrary()
        assert len(library) == 0

        library.register(sample_criteria)
        assert len(library) == 1

        library.register(another_criteria)
        assert len(library) == 2

    def test_to_dict(self, sample_criteria, another_criteria):
        """to_dict serialization."""
        library = DesignCriteriaLibrary(
            name="Test Library",
            metadata={"version": "1.0"},
        )
        library.register(sample_criteria)
        library.register(another_criteria)

        d = library.to_dict()
        assert d["name"] == "Test Library"
        assert d["metadata"] == {"version": "1.0"}
        assert len(d["criteria"]) == 2

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "name": "From Dict Library",
            "metadata": {"source": "test"},
            "criteria": [
                {"id": "c1", "name": "Criteria 1"},
                {"id": "c2", "name": "Criteria 2"},
            ],
        }
        library = DesignCriteriaLibrary.from_dict(data)
        assert library.name == "From Dict Library"
        assert len(library) == 2
        assert library.has("c1")
        assert library.has("c2")

    def test_from_dict_empty(self):
        """from_dict with empty criteria list."""
        data = {"name": "Empty Library"}
        library = DesignCriteriaLibrary.from_dict(data)
        assert library.name == "Empty Library"
        assert len(library) == 0

    def test_roundtrip(self, sample_criteria, another_criteria):
        """to_dict/from_dict roundtrip."""
        original = DesignCriteriaLibrary(
            name="Original",
            metadata={"key": "value"},
        )
        original.register(sample_criteria)
        original.register(another_criteria)

        restored = DesignCriteriaLibrary.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.metadata == original.metadata
        assert len(restored) == len(original)
        assert restored.list_ids() == original.list_ids()

        for cid in original.list_ids():
            orig_c = original.get(cid)
            rest_c = restored.get(cid)
            assert rest_c.id == orig_c.id
            assert rest_c.name == orig_c.name
