"""Tests for infrastructure sizing example functions."""

import pytest

from civil_toolbox.infrastructure_sizing import (
    create_example_pipe_check,
    create_example_culvert_check,
    create_example_channel_check,
    create_example_swale_check,
    create_example_detention_check,
    InfrastructureCheckResult,
)


class TestExampleCreators:
    """Tests for example creation functions."""

    def test_create_example_pipe_check(self):
        """create_example_pipe_check returns valid result."""
        result = create_example_pipe_check()
        assert isinstance(result, InfrastructureCheckResult)
        assert result.element_type == "pipe"
        assert result.capacity_cfs is not None
        assert result.capacity_cfs > 0
        assert result.design_flow_cfs == 10.0

    def test_create_example_culvert_check(self):
        """create_example_culvert_check returns valid result."""
        result = create_example_culvert_check()
        assert isinstance(result, InfrastructureCheckResult)
        assert result.element_type == "culvert"
        assert result.capacity_cfs is not None
        assert result.capacity_cfs > 0
        assert result.design_flow_cfs == 100.0

    def test_create_example_channel_check(self):
        """create_example_channel_check returns valid result."""
        result = create_example_channel_check()
        assert isinstance(result, InfrastructureCheckResult)
        assert result.element_type == "channel"
        assert result.capacity_cfs is not None
        assert result.capacity_cfs > 0
        assert result.design_flow_cfs == 50.0

    def test_create_example_swale_check(self):
        """create_example_swale_check returns valid result."""
        result = create_example_swale_check()
        assert isinstance(result, InfrastructureCheckResult)
        assert result.element_type == "swale"
        assert result.capacity_cfs is not None
        assert result.capacity_cfs > 0
        assert result.design_flow_cfs == 5.0

    def test_create_example_detention_check(self):
        """create_example_detention_check returns valid result."""
        result = create_example_detention_check()
        assert isinstance(result, InfrastructureCheckResult)
        assert result.element_type == "detention"
        assert result.storage_cuft is not None
        assert result.storage_cuft > 0
        assert result.required_storage_cuft == 80000.0


class TestExampleResultsAreValid:
    """Tests that example results are properly constructed."""

    def test_pipe_result_has_method(self):
        """Pipe result has method field."""
        result = create_example_pipe_check()
        assert result.method != ""
        assert "Manning" in result.method

    def test_culvert_result_has_warnings(self):
        """Culvert result has barrel-only warning."""
        result = create_example_culvert_check()
        warning_codes = [w.warning_code for w in result.warnings]
        assert "BARREL_CAPACITY_ONLY" in warning_codes

    def test_channel_result_has_assumptions(self):
        """Channel result has assumptions."""
        result = create_example_channel_check()
        assert len(result.assumptions) > 0

    def test_detention_result_has_routing_warning(self):
        """Detention result has routing-required warning."""
        result = create_example_detention_check()
        warning_codes = [w.warning_code for w in result.warnings]
        assert "ROUTING_REQUIRED" in warning_codes

    def test_all_examples_have_utilization(self):
        """All examples with design flow have utilization ratio."""
        results = [
            create_example_pipe_check(),
            create_example_culvert_check(),
            create_example_channel_check(),
            create_example_swale_check(),
            create_example_detention_check(),
        ]
        for result in results:
            assert result.utilization_ratio is not None
