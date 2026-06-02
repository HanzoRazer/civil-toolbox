"""Tests for hydraulic input builders."""

import pytest

from civil_toolbox.domain.infrastructure import InfrastructureElement
from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError
from civil_toolbox.hydraulics.builders import (
    build_pipe_reach_from_infrastructure,
    build_pipe_reaches_from_infrastructure,
)


def make_pipe_element(**kwargs) -> InfrastructureElement:
    """Create a pipe infrastructure element with defaults."""
    defaults = {
        "name": "Test Pipe",
        "element_type": "pipe",
        "length_ft": 200.0,
        "diameter_in": 18.0,
        "mannings_n": 0.013,
    }
    defaults.update(kwargs)
    return InfrastructureElement(**defaults)


class TestBuildPipeReachFromInfrastructure:
    """Tests for build_pipe_reach_from_infrastructure."""

    def test_basic_conversion(self):
        """Converts pipe element to reach input."""
        element = make_pipe_element()
        reach = build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

        assert reach.pipe_id == element.id
        assert reach.name == "Test Pipe"
        assert reach.design_flow_cfs == 10.0
        assert reach.length_ft == 200.0
        assert reach.diameter_in == 18.0
        assert reach.roughness_n == 0.013

    def test_culvert_allowed(self):
        """Culvert element type is allowed."""
        element = make_pipe_element(element_type="culvert")
        reach = build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

        assert reach.pipe_id == element.id

    def test_channel_rejected(self):
        """Channel element type is rejected."""
        element = InfrastructureElement(
            name="Test Channel",
            element_type="channel",
            length_ft=200.0,
            bottom_width_ft=10.0,
            depth_ft=3.0,
            mannings_n=0.035,
        )
        with pytest.raises(InvalidHydraulicInputError, match="must be 'pipe' or 'culvert'"):
            build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

    def test_missing_length_raises(self):
        """Missing length raises error."""
        element = InfrastructureElement(
            name="Test Pipe",
            element_type="pipe",
            diameter_in=18.0,
            mannings_n=0.013,
        )
        with pytest.raises(InvalidHydraulicInputError, match="length_ft is required"):
            build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

    def test_missing_mannings_n_raises(self):
        """Missing Manning's n raises error."""
        element = InfrastructureElement(
            name="Test Pipe",
            element_type="pipe",
            length_ft=200.0,
            diameter_in=18.0,
        )
        with pytest.raises(InvalidHydraulicInputError, match="mannings_n is required"):
            build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

    def test_missing_diameter_raises(self):
        """Missing diameter raises error."""
        element = InfrastructureElement(
            name="Test Pipe",
            element_type="pipe",
            length_ft=200.0,
            mannings_n=0.013,
        )
        with pytest.raises(InvalidHydraulicInputError, match="diameter_in is required"):
            build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

    def test_elevations_passed_through(self):
        """Elevation data is passed through."""
        element = make_pipe_element()
        reach = build_pipe_reach_from_infrastructure(
            element,
            design_flow_cfs=10.0,
            upstream_invert_elevation_ft=99.0,
            downstream_invert_elevation_ft=98.0,
            upstream_rim_elevation_ft=105.0,
            downstream_rim_elevation_ft=104.0,
        )

        assert reach.upstream_invert_elevation_ft == 99.0
        assert reach.downstream_invert_elevation_ft == 98.0
        assert reach.upstream_rim_elevation_ft == 105.0
        assert reach.downstream_rim_elevation_ft == 104.0

    def test_custom_reach_id(self):
        """Custom reach ID can be provided."""
        element = make_pipe_element()
        reach = build_pipe_reach_from_infrastructure(
            element,
            design_flow_cfs=10.0,
            reach_id="custom_reach_001",
        )

        assert reach.id == "custom_reach_001"
        assert reach.pipe_id == element.id

    def test_slope_included_when_available(self):
        """Slope is included when element has it."""
        element = make_pipe_element(slope_ft_per_ft=0.005)
        reach = build_pipe_reach_from_infrastructure(element, design_flow_cfs=10.0)

        assert reach.slope_ft_per_ft == 0.005


class TestBuildPipeReachesFromInfrastructure:
    """Tests for build_pipe_reaches_from_infrastructure."""

    def test_single_flow_applied_to_all(self):
        """Single flow value applied to all elements."""
        elements = [
            make_pipe_element(name="Pipe 1"),
            make_pipe_element(name="Pipe 2"),
            make_pipe_element(name="Pipe 3"),
        ]
        reaches = build_pipe_reaches_from_infrastructure(elements, design_flows_cfs=10.0)

        assert len(reaches) == 3
        assert all(r.design_flow_cfs == 10.0 for r in reaches)

    def test_individual_flows(self):
        """Individual flows assigned to each element."""
        elements = [
            make_pipe_element(name="Pipe 1"),
            make_pipe_element(name="Pipe 2"),
            make_pipe_element(name="Pipe 3"),
        ]
        flows = [5.0, 10.0, 15.0]
        reaches = build_pipe_reaches_from_infrastructure(elements, design_flows_cfs=flows)

        assert len(reaches) == 3
        assert reaches[0].design_flow_cfs == 5.0
        assert reaches[1].design_flow_cfs == 10.0
        assert reaches[2].design_flow_cfs == 15.0

    def test_flow_list_length_mismatch_raises(self):
        """Mismatched flow list length raises error."""
        elements = [
            make_pipe_element(name="Pipe 1"),
            make_pipe_element(name="Pipe 2"),
        ]
        flows = [5.0, 10.0, 15.0]
        with pytest.raises(InvalidHydraulicInputError, match="length.*must match"):
            build_pipe_reaches_from_infrastructure(elements, design_flows_cfs=flows)

    def test_empty_elements_returns_empty(self):
        """Empty elements list returns empty reaches list."""
        reaches = build_pipe_reaches_from_infrastructure([], design_flows_cfs=10.0)
        assert reaches == []

    def test_order_preserved(self):
        """Element order is preserved in reaches."""
        elements = [
            make_pipe_element(name="Downstream"),
            make_pipe_element(name="Middle"),
            make_pipe_element(name="Upstream"),
        ]
        reaches = build_pipe_reaches_from_infrastructure(elements, design_flows_cfs=10.0)

        assert reaches[0].name == "Downstream"
        assert reaches[1].name == "Middle"
        assert reaches[2].name == "Upstream"
