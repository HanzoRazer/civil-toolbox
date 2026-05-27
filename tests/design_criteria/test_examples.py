"""Tests for example design criteria data."""

import pytest

from civil_toolbox.design_criteria.examples import (
    create_example_runoff_coefficient_table,
    create_example_curve_number_table,
    create_example_design_criteria,
)
from civil_toolbox.design_criteria.criteria import (
    RunoffCoefficientTable,
    CurveNumberTable,
    DesignCriteria,
)


class TestExampleRunoffCoefficientTable:
    """Tests for create_example_runoff_coefficient_table."""

    @pytest.fixture
    def table(self):
        """Create example runoff coefficient table."""
        return create_example_runoff_coefficient_table()

    def test_returns_table(self, table):
        """Returns RunoffCoefficientTable."""
        assert isinstance(table, RunoffCoefficientTable)

    def test_has_entries(self, table):
        """Table has entries."""
        assert len(table.entries) > 0

    def test_common_land_uses_present(self, table):
        """Common land uses are present."""
        land_uses = table.get_land_uses()
        assert "asphalt" in land_uses
        assert "concrete" in land_uses
        assert "roof" in land_uses
        assert "lawn_sandy" in land_uses
        assert "lawn_clay" in land_uses
        assert "commercial" in land_uses

    def test_asphalt_coefficient(self, table):
        """Asphalt has expected coefficient."""
        coeff = table.lookup("asphalt")
        assert 0.7 <= coeff <= 0.95

    def test_lawn_sandy_coefficient(self, table):
        """Lawn sandy has expected coefficient."""
        coeff = table.lookup("lawn_sandy")
        assert 0.05 <= coeff <= 0.20

    def test_entries_have_descriptions(self, table):
        """Entries have descriptions."""
        entry = table.lookup_entry("asphalt")
        assert entry.description is not None
        assert len(entry.description) > 0

    def test_source_indicates_synthetic(self, table):
        """Source indicates synthetic data."""
        assert table.source is not None
        assert "Synthetic" in table.source or "Demo" in table.source

    def test_metadata_indicates_synthetic(self, table):
        """Metadata indicates synthetic data."""
        assert table.metadata.get("synthetic") is True
        assert table.metadata.get("for_testing_only") is True

    def test_all_entries_valid(self, table):
        """All entries pass validation."""
        for entry in table.entries:
            assert 0 <= entry.min <= 1
            assert 0 <= entry.max <= 1
            assert 0 <= entry.typical <= 1
            assert entry.min <= entry.typical <= entry.max


class TestExampleCurveNumberTable:
    """Tests for create_example_curve_number_table."""

    @pytest.fixture
    def table(self):
        """Create example curve number table."""
        return create_example_curve_number_table()

    def test_returns_table(self, table):
        """Returns CurveNumberTable."""
        assert isinstance(table, CurveNumberTable)

    def test_has_entries(self, table):
        """Table has entries."""
        assert len(table.entries) > 0

    def test_common_land_uses_present(self, table):
        """Common land uses are present."""
        land_uses = table.get_land_uses()
        assert "impervious" in land_uses
        assert "open_space_good" in land_uses
        assert "residential_half_acre" in land_uses
        assert "commercial" in land_uses
        assert "woods_good" in land_uses

    def test_impervious_curve_number(self, table):
        """Impervious has expected CN (near 98)."""
        cn = table.lookup("impervious", "A")
        assert cn == 98

    def test_woods_good_curve_number(self, table):
        """Woods good has lower CN for group A."""
        cn = table.lookup("woods_good", "A")
        assert cn < 50

    def test_all_soil_groups_present(self, table):
        """All entries have all four soil groups."""
        for entry in table.entries:
            assert "A" in entry.soil_groups
            assert "B" in entry.soil_groups
            assert "C" in entry.soil_groups
            assert "D" in entry.soil_groups

    def test_cn_increases_by_soil_group(self, table):
        """CN generally increases from A to D."""
        entry = table.lookup_entry("open_space_good")
        assert entry.soil_groups["A"] < entry.soil_groups["B"]
        assert entry.soil_groups["B"] < entry.soil_groups["C"]
        assert entry.soil_groups["C"] < entry.soil_groups["D"]

    def test_entries_have_descriptions(self, table):
        """Entries have descriptions."""
        entry = table.lookup_entry("impervious")
        assert entry.description is not None
        assert len(entry.description) > 0

    def test_source_indicates_synthetic(self, table):
        """Source indicates synthetic data."""
        assert table.source is not None
        assert "Synthetic" in table.source or "Demo" in table.source

    def test_metadata_indicates_synthetic(self, table):
        """Metadata indicates synthetic data."""
        assert table.metadata.get("synthetic") is True
        assert table.metadata.get("for_testing_only") is True

    def test_all_entries_valid(self, table):
        """All entries pass validation."""
        for entry in table.entries:
            for sg, cn in entry.soil_groups.items():
                assert sg in {"A", "B", "C", "D"}
                assert 0 <= cn <= 100


class TestExampleDesignCriteria:
    """Tests for create_example_design_criteria."""

    @pytest.fixture
    def criteria(self):
        """Create example design criteria."""
        return create_example_design_criteria()

    def test_returns_criteria(self, criteria):
        """Returns DesignCriteria."""
        assert isinstance(criteria, DesignCriteria)

    def test_has_id_and_name(self, criteria):
        """Has id and name."""
        assert criteria.id == "example-synthetic"
        assert criteria.name == "Example Design Criteria"

    def test_has_jurisdiction(self, criteria):
        """Has jurisdiction."""
        assert criteria.jurisdiction is not None
        assert "Synthetic" in criteria.jurisdiction or "Example" in criteria.jurisdiction

    def test_has_idf_curve(self, criteria):
        """Has embedded IDF curve."""
        assert criteria.idf_curve is not None
        curve = criteria.get_idf_curve()
        assert curve is not None

    def test_has_runoff_coefficients(self, criteria):
        """Has runoff coefficient table."""
        assert criteria.runoff_coefficients is not None
        coeff = criteria.lookup_runoff_coefficient("asphalt")
        assert coeff > 0

    def test_has_curve_numbers(self, criteria):
        """Has curve number table."""
        assert criteria.curve_numbers is not None
        cn = criteria.lookup_curve_number("impervious", "B")
        assert cn > 0

    def test_has_design_storms(self, criteria):
        """Has design storm definitions."""
        assert len(criteria.design_storms) > 0
        names = criteria.get_design_storm_names()
        assert len(names) > 0

    def test_common_storms_present(self, criteria):
        """Common design storms are present."""
        names = criteria.get_design_storm_names()
        assert "2-year 24-hour" in names
        assert "10-year 24-hour" in names
        assert "100-year 24-hour" in names

    def test_24_hour_storms(self, criteria):
        """24-hour storms have correct duration."""
        storm = criteria.get_design_storm("100-year 24-hour")
        assert storm.duration_minutes == 1440
        assert storm.return_period_years == 100

    def test_15_minute_storms(self, criteria):
        """15-minute storms have correct duration."""
        names = criteria.get_design_storm_names()
        if "10-year 15-minute" in names:
            storm = criteria.get_design_storm("10-year 15-minute")
            assert storm.duration_minutes == 15
            assert storm.return_period_years == 10

    def test_generate_storm_event(self, criteria):
        """Can generate storm event from definition."""
        event = criteria.generate_storm_event("10-year 24-hour")
        assert event.name == "10-year 24-hour"
        assert event.return_period_years == 10
        assert event.duration_hours == 24
        assert event.rainfall_intensity_in_per_hr > 0
        assert event.rainfall_depth_in > 0

    def test_metadata_indicates_synthetic(self, criteria):
        """Metadata indicates synthetic data."""
        assert criteria.metadata.get("synthetic") is True
        assert criteria.metadata.get("for_testing_only") is True
        assert "warning" in criteria.metadata

    def test_roundtrip(self, criteria):
        """to_dict/from_dict roundtrip preserves data."""
        restored = DesignCriteria.from_dict(criteria.to_dict())
        assert restored.id == criteria.id
        assert restored.name == criteria.name
        assert restored.lookup_runoff_coefficient("asphalt") == \
            criteria.lookup_runoff_coefficient("asphalt")
        assert restored.lookup_curve_number("impervious", "A") == \
            criteria.lookup_curve_number("impervious", "A")
        assert len(restored.design_storms) == len(criteria.design_storms)
