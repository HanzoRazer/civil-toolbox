"""Tests for ParameterSchema / ParameterContext and the Phase A schema set."""

import pytest

from civil_toolbox.design_criteria.parameter_registry import registered_parameter_ids
from civil_toolbox.design_criteria.parameters import (
    PHASE_A_PARAMETERS,
    ParameterContext,
    ParameterSchema,
    get_parameter_schema,
    parameters_required_by,
)


class TestParameterSchema:
    def test_valid_id_accepted(self):
        s = ParameterSchema("project_freeboard_ft", "float", units="ft", required=True)
        assert s.parameter_id == "project_freeboard_ft"

    @pytest.mark.parametrize("bad_id", ["n", "MannignsN", "manning-n", "bfe", "nope_no_prefix"])
    def test_invalid_id_rejected(self, bad_id):
        with pytest.raises(ValueError, match="Invalid parameter_id"):
            ParameterSchema(bad_id, "str")


class TestParameterContext:
    def test_defaults_none(self):
        ctx = ParameterContext()
        assert ctx.project_type is None
        assert ctx.petition_type is None
        assert ctx.drainage_area_ac is None
        assert ctx.metadata == {}

    def test_new_fields_settable(self):
        ctx = ParameterContext(project_type="detention", metadata={"k": 1})
        assert ctx.project_type == "detention"
        assert ctx.metadata == {"k": 1}


class TestEnrichedSchema:
    def test_presentation_fields_present(self):
        s = get_parameter_schema("project_latitude_deg")
        assert s is not None
        assert s.name == "Latitude"
        assert s.help_text
        assert s.valid_range == (-90.0, 90.0)

    def test_value_type_and_required_retained(self):
        s = get_parameter_schema("project_name")
        assert s.value_type == "str"
        assert s.required is True


class TestLookupFunctions:
    def test_get_parameter_schema_known(self):
        assert get_parameter_schema("project_freeboard_ft").parameter_id == "project_freeboard_ft"

    def test_get_parameter_schema_unknown(self):
        assert get_parameter_schema("project_not_a_real_param") is None

    def test_parameters_required_by_hcfcd(self):
        req = parameters_required_by("hcfcd")
        assert "project_freeboard_ft" in req

    def test_parameters_required_by_generic(self):
        req = parameters_required_by("generic")
        assert "project_name" in req
        assert "project_freeboard_ft" not in req

    def test_parameters_required_by_unknown(self):
        assert parameters_required_by("nope") == ()


class TestPhaseAParameters:
    def test_all_schema_ids_valid_and_registered(self):
        registered = registered_parameter_ids()
        for schema in PHASE_A_PARAMETERS:
            assert schema.parameter_id in registered, schema.parameter_id

    def test_required_set(self):
        required = {s.parameter_id for s in PHASE_A_PARAMETERS if s.required}
        assert "project_name" in required
        assert "project_jurisdiction_id" in required
        assert "project_design_storms_years" in required

    def test_one_schema_per_registry_row(self):
        # Code↔registry cardinality: every registered ID has exactly one schema.
        schema_ids = [s.parameter_id for s in PHASE_A_PARAMETERS]
        assert len(schema_ids) == len(set(schema_ids))
        assert set(schema_ids) == set(registered_parameter_ids())
