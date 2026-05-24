"""Tests for infrastructure public exports."""


class TestBaseImports:
    """Tests for base class imports."""

    def test_element_type_imports(self):
        """ElementType imports from package."""
        from civil_toolbox.infrastructure import ElementType
        assert ElementType.PIPE.value == "pipe"

    def test_infrastructure_element_base_imports(self):
        """InfrastructureElementBase imports from package."""
        from civil_toolbox.infrastructure import InfrastructureElementBase
        assert InfrastructureElementBase is not None

    def test_infrastructure_check_result_imports(self):
        """InfrastructureCheckResult imports from package."""
        from civil_toolbox.infrastructure import InfrastructureCheckResult
        result = InfrastructureCheckResult(is_valid=True)
        assert result.is_valid is True

    def test_infrastructure_validation_warning_imports(self):
        """InfrastructureValidationWarning imports from package."""
        from civil_toolbox.infrastructure import InfrastructureValidationWarning
        warning = InfrastructureValidationWarning(
            element_id="e1",
            element_name="E-1",
            warning_code="TEST",
            message="Test warning",
        )
        assert warning.warning_code == "TEST"


class TestElementImports:
    """Tests for element class imports."""

    def test_infrastructure_node_imports(self):
        """InfrastructureNode imports from package."""
        from civil_toolbox.infrastructure import InfrastructureNode
        node = InfrastructureNode(id="n1", name="N-1")
        assert node.id == "n1"

    def test_pipe_imports(self):
        """Pipe imports from package."""
        from civil_toolbox.infrastructure import Pipe
        pipe = Pipe(id="p1", name="P-1", diameter_in=18.0, length_ft=100.0)
        assert pipe.diameter_in == 18.0

    def test_inlet_imports(self):
        """Inlet imports from package."""
        from civil_toolbox.infrastructure import Inlet
        inlet = Inlet(id="i1", name="I-1")
        assert inlet.inlet_type == "grate"

    def test_culvert_imports(self):
        """Culvert imports from package."""
        from civil_toolbox.infrastructure import Culvert
        culvert = Culvert(id="c1", name="C-1", diameter_in=24.0, length_ft=50.0)
        assert culvert.diameter_in == 24.0

    def test_open_channel_imports(self):
        """OpenChannel imports from package."""
        from civil_toolbox.infrastructure import OpenChannel
        channel = OpenChannel(
            id="ch1", name="CH-1",
            shape="rectangular",
            bottom_width_ft=6.0, depth_ft=3.0, length_ft=100.0,
        )
        assert channel.shape == "rectangular"

    def test_detention_facility_imports(self):
        """DetentionFacility imports from package."""
        from civil_toolbox.infrastructure import DetentionFacility
        facility = DetentionFacility(id="d1", name="DP-1")
        assert facility.facility_type == "detention"

    def test_stage_storage_point_imports(self):
        """StageStoragePoint imports from package."""
        from civil_toolbox.infrastructure import StageStoragePoint
        point = StageStoragePoint(stage_ft=90.0, storage_cuft=0)
        assert point.stage_ft == 90.0

    def test_outlet_structure_imports(self):
        """OutletStructure imports from package."""
        from civil_toolbox.infrastructure import OutletStructure
        outlet = OutletStructure(id="o1", name="OS-1")
        assert outlet.outlet_type == "orifice"

    def test_swale_imports(self):
        """Swale imports from package."""
        from civil_toolbox.infrastructure import Swale
        swale = Swale(id="s1", name="SW-1", depth_ft=1.0, length_ft=100.0)
        assert swale.swale_type == "grass"


class TestNetworkImports:
    """Tests for network class imports."""

    def test_infrastructure_network_imports(self):
        """InfrastructureNetwork imports from package."""
        from civil_toolbox.infrastructure import InfrastructureNetwork
        network = InfrastructureNetwork(id="net1", name="Test Network")
        assert network.id == "net1"

    def test_network_element_imports(self):
        """NetworkElement type imports from package."""
        from civil_toolbox.infrastructure import NetworkElement
        assert NetworkElement is not None


class TestScheduleImports:
    """Tests for schedule class imports."""

    def test_infrastructure_schedule_imports(self):
        """InfrastructureSchedule imports from package."""
        from civil_toolbox.infrastructure import InfrastructureSchedule
        schedule = InfrastructureSchedule(name="Test", schedule_type="pipe")
        assert schedule.name == "Test"

    def test_infrastructure_schedule_row_imports(self):
        """InfrastructureScheduleRow imports from package."""
        from civil_toolbox.infrastructure import InfrastructureScheduleRow
        row = InfrastructureScheduleRow(
            element_id="p1", element_name="P-1", element_type="pipe"
        )
        assert row.element_id == "p1"


class TestErrorImports:
    """Tests for error class imports."""

    def test_infrastructure_error_imports(self):
        """InfrastructureError imports from package."""
        from civil_toolbox.infrastructure import InfrastructureError
        assert issubclass(InfrastructureError, Exception)

    def test_invalid_infrastructure_error_imports(self):
        """InvalidInfrastructureError imports from package."""
        from civil_toolbox.infrastructure import InvalidInfrastructureError
        assert issubclass(InvalidInfrastructureError, ValueError)

    def test_infrastructure_validation_error_imports(self):
        """InfrastructureValidationError imports from package."""
        from civil_toolbox.infrastructure import InfrastructureValidationError
        assert issubclass(InfrastructureValidationError, Exception)

    def test_node_not_found_error_imports(self):
        """NodeNotFoundError imports from package."""
        from civil_toolbox.infrastructure import NodeNotFoundError
        assert issubclass(NodeNotFoundError, KeyError)

    def test_element_not_found_error_imports(self):
        """ElementNotFoundError imports from package."""
        from civil_toolbox.infrastructure import ElementNotFoundError
        assert issubclass(ElementNotFoundError, KeyError)

    def test_network_validation_error_imports(self):
        """NetworkValidationError imports from package."""
        from civil_toolbox.infrastructure import NetworkValidationError
        assert issubclass(NetworkValidationError, Exception)


class TestValidationImports:
    """Tests for validation function imports."""

    def test_validate_positive_imports(self):
        """validate_positive imports from package."""
        from civil_toolbox.infrastructure import validate_positive
        assert validate_positive(1.0, "x") == 1.0

    def test_validate_non_negative_imports(self):
        """validate_non_negative imports from package."""
        from civil_toolbox.infrastructure import validate_non_negative
        assert validate_non_negative(0.0, "x") == 0.0

    def test_validate_mannings_n_imports(self):
        """validate_mannings_n imports from package."""
        from civil_toolbox.infrastructure import validate_mannings_n
        assert validate_mannings_n(0.013, "n") == 0.013

    def test_validate_slope_imports(self):
        """validate_slope imports from package."""
        from civil_toolbox.infrastructure import validate_slope
        assert validate_slope(0.01, "s") == 0.01

    def test_validate_pipe_shape_imports(self):
        """validate_pipe_shape imports from package."""
        from civil_toolbox.infrastructure import validate_pipe_shape
        assert validate_pipe_shape("circular") == "circular"

    def test_validate_inlet_type_imports(self):
        """validate_inlet_type imports from package."""
        from civil_toolbox.infrastructure import validate_inlet_type
        assert validate_inlet_type("grate") == "grate"

    def test_validate_channel_shape_imports(self):
        """validate_channel_shape imports from package."""
        from civil_toolbox.infrastructure import validate_channel_shape
        assert validate_channel_shape("trapezoidal") == "trapezoidal"

    def test_validate_outlet_type_imports(self):
        """validate_outlet_type imports from package."""
        from civil_toolbox.infrastructure import validate_outlet_type
        assert validate_outlet_type("orifice") == "orifice"


class TestExampleImports:
    """Tests for example function imports."""

    def test_create_example_node_imports(self):
        """create_example_node imports from package."""
        from civil_toolbox.infrastructure import create_example_node
        node = create_example_node()
        assert node is not None

    def test_create_example_pipe_imports(self):
        """create_example_pipe imports from package."""
        from civil_toolbox.infrastructure import create_example_pipe
        pipe = create_example_pipe()
        assert pipe is not None

    def test_create_example_network_imports(self):
        """create_example_network imports from package."""
        from civil_toolbox.infrastructure import create_example_network
        network = create_example_network()
        assert network is not None


class TestAllExports:
    """Tests for __all__ exports."""

    def test_all_exports_are_importable(self):
        """All items in __all__ are importable."""
        from civil_toolbox import infrastructure
        for name in infrastructure.__all__:
            assert hasattr(infrastructure, name), f"{name} not in module"
