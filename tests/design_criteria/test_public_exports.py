"""Tests for design criteria public exports."""


class TestCriteriaClassImports:
    """Tests for criteria class imports."""

    def test_runoff_coefficient_entry_imports(self):
        """RunoffCoefficientEntry imports from package."""
        from civil_toolbox.design_criteria import RunoffCoefficientEntry
        assert RunoffCoefficientEntry is not None

    def test_runoff_coefficient_table_imports(self):
        """RunoffCoefficientTable imports from package."""
        from civil_toolbox.design_criteria import RunoffCoefficientTable
        assert RunoffCoefficientTable is not None

    def test_curve_number_entry_imports(self):
        """CurveNumberEntry imports from package."""
        from civil_toolbox.design_criteria import CurveNumberEntry
        assert CurveNumberEntry is not None

    def test_curve_number_table_imports(self):
        """CurveNumberTable imports from package."""
        from civil_toolbox.design_criteria import CurveNumberTable
        assert CurveNumberTable is not None

    def test_design_storm_definition_imports(self):
        """DesignStormDefinition imports from package."""
        from civil_toolbox.design_criteria import DesignStormDefinition
        assert DesignStormDefinition is not None

    def test_design_criteria_imports(self):
        """DesignCriteria imports from package."""
        from civil_toolbox.design_criteria import DesignCriteria
        assert DesignCriteria is not None


class TestLibraryImports:
    """Tests for library class imports."""

    def test_design_criteria_library_imports(self):
        """DesignCriteriaLibrary imports from package."""
        from civil_toolbox.design_criteria import DesignCriteriaLibrary
        assert DesignCriteriaLibrary is not None


class TestErrorImports:
    """Tests for error class imports."""

    def test_design_criteria_error_imports(self):
        """DesignCriteriaError imports from package."""
        from civil_toolbox.design_criteria import DesignCriteriaError
        assert DesignCriteriaError is not None

    def test_invalid_design_criteria_error_imports(self):
        """InvalidDesignCriteriaError imports from package."""
        from civil_toolbox.design_criteria import InvalidDesignCriteriaError
        assert InvalidDesignCriteriaError is not None

    def test_design_criteria_lookup_error_imports(self):
        """DesignCriteriaLookupError imports from package."""
        from civil_toolbox.design_criteria import DesignCriteriaLookupError
        assert DesignCriteriaLookupError is not None

    def test_criteria_not_found_error_imports(self):
        """CriteriaNotFoundError imports from package."""
        from civil_toolbox.design_criteria import CriteriaNotFoundError
        assert CriteriaNotFoundError is not None


class TestValidationImports:
    """Tests for validation imports."""

    def test_valid_soil_groups_imports(self):
        """VALID_SOIL_GROUPS imports from package."""
        from civil_toolbox.design_criteria import VALID_SOIL_GROUPS
        assert VALID_SOIL_GROUPS == {"A", "B", "C", "D"}

    def test_normalize_land_use_key_imports(self):
        """normalize_land_use_key imports from package."""
        from civil_toolbox.design_criteria import normalize_land_use_key
        assert normalize_land_use_key("  Test  ") == "test"

    def test_validate_runoff_coefficient_imports(self):
        """validate_runoff_coefficient imports from package."""
        from civil_toolbox.design_criteria import validate_runoff_coefficient
        assert validate_runoff_coefficient(0.5, "c") == 0.5

    def test_validate_curve_number_imports(self):
        """validate_curve_number imports from package."""
        from civil_toolbox.design_criteria import validate_curve_number
        assert validate_curve_number(75, "cn") == 75

    def test_validate_soil_group_imports(self):
        """validate_soil_group imports from package."""
        from civil_toolbox.design_criteria import validate_soil_group
        assert validate_soil_group("a", "sg") == "A"

    def test_validate_return_period_imports(self):
        """validate_return_period imports from package."""
        from civil_toolbox.design_criteria import validate_return_period
        assert validate_return_period(10, "rp") == 10

    def test_validate_duration_minutes_imports(self):
        """validate_duration_minutes imports from package."""
        from civil_toolbox.design_criteria import validate_duration_minutes
        assert validate_duration_minutes(60.0, "d") == 60.0


class TestExampleImports:
    """Tests for example function imports."""

    def test_create_example_runoff_coefficient_table_imports(self):
        """create_example_runoff_coefficient_table imports from package."""
        from civil_toolbox.design_criteria import create_example_runoff_coefficient_table
        table = create_example_runoff_coefficient_table()
        assert len(table.entries) > 0

    def test_create_example_curve_number_table_imports(self):
        """create_example_curve_number_table imports from package."""
        from civil_toolbox.design_criteria import create_example_curve_number_table
        table = create_example_curve_number_table()
        assert len(table.entries) > 0

    def test_create_example_design_criteria_imports(self):
        """create_example_design_criteria imports from package."""
        from civil_toolbox.design_criteria import create_example_design_criteria
        criteria = create_example_design_criteria()
        assert criteria.id == "example-synthetic"

    def test_create_example_design_criteria_library_imports(self):
        """create_example_design_criteria_library imports from package."""
        from civil_toolbox.design_criteria import create_example_design_criteria_library
        library = create_example_design_criteria_library()
        assert len(library) > 0
        assert library.has("example-synthetic")


class TestAllExports:
    """Tests for __all__ exports."""

    def test_all_exports_are_importable(self):
        """All items in __all__ are importable."""
        from civil_toolbox import design_criteria
        for name in design_criteria.__all__:
            assert hasattr(design_criteria, name), f"{name} not in module"
