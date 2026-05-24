"""Tests for infrastructure sizing public exports."""


class TestModelImports:
    """Tests for model imports."""

    def test_infrastructure_check_result_imports(self):
        """InfrastructureCheckResult imports from package."""
        from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult
        result = InfrastructureCheckResult(
            element_id="e1",
            element_name="E-1",
            element_type="pipe",
            passes=True,
        )
        assert result.passes is True

    def test_infrastructure_check_warning_imports(self):
        """InfrastructureCheckWarning imports from package."""
        from civil_toolbox.infrastructure_sizing import InfrastructureCheckWarning
        warning = InfrastructureCheckWarning(
            warning_code="TEST",
            message="Test warning",
        )
        assert warning.warning_code == "TEST"


class TestManningImports:
    """Tests for Manning function imports."""

    def test_manning_capacity_cfs_imports(self):
        """manning_capacity_cfs imports from package."""
        from civil_toolbox.infrastructure_sizing import manning_capacity_cfs
        q = manning_capacity_cfs(1.0, 0.25, 0.01, 0.013)
        assert q > 0

    def test_manning_velocity_fps_imports(self):
        """manning_velocity_fps imports from package."""
        from civil_toolbox.infrastructure_sizing import manning_velocity_fps
        v = manning_velocity_fps(0.25, 0.01, 0.013)
        assert v > 0

    def test_geometry_functions_import(self):
        """Geometry helper functions import."""
        from civil_toolbox.infrastructure_sizing import (
            circular_pipe_full_flow_area_sqft,
            circular_pipe_full_flow_hydraulic_radius_ft,
            box_full_flow_area_sqft,
            box_full_flow_hydraulic_radius_ft,
            rectangular_area_sqft,
            rectangular_hydraulic_radius_ft,
            trapezoidal_area_sqft,
            trapezoidal_hydraulic_radius_ft,
            triangular_area_sqft,
            triangular_hydraulic_radius_ft,
        )
        assert circular_pipe_full_flow_area_sqft(1.0) > 0
        assert box_full_flow_area_sqft(4.0, 3.0) == 12.0


class TestCheckFunctionImports:
    """Tests for capacity check function imports."""

    def test_pipe_functions_import(self):
        """Pipe functions import from package."""
        from civil_toolbox.infrastructure_sizing import (
            estimate_pipe_full_flow_capacity_cfs,
            check_pipe_capacity,
        )
        assert estimate_pipe_full_flow_capacity_cfs is not None
        assert check_pipe_capacity is not None

    def test_culvert_functions_import(self):
        """Culvert functions import from package."""
        from civil_toolbox.infrastructure_sizing import (
            estimate_culvert_barrel_capacity_cfs,
            check_culvert_capacity,
        )
        assert estimate_culvert_barrel_capacity_cfs is not None
        assert check_culvert_capacity is not None

    def test_channel_functions_import(self):
        """Channel functions import from package."""
        from civil_toolbox.infrastructure_sizing import (
            estimate_open_channel_capacity_cfs,
            check_open_channel_capacity,
        )
        assert estimate_open_channel_capacity_cfs is not None
        assert check_open_channel_capacity is not None

    def test_swale_functions_import(self):
        """Swale functions import from package."""
        from civil_toolbox.infrastructure_sizing import (
            estimate_swale_capacity_cfs,
            check_swale_capacity,
        )
        assert estimate_swale_capacity_cfs is not None
        assert check_swale_capacity is not None

    def test_detention_function_imports(self):
        """Detention function imports from package."""
        from civil_toolbox.infrastructure_sizing import check_detention_storage
        assert check_detention_storage is not None


class TestValidationImports:
    """Tests for validation function imports."""

    def test_validation_functions_import(self):
        """Validation functions import from package."""
        from civil_toolbox.infrastructure_sizing import (
            validate_positive_flow,
            validate_positive_storage,
            validate_mannings_n,
            validate_positive_slope,
            validate_positive_dimension,
        )
        assert validate_positive_flow(10.0, "x") == 10.0
        assert validate_positive_storage(1000.0, "x") == 1000.0
        assert validate_mannings_n(0.013, "x") == 0.013
        assert validate_positive_slope(0.01, "x") == 0.01
        assert validate_positive_dimension(18.0, "x") == 18.0


class TestErrorImports:
    """Tests for error class imports."""

    def test_error_classes_import(self):
        """Error classes import from package."""
        from civil_toolbox.infrastructure_sizing import (
            InfrastructureSizingError,
            InvalidSizingInputError,
            CapacityCalculationError,
        )
        assert issubclass(InfrastructureSizingError, Exception)
        assert issubclass(InvalidSizingInputError, ValueError)
        assert issubclass(CapacityCalculationError, InfrastructureSizingError)


class TestExampleImports:
    """Tests for example function imports."""

    def test_example_functions_import(self):
        """Example functions import from package."""
        from civil_toolbox.infrastructure_sizing import (
            create_example_pipe_check,
            create_example_culvert_check,
            create_example_channel_check,
            create_example_swale_check,
            create_example_detention_check,
        )
        assert create_example_pipe_check is not None
        assert create_example_culvert_check is not None


class TestAllExports:
    """Tests for __all__ exports."""

    def test_all_exports_are_importable(self):
        """All items in __all__ are importable."""
        from civil_toolbox import infrastructure_sizing
        for name in infrastructure_sizing.__all__:
            assert hasattr(infrastructure_sizing, name), f"{name} not in module"
