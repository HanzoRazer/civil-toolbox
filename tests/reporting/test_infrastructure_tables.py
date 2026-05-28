"""Tests for infrastructure table builders."""

import pytest

from civil_toolbox.infrastructure import (
    InfrastructureNetwork,
    InfrastructureNode,
    Pipe,
    Inlet,
    DetentionFacility,
    StageStoragePoint,
)
from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult
from civil_toolbox.reporting.infrastructure_tables import (
    build_infrastructure_summary_table,
    build_pipe_schedule_table,
    build_inlet_schedule_table,
    build_detention_schedule_table,
    build_infrastructure_check_summary_table,
)


class TestBuildInfrastructureSummaryTable:
    """Tests for build_infrastructure_summary_table."""

    @pytest.fixture
    def empty_network(self):
        """Create an empty network."""
        return InfrastructureNetwork(id="net1", name="Empty Network")

    @pytest.fixture
    def sample_network(self):
        """Create a sample network with multiple element types."""
        network = InfrastructureNetwork(id="net1", name="Sample Network")

        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_node(InfrastructureNode(id="n2", name="N-2"))

        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=200.0,
            slope_ft_per_ft=0.01,
            upstream_node_id="n1", downstream_node_id="n2",
            metadata={"status": "existing"},
        ))
        network.add_element(Pipe(
            id="p2", name="P-2",
            diameter_in=24.0, length_ft=150.0,
            slope_ft_per_ft=0.005,
            metadata={"status": "proposed"},
        ))
        network.add_element(Inlet(
            id="i1", name="I-1",
            inlet_type="grate",
            node_id="n1",
        ))

        return network

    def test_empty_network_returns_table_with_nodes_only(self, empty_network):
        """Empty network returns table with headers only."""
        table = build_infrastructure_summary_table(empty_network)
        assert table is not None
        assert len(table.headers) == 6
        assert table.headers[0] == "Element Type"

    def test_has_correct_headers(self, sample_network):
        """Table has correct headers."""
        table = build_infrastructure_summary_table(sample_network)
        expected_headers = [
            "Element Type", "Count", "Existing", "Proposed", "Future", "Other"
        ]
        assert table.headers == expected_headers

    def test_counts_elements_correctly(self, sample_network):
        """Table counts elements correctly."""
        table = build_infrastructure_summary_table(sample_network)
        assert len(table.rows) >= 2

        pipe_row = next(r for r in table.rows if r[0] == "Pipes")
        assert pipe_row[1] == "2"

        inlet_row = next(r for r in table.rows if r[0] == "Inlets")
        assert inlet_row[1] == "1"

    def test_counts_status_correctly(self, sample_network):
        """Table breaks down status correctly."""
        table = build_infrastructure_summary_table(sample_network)

        pipe_row = next(r for r in table.rows if r[0] == "Pipes")
        assert pipe_row[2] == "1"
        assert pipe_row[3] == "1"

    def test_has_title(self, sample_network):
        """Table has title."""
        table = build_infrastructure_summary_table(sample_network)
        assert table.title == "Infrastructure Summary"


class TestBuildPipeScheduleTable:
    """Tests for build_pipe_schedule_table."""

    @pytest.fixture
    def network_with_pipes(self):
        """Create a network with pipes."""
        network = InfrastructureNetwork(id="net1", name="Test Network")

        network.add_node(InfrastructureNode(id="n1", name="N-1"))
        network.add_node(InfrastructureNode(id="n2", name="N-2"))

        network.add_element(Pipe(
            id="p1", name="P-1",
            diameter_in=18.0, length_ft=200.0,
            slope_ft_per_ft=0.01,
            mannings_n=0.013,
            material="RCP",
            upstream_node_id="n1",
            downstream_node_id="n2",
            metadata={"status": "existing"},
        ))
        network.add_element(Pipe(
            id="p2", name="P-2",
            shape="box",
            width_in=48.0, height_in=36.0,
            length_ft=150.0,
            slope_ft_per_ft=0.005,
        ))

        return network

    def test_has_correct_headers(self, network_with_pipes):
        """Table has correct headers."""
        table = build_pipe_schedule_table(network_with_pipes)
        expected_headers = [
            "ID", "Name", "Status", "Upstream Node", "Downstream Node",
            "Length (ft)", "Diameter (in)", "Material", "Slope (ft/ft)"
        ]
        assert table.headers == expected_headers

    def test_includes_all_pipes(self, network_with_pipes):
        """Table includes all pipes."""
        table = build_pipe_schedule_table(network_with_pipes)
        assert len(table.rows) == 2

    def test_circular_pipe_shows_diameter(self, network_with_pipes):
        """Circular pipe shows diameter."""
        table = build_pipe_schedule_table(network_with_pipes)
        p1_row = next(r for r in table.rows if r[0] == "p1")
        assert "18" in p1_row[6]

    def test_box_pipe_shows_dimensions(self, network_with_pipes):
        """Box pipe shows width x height."""
        table = build_pipe_schedule_table(network_with_pipes)
        p2_row = next(r for r in table.rows if r[0] == "p2")
        assert "48" in p2_row[6]
        assert "36" in p2_row[6]

    def test_missing_values_show_dash(self, network_with_pipes):
        """Missing values show dash."""
        table = build_pipe_schedule_table(network_with_pipes)
        p2_row = next(r for r in table.rows if r[0] == "p2")
        assert p2_row[3] == "—"

    def test_has_title(self, network_with_pipes):
        """Table has title."""
        table = build_pipe_schedule_table(network_with_pipes)
        assert table.title == "Pipe Schedule"


class TestBuildInletScheduleTable:
    """Tests for build_inlet_schedule_table."""

    @pytest.fixture
    def network_with_inlets(self):
        """Create a network with inlets."""
        network = InfrastructureNetwork(id="net1", name="Test Network")

        network.add_node(InfrastructureNode(id="n1", name="N-1"))

        network.add_element(Inlet(
            id="i1", name="I-1",
            inlet_type="grate",
            node_id="n1",
            metadata={
                "status": "proposed",
                "connected_drainage_areas": ["DA-1", "DA-2"],
            },
        ))
        network.add_element(Inlet(
            id="i2", name="I-2",
            inlet_type="curb_opening",
        ))

        return network

    def test_has_correct_headers(self, network_with_inlets):
        """Table has correct headers."""
        table = build_inlet_schedule_table(network_with_inlets)
        expected_headers = [
            "ID", "Name", "Status", "Node", "Type", "Connected Drainage Areas"
        ]
        assert table.headers == expected_headers

    def test_includes_all_inlets(self, network_with_inlets):
        """Table includes all inlets."""
        table = build_inlet_schedule_table(network_with_inlets)
        assert len(table.rows) == 2

    def test_shows_inlet_type(self, network_with_inlets):
        """Table shows inlet type."""
        table = build_inlet_schedule_table(network_with_inlets)
        i1_row = next(r for r in table.rows if r[0] == "i1")
        assert i1_row[4] == "grate"

    def test_shows_connected_areas(self, network_with_inlets):
        """Table shows connected drainage areas."""
        table = build_inlet_schedule_table(network_with_inlets)
        i1_row = next(r for r in table.rows if r[0] == "i1")
        assert "DA-1" in i1_row[5]
        assert "DA-2" in i1_row[5]


class TestBuildDetentionScheduleTable:
    """Tests for build_detention_schedule_table."""

    @pytest.fixture
    def network_with_detention(self):
        """Create a network with detention facilities."""
        network = InfrastructureNetwork(id="net1", name="Test Network")

        network.add_node(InfrastructureNode(id="n1", name="Outlet"))

        network.add_element(DetentionFacility(
            id="d1", name="DP-1",
            facility_type="detention",
            stage_storage=[
                StageStoragePoint(stage_ft=0.0, storage_cuft=0),
                StageStoragePoint(stage_ft=5.0, storage_cuft=50000),
            ],
            outlet_node_id="n1",
            metadata={"status": "proposed"},
        ))
        network.add_element(DetentionFacility(
            id="d2", name="DP-2",
            facility_type="retention",
        ))

        return network

    def test_has_correct_headers(self, network_with_detention):
        """Table has correct headers."""
        table = build_detention_schedule_table(network_with_detention)
        expected_headers = [
            "ID", "Name", "Status", "Type", "Storage Volume (cu ft)", "Outlet Structure"
        ]
        assert table.headers == expected_headers

    def test_includes_all_detention(self, network_with_detention):
        """Table includes all detention facilities."""
        table = build_detention_schedule_table(network_with_detention)
        assert len(table.rows) == 2

    def test_shows_storage_volume(self, network_with_detention):
        """Table shows storage volume."""
        table = build_detention_schedule_table(network_with_detention)
        d1_row = next(r for r in table.rows if r[0] == "d1")
        assert "50,000" in d1_row[4] or "50000" in d1_row[4]

    def test_shows_facility_type(self, network_with_detention):
        """Table shows facility type."""
        table = build_detention_schedule_table(network_with_detention)
        d2_row = next(r for r in table.rows if r[0] == "d2")
        assert d2_row[3] == "retention"


class TestBuildInfrastructureCheckSummaryTable:
    """Tests for build_infrastructure_check_summary_table."""

    @pytest.fixture
    def sample_check_results(self):
        """Create sample check results."""
        results = []

        result1 = InfrastructureCheckResult(
            element_id="p1",
            element_name="P-1",
            element_type="pipe",
            passes=True,
            capacity_cfs=15.5,
            design_flow_cfs=10.0,
            velocity_fps=5.2,
            method="Manning's equation (full flow)",
        )
        results.append(result1)

        result2 = InfrastructureCheckResult(
            element_id="p2",
            element_name="P-2",
            element_type="pipe",
            passes=False,
            capacity_cfs=8.0,
            design_flow_cfs=12.0,
            velocity_fps=6.5,
            method="Manning's equation (full flow)",
        )
        result2.add_warning("OVERCAPACITY", "Design flow exceeds capacity")
        results.append(result2)

        result3 = InfrastructureCheckResult(
            element_id="d1",
            element_name="DP-1",
            element_type="detention",
            passes=True,
            storage_cuft=50000,
            required_storage_cuft=40000,
            method="Volume comparison",
        )
        results.append(result3)

        return results

    def test_has_correct_headers(self, sample_check_results):
        """Table has correct headers."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        expected_headers = [
            "Entity ID", "Entity Type", "Check Type", "Status",
            "Capacity / Provided", "Demand / Required", "Margin", "Warnings"
        ]
        assert table.headers == expected_headers

    def test_includes_all_results(self, sample_check_results):
        """Table includes all results."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        assert len(table.rows) == 3

    def test_shows_pass_fail_status(self, sample_check_results):
        """Table shows PASS/FAIL status."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        statuses = [r[3] for r in table.rows]
        assert "PASS" in statuses
        assert "FAIL" in statuses

    def test_shows_capacity_for_flow_checks(self, sample_check_results):
        """Table shows capacity for flow-based checks."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        p1_row = next(r for r in table.rows if r[0] == "p1")
        assert "cfs" in p1_row[4]

    def test_shows_storage_for_detention_checks(self, sample_check_results):
        """Table shows storage for detention checks."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        d1_row = next(r for r in table.rows if r[0] == "d1")
        assert "cu ft" in d1_row[4]

    def test_shows_warning_count(self, sample_check_results):
        """Table shows warning count."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        p2_row = next(r for r in table.rows if r[0] == "p2")
        assert p2_row[7] == "1"

    def test_empty_results_returns_empty_table(self):
        """Empty results returns table with headers only."""
        table = build_infrastructure_check_summary_table([])
        assert len(table.rows) == 0
        assert len(table.headers) == 8

    def test_has_title(self, sample_check_results):
        """Table has title."""
        table = build_infrastructure_check_summary_table(sample_check_results)
        assert table.title == "Infrastructure Sizing Check Summary"
