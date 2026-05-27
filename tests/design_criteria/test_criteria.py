"""Tests for design criteria data models."""

import pytest

from civil_toolbox.design_criteria.criteria import (
    RunoffCoefficientEntry,
    RunoffCoefficientTable,
    CurveNumberEntry,
    CurveNumberTable,
    DesignStormDefinition,
    DesignCriteria,
)
from civil_toolbox.design_criteria.errors import (
    InvalidDesignCriteriaError,
    DesignCriteriaLookupError,
)
from civil_toolbox.rainfall.examples import create_example_idf_curve


class TestRunoffCoefficientEntry:
    """Tests for RunoffCoefficientEntry."""

    def test_create_valid_entry(self):
        """Create entry with valid data."""
        entry = RunoffCoefficientEntry(
            land_use="asphalt",
            min=0.70,
            max=0.95,
            typical=0.85,
            description="Asphalt pavement",
        )
        assert entry.land_use == "asphalt"
        assert entry.min == 0.70
        assert entry.max == 0.95
        assert entry.typical == 0.85
        assert entry.description == "Asphalt pavement"

    def test_entry_without_description(self):
        """Entry without description is valid."""
        entry = RunoffCoefficientEntry(
            land_use="concrete",
            min=0.80,
            max=0.95,
            typical=0.90,
        )
        assert entry.description is None

    def test_empty_land_use_raises(self):
        """Empty land_use raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="land_use is required"):
            RunoffCoefficientEntry(land_use="", min=0.5, max=0.6, typical=0.55)

    def test_min_greater_than_max_raises(self):
        """min > max raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="cannot be greater than max"):
            RunoffCoefficientEntry(land_use="test", min=0.8, max=0.5, typical=0.6)

    def test_typical_below_min_raises(self):
        """typical < min raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="typical .* must be between"):
            RunoffCoefficientEntry(land_use="test", min=0.5, max=0.8, typical=0.4)

    def test_typical_above_max_raises(self):
        """typical > max raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="typical .* must be between"):
            RunoffCoefficientEntry(land_use="test", min=0.5, max=0.8, typical=0.9)

    def test_invalid_coefficient_raises(self):
        """Coefficient outside 0-1 raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 0 and 1"):
            RunoffCoefficientEntry(land_use="test", min=-0.1, max=0.5, typical=0.3)

    def test_to_dict(self):
        """to_dict serialization."""
        entry = RunoffCoefficientEntry(
            land_use="lawn", min=0.1, max=0.3, typical=0.2, description="Lawns"
        )
        d = entry.to_dict()
        assert d["land_use"] == "lawn"
        assert d["min"] == 0.1
        assert d["max"] == 0.3
        assert d["typical"] == 0.2
        assert d["description"] == "Lawns"

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "land_use": "park",
            "min": 0.1,
            "max": 0.25,
            "typical": 0.15,
            "description": "Parks",
        }
        entry = RunoffCoefficientEntry.from_dict(data)
        assert entry.land_use == "park"
        assert entry.typical == 0.15

    def test_roundtrip(self):
        """to_dict/from_dict roundtrip."""
        original = RunoffCoefficientEntry(
            land_use="roof", min=0.75, max=0.95, typical=0.85
        )
        restored = RunoffCoefficientEntry.from_dict(original.to_dict())
        assert restored.land_use == original.land_use
        assert restored.min == original.min
        assert restored.max == original.max
        assert restored.typical == original.typical


class TestRunoffCoefficientTable:
    """Tests for RunoffCoefficientTable."""

    @pytest.fixture
    def sample_table(self):
        """Create a sample coefficient table."""
        return RunoffCoefficientTable(
            entries=[
                RunoffCoefficientEntry("asphalt", 0.70, 0.95, 0.85),
                RunoffCoefficientEntry("lawn", 0.10, 0.30, 0.20),
                RunoffCoefficientEntry("roof", 0.75, 0.95, 0.85),
            ],
            source="Test Data",
        )

    def test_create_empty_table(self):
        """Create table with no entries."""
        table = RunoffCoefficientTable()
        assert len(table.entries) == 0
        assert table.source is None

    def test_create_with_entries(self, sample_table):
        """Create table with entries."""
        assert len(sample_table.entries) == 3
        assert sample_table.source == "Test Data"

    def test_duplicate_land_use_raises(self):
        """Duplicate land_use raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="Duplicate land_use"):
            RunoffCoefficientTable(
                entries=[
                    RunoffCoefficientEntry("asphalt", 0.70, 0.95, 0.85),
                    RunoffCoefficientEntry("asphalt", 0.75, 0.90, 0.80),
                ]
            )

    def test_get_land_uses(self, sample_table):
        """get_land_uses returns sorted list."""
        land_uses = sample_table.get_land_uses()
        assert land_uses == ["asphalt", "lawn", "roof"]

    def test_lookup_returns_typical(self, sample_table):
        """lookup returns typical coefficient."""
        assert sample_table.lookup("asphalt") == 0.85
        assert sample_table.lookup("lawn") == 0.20

    def test_lookup_not_found_raises(self, sample_table):
        """lookup raises error for unknown land use."""
        with pytest.raises(DesignCriteriaLookupError, match="not found"):
            sample_table.lookup("unknown")

    def test_lookup_error_shows_available(self, sample_table):
        """lookup error shows available land uses."""
        with pytest.raises(DesignCriteriaLookupError, match="asphalt"):
            sample_table.lookup("unknown")

    def test_lookup_entry_returns_full_entry(self, sample_table):
        """lookup_entry returns full entry."""
        entry = sample_table.lookup_entry("lawn")
        assert entry.land_use == "lawn"
        assert entry.min == 0.10
        assert entry.max == 0.30
        assert entry.typical == 0.20

    def test_lookup_entry_not_found_raises(self, sample_table):
        """lookup_entry raises error for unknown land use."""
        with pytest.raises(DesignCriteriaLookupError, match="not found"):
            sample_table.lookup_entry("unknown")

    def test_to_dict(self, sample_table):
        """to_dict serialization."""
        d = sample_table.to_dict()
        assert len(d["entries"]) == 3
        assert d["source"] == "Test Data"
        assert d["metadata"] == {}

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "entries": [
                {"land_use": "test", "min": 0.5, "max": 0.7, "typical": 0.6}
            ],
            "source": "From Dict",
        }
        table = RunoffCoefficientTable.from_dict(data)
        assert len(table.entries) == 1
        assert table.source == "From Dict"

    def test_roundtrip(self, sample_table):
        """to_dict/from_dict roundtrip."""
        restored = RunoffCoefficientTable.from_dict(sample_table.to_dict())
        assert len(restored.entries) == len(sample_table.entries)
        assert restored.source == sample_table.source


class TestCurveNumberEntry:
    """Tests for CurveNumberEntry."""

    def test_create_valid_entry(self):
        """Create entry with valid data."""
        entry = CurveNumberEntry(
            land_use="open_space",
            soil_groups={"A": 39, "B": 61, "C": 74, "D": 80},
            description="Open space, good condition",
        )
        assert entry.land_use == "open_space"
        assert entry.soil_groups == {"A": 39, "B": 61, "C": 74, "D": 80}

    def test_entry_without_description(self):
        """Entry without description is valid."""
        entry = CurveNumberEntry(
            land_use="impervious",
            soil_groups={"A": 98, "B": 98, "C": 98, "D": 98},
        )
        assert entry.description is None

    def test_empty_land_use_raises(self):
        """Empty land_use raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="land_use is required"):
            CurveNumberEntry(land_use="", soil_groups={"A": 75})

    def test_invalid_soil_group_raises(self):
        """Invalid soil group raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be one of"):
            CurveNumberEntry(land_use="test", soil_groups={"E": 75})

    def test_invalid_curve_number_raises(self):
        """Curve number outside 1-100 raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="between 1 and 100"):
            CurveNumberEntry(land_use="test", soil_groups={"A": 150})

    def test_get_cn(self):
        """get_cn returns curve number for soil group."""
        entry = CurveNumberEntry(
            land_use="test",
            soil_groups={"A": 39, "B": 61, "C": 74, "D": 80},
        )
        assert entry.get_cn("A") == 39
        assert entry.get_cn("B") == 61
        assert entry.get_cn("C") == 74
        assert entry.get_cn("D") == 80

    def test_get_cn_lowercase(self):
        """get_cn accepts lowercase soil group."""
        entry = CurveNumberEntry(
            land_use="test",
            soil_groups={"A": 50, "B": 60},
        )
        assert entry.get_cn("a") == 50
        assert entry.get_cn("b") == 60

    def test_get_cn_not_found_raises(self):
        """get_cn raises error for missing soil group."""
        entry = CurveNumberEntry(
            land_use="test",
            soil_groups={"A": 50},
        )
        with pytest.raises(DesignCriteriaLookupError, match="Soil group 'B' not found"):
            entry.get_cn("B")

    def test_to_dict(self):
        """to_dict serialization."""
        entry = CurveNumberEntry(
            land_use="woods",
            soil_groups={"A": 30, "B": 55},
            description="Woods",
        )
        d = entry.to_dict()
        assert d["land_use"] == "woods"
        assert d["soil_groups"] == {"A": 30, "B": 55}
        assert d["description"] == "Woods"

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "land_use": "pasture",
            "soil_groups": {"A": 39, "B": 61},
            "description": "Pasture",
        }
        entry = CurveNumberEntry.from_dict(data)
        assert entry.land_use == "pasture"
        assert entry.get_cn("A") == 39

    def test_roundtrip(self):
        """to_dict/from_dict roundtrip."""
        original = CurveNumberEntry(
            land_use="test",
            soil_groups={"A": 50, "B": 65, "C": 75, "D": 82},
        )
        restored = CurveNumberEntry.from_dict(original.to_dict())
        assert restored.land_use == original.land_use
        assert restored.soil_groups == original.soil_groups


class TestCurveNumberTable:
    """Tests for CurveNumberTable."""

    @pytest.fixture
    def sample_table(self):
        """Create a sample curve number table."""
        return CurveNumberTable(
            entries=[
                CurveNumberEntry(
                    "impervious",
                    {"A": 98, "B": 98, "C": 98, "D": 98},
                ),
                CurveNumberEntry(
                    "open_space",
                    {"A": 39, "B": 61, "C": 74, "D": 80},
                ),
                CurveNumberEntry(
                    "woods",
                    {"A": 30, "B": 55, "C": 70, "D": 77},
                ),
            ],
            source="Test Data",
        )

    def test_create_empty_table(self):
        """Create table with no entries."""
        table = CurveNumberTable()
        assert len(table.entries) == 0

    def test_create_with_entries(self, sample_table):
        """Create table with entries."""
        assert len(sample_table.entries) == 3

    def test_duplicate_land_use_raises(self):
        """Duplicate land_use raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="Duplicate land_use"):
            CurveNumberTable(
                entries=[
                    CurveNumberEntry("impervious", {"A": 98}),
                    CurveNumberEntry("impervious", {"B": 98}),
                ]
            )

    def test_get_land_uses(self, sample_table):
        """get_land_uses returns sorted list."""
        land_uses = sample_table.get_land_uses()
        assert land_uses == ["impervious", "open_space", "woods"]

    def test_lookup(self, sample_table):
        """lookup returns curve number."""
        assert sample_table.lookup("impervious", "A") == 98
        assert sample_table.lookup("open_space", "B") == 61
        assert sample_table.lookup("woods", "D") == 77

    def test_lookup_land_use_not_found(self, sample_table):
        """lookup raises error for unknown land use."""
        with pytest.raises(DesignCriteriaLookupError, match="not found"):
            sample_table.lookup("unknown", "A")

    def test_lookup_soil_group_not_found(self, sample_table):
        """lookup raises error for missing soil group."""
        table = CurveNumberTable(
            entries=[CurveNumberEntry("partial", {"A": 50, "B": 60})]
        )
        with pytest.raises(DesignCriteriaLookupError, match="Soil group 'C'"):
            table.lookup("partial", "C")

    def test_lookup_entry(self, sample_table):
        """lookup_entry returns full entry."""
        entry = sample_table.lookup_entry("woods")
        assert entry.land_use == "woods"
        assert entry.get_cn("A") == 30

    def test_lookup_entry_not_found(self, sample_table):
        """lookup_entry raises error for unknown land use."""
        with pytest.raises(DesignCriteriaLookupError, match="not found"):
            sample_table.lookup_entry("unknown")

    def test_to_dict(self, sample_table):
        """to_dict serialization."""
        d = sample_table.to_dict()
        assert len(d["entries"]) == 3
        assert d["source"] == "Test Data"

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "entries": [
                {"land_use": "test", "soil_groups": {"A": 50, "B": 60}}
            ],
            "source": "From Dict",
        }
        table = CurveNumberTable.from_dict(data)
        assert len(table.entries) == 1
        assert table.lookup("test", "A") == 50

    def test_roundtrip(self, sample_table):
        """to_dict/from_dict roundtrip."""
        restored = CurveNumberTable.from_dict(sample_table.to_dict())
        assert len(restored.entries) == len(sample_table.entries)


class TestDesignStormDefinition:
    """Tests for DesignStormDefinition."""

    def test_create_valid_storm(self):
        """Create storm definition with valid data."""
        storm = DesignStormDefinition(
            name="100-year 24-hour",
            return_period_years=100,
            duration_minutes=1440,
            description="Major flood event",
        )
        assert storm.name == "100-year 24-hour"
        assert storm.return_period_years == 100
        assert storm.duration_minutes == 1440
        assert storm.description == "Major flood event"

    def test_storm_without_description(self):
        """Storm without description is valid."""
        storm = DesignStormDefinition(
            name="10-year 15-minute",
            return_period_years=10,
            duration_minutes=15,
        )
        assert storm.description is None

    def test_empty_name_raises(self):
        """Empty name raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="name is required"):
            DesignStormDefinition(name="", return_period_years=10, duration_minutes=60)

    def test_invalid_return_period_raises(self):
        """Invalid return period raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be positive"):
            DesignStormDefinition(
                name="test", return_period_years=0, duration_minutes=60
            )

    def test_invalid_duration_raises(self):
        """Invalid duration raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="must be positive"):
            DesignStormDefinition(
                name="test", return_period_years=10, duration_minutes=-5
            )

    def test_to_dict(self):
        """to_dict serialization."""
        storm = DesignStormDefinition(
            name="test",
            return_period_years=25,
            duration_minutes=720,
            description="Test storm",
            metadata={"key": "value"},
        )
        d = storm.to_dict()
        assert d["name"] == "test"
        assert d["return_period_years"] == 25
        assert d["duration_minutes"] == 720
        assert d["description"] == "Test storm"
        assert d["metadata"] == {"key": "value"}

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "name": "2-year 24-hour",
            "return_period_years": 2,
            "duration_minutes": 1440,
            "description": "Minor storm",
        }
        storm = DesignStormDefinition.from_dict(data)
        assert storm.name == "2-year 24-hour"
        assert storm.return_period_years == 2

    def test_roundtrip(self):
        """to_dict/from_dict roundtrip."""
        original = DesignStormDefinition(
            name="50-year 6-hour",
            return_period_years=50,
            duration_minutes=360,
        )
        restored = DesignStormDefinition.from_dict(original.to_dict())
        assert restored.name == original.name
        assert restored.return_period_years == original.return_period_years
        assert restored.duration_minutes == original.duration_minutes


class TestDesignCriteria:
    """Tests for DesignCriteria."""

    @pytest.fixture
    def minimal_criteria(self):
        """Create minimal criteria."""
        return DesignCriteria(
            id="test-criteria",
            name="Test Criteria",
        )

    @pytest.fixture
    def full_criteria(self):
        """Create criteria with all components."""
        return DesignCriteria(
            id="full-criteria",
            name="Full Criteria",
            jurisdiction="Test County",
            source="Test Data",
            idf_curve=create_example_idf_curve(),
            runoff_coefficients=RunoffCoefficientTable(
                entries=[
                    RunoffCoefficientEntry("asphalt", 0.70, 0.95, 0.85),
                    RunoffCoefficientEntry("lawn", 0.10, 0.30, 0.20),
                ]
            ),
            curve_numbers=CurveNumberTable(
                entries=[
                    CurveNumberEntry("impervious", {"A": 98, "B": 98, "C": 98, "D": 98}),
                    CurveNumberEntry("open_space", {"A": 39, "B": 61, "C": 74, "D": 80}),
                ]
            ),
            design_storms=[
                DesignStormDefinition("10-year 24-hour", 10, 1440),
                DesignStormDefinition("100-year 24-hour", 100, 1440),
            ],
        )

    def test_create_minimal(self, minimal_criteria):
        """Create criteria with minimal data."""
        assert minimal_criteria.id == "test-criteria"
        assert minimal_criteria.name == "Test Criteria"
        assert minimal_criteria.jurisdiction is None
        assert minimal_criteria.idf_curve is None
        assert minimal_criteria.runoff_coefficients is None
        assert minimal_criteria.curve_numbers is None
        assert len(minimal_criteria.design_storms) == 0

    def test_empty_id_raises(self):
        """Empty id raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="id is required"):
            DesignCriteria(id="", name="Test")

    def test_empty_name_raises(self):
        """Empty name raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="name is required"):
            DesignCriteria(id="test", name="")

    def test_duplicate_storm_names_raises(self):
        """Duplicate design storm names raises error."""
        with pytest.raises(InvalidDesignCriteriaError, match="Duplicate design storm"):
            DesignCriteria(
                id="test",
                name="Test",
                design_storms=[
                    DesignStormDefinition("storm1", 10, 60),
                    DesignStormDefinition("storm1", 25, 120),
                ],
            )

    def test_get_idf_curve(self, full_criteria):
        """get_idf_curve returns embedded curve."""
        curve = full_criteria.get_idf_curve()
        assert curve is not None

    def test_get_idf_curve_none(self, minimal_criteria):
        """get_idf_curve returns None when not set."""
        assert minimal_criteria.get_idf_curve() is None

    def test_lookup_runoff_coefficient(self, full_criteria):
        """lookup_runoff_coefficient returns typical value."""
        assert full_criteria.lookup_runoff_coefficient("asphalt") == 0.85
        assert full_criteria.lookup_runoff_coefficient("lawn") == 0.20

    def test_lookup_runoff_coefficient_no_table(self, minimal_criteria):
        """lookup_runoff_coefficient raises when no table."""
        with pytest.raises(DesignCriteriaLookupError, match="not defined"):
            minimal_criteria.lookup_runoff_coefficient("asphalt")

    def test_lookup_runoff_coefficient_not_found(self, full_criteria):
        """lookup_runoff_coefficient raises for unknown land use."""
        with pytest.raises(DesignCriteriaLookupError, match="not found"):
            full_criteria.lookup_runoff_coefficient("unknown")

    def test_lookup_curve_number(self, full_criteria):
        """lookup_curve_number returns value."""
        assert full_criteria.lookup_curve_number("impervious", "A") == 98
        assert full_criteria.lookup_curve_number("open_space", "B") == 61

    def test_lookup_curve_number_no_table(self, minimal_criteria):
        """lookup_curve_number raises when no table."""
        with pytest.raises(DesignCriteriaLookupError, match="not defined"):
            minimal_criteria.lookup_curve_number("impervious", "A")

    def test_get_design_storm(self, full_criteria):
        """get_design_storm returns storm definition."""
        storm = full_criteria.get_design_storm("10-year 24-hour")
        assert storm.name == "10-year 24-hour"
        assert storm.return_period_years == 10

    def test_get_design_storm_not_found(self, full_criteria):
        """get_design_storm raises for unknown storm."""
        with pytest.raises(DesignCriteriaLookupError, match="not found"):
            full_criteria.get_design_storm("unknown")

    def test_get_design_storm_names(self, full_criteria):
        """get_design_storm_names returns all names."""
        names = full_criteria.get_design_storm_names()
        assert "10-year 24-hour" in names
        assert "100-year 24-hour" in names

    def test_generate_storm_event(self, full_criteria):
        """generate_storm_event creates StormEvent from definition."""
        event = full_criteria.generate_storm_event("10-year 24-hour")
        assert event.name == "10-year 24-hour"
        assert event.return_period_years == 10
        assert event.duration_hours == 24

    def test_generate_storm_event_no_idf(self, minimal_criteria):
        """generate_storm_event raises without IDF curve."""
        minimal_criteria.design_storms.append(
            DesignStormDefinition("test", 10, 60)
        )
        with pytest.raises(DesignCriteriaLookupError, match="no embedded IDF"):
            minimal_criteria.generate_storm_event("test")

    def test_to_dict(self, full_criteria):
        """to_dict serialization."""
        d = full_criteria.to_dict()
        assert d["id"] == "full-criteria"
        assert d["name"] == "Full Criteria"
        assert d["jurisdiction"] == "Test County"
        assert d["idf_curve"] is not None
        assert d["runoff_coefficients"] is not None
        assert d["curve_numbers"] is not None
        assert len(d["design_storms"]) == 2

    def test_from_dict(self):
        """from_dict deserialization."""
        data = {
            "id": "from-dict",
            "name": "From Dict",
            "jurisdiction": "Test",
            "design_storms": [
                {"name": "test", "return_period_years": 10, "duration_minutes": 60}
            ],
        }
        criteria = DesignCriteria.from_dict(data)
        assert criteria.id == "from-dict"
        assert criteria.name == "From Dict"
        assert len(criteria.design_storms) == 1

    def test_roundtrip(self, full_criteria):
        """to_dict/from_dict roundtrip."""
        restored = DesignCriteria.from_dict(full_criteria.to_dict())
        assert restored.id == full_criteria.id
        assert restored.name == full_criteria.name
        assert restored.jurisdiction == full_criteria.jurisdiction
        assert len(restored.design_storms) == len(full_criteria.design_storms)
        assert restored.lookup_runoff_coefficient("asphalt") == 0.85
        assert restored.lookup_curve_number("impervious", "A") == 98

    def test_idf_curve_id_stored(self):
        """idf_curve_id is stored for registry lookup."""
        criteria = DesignCriteria(
            id="test",
            name="Test",
            idf_curve_id="external-idf-123",
        )
        assert criteria.idf_curve_id == "external-idf-123"

    def test_both_idf_fields(self):
        """Both idf_curve and idf_curve_id can be set."""
        criteria = DesignCriteria(
            id="test",
            name="Test",
            idf_curve=create_example_idf_curve(),
            idf_curve_id="backup-ref",
        )
        assert criteria.idf_curve is not None
        assert criteria.idf_curve_id == "backup-ref"

    def test_generate_storm_event_includes_metadata(self, full_criteria):
        """generate_storm_event includes criteria metadata."""
        event = full_criteria.generate_storm_event("10-year 24-hour")
        assert event.metadata["design_criteria_id"] == "full-criteria"
        assert event.metadata["design_criteria_name"] == "Full Criteria"
        assert event.metadata["design_storm_name"] == "10-year 24-hour"
        assert "idf_curve_id" in event.metadata
        assert "idf_curve_name" in event.metadata

    def test_generate_all_storm_events(self, full_criteria):
        """generate_all_storm_events creates events for all storms."""
        events = full_criteria.generate_all_storm_events()
        assert len(events) == 2
        names = [e.name for e in events]
        assert "10-year 24-hour" in names
        assert "100-year 24-hour" in names

    def test_generate_all_storm_events_no_idf(self, minimal_criteria):
        """generate_all_storm_events raises without IDF curve."""
        minimal_criteria.design_storms.append(
            DesignStormDefinition("test", 10, 60)
        )
        with pytest.raises(DesignCriteriaLookupError, match="no embedded IDF"):
            minimal_criteria.generate_all_storm_events()

    def test_lookup_runoff_coefficient_range(self, full_criteria):
        """lookup_runoff_coefficient_range returns min/max tuple."""
        min_c, max_c = full_criteria.lookup_runoff_coefficient_range("asphalt")
        assert min_c == 0.70
        assert max_c == 0.95

    def test_lookup_runoff_coefficient_range_no_table(self, minimal_criteria):
        """lookup_runoff_coefficient_range raises when no table."""
        with pytest.raises(DesignCriteriaLookupError, match="not defined"):
            minimal_criteria.lookup_runoff_coefficient_range("asphalt")


class TestLandUseNormalization:
    """Tests for land use key normalization in lookups."""

    def test_runoff_coefficient_case_insensitive(self):
        """Runoff coefficient lookup is case insensitive."""
        table = RunoffCoefficientTable(
            entries=[RunoffCoefficientEntry("asphalt", 0.70, 0.95, 0.85)]
        )
        assert table.lookup("ASPHALT") == 0.85
        assert table.lookup("Asphalt") == 0.85
        assert table.lookup("asphalt") == 0.85

    def test_runoff_coefficient_whitespace_stripped(self):
        """Runoff coefficient lookup strips whitespace."""
        table = RunoffCoefficientTable(
            entries=[RunoffCoefficientEntry("asphalt", 0.70, 0.95, 0.85)]
        )
        assert table.lookup("  asphalt  ") == 0.85
        assert table.lookup("asphalt ") == 0.85

    def test_runoff_coefficient_spaces_to_underscores(self):
        """Runoff coefficient lookup converts spaces to underscores."""
        table = RunoffCoefficientTable(
            entries=[RunoffCoefficientEntry("open_space", 0.10, 0.30, 0.20)]
        )
        assert table.lookup("open space") == 0.20
        assert table.lookup("Open Space") == 0.20

    def test_curve_number_case_insensitive(self):
        """Curve number lookup is case insensitive."""
        table = CurveNumberTable(
            entries=[
                CurveNumberEntry("impervious", {"A": 98, "B": 98, "C": 98, "D": 98})
            ]
        )
        assert table.lookup("IMPERVIOUS", "A") == 98
        assert table.lookup("Impervious", "a") == 98

    def test_curve_number_whitespace_stripped(self):
        """Curve number lookup strips whitespace."""
        table = CurveNumberTable(
            entries=[
                CurveNumberEntry("woods_good", {"A": 30, "B": 55, "C": 70, "D": 77})
            ]
        )
        assert table.lookup("  woods_good  ", "B") == 55

    def test_curve_number_spaces_to_underscores(self):
        """Curve number lookup converts spaces to underscores."""
        table = CurveNumberTable(
            entries=[
                CurveNumberEntry("woods_good", {"A": 30, "B": 55, "C": 70, "D": 77})
            ]
        )
        assert table.lookup("woods good", "A") == 30
        assert table.lookup("Woods Good", "B") == 55
