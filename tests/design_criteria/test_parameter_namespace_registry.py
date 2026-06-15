"""CI validation of the parameter namespace registry (SPEC v0.2.1 §3.8, §11.5).

Validates docs/PARAMETER_NAMESPACE.md and its synchrony with code:

1. Every registered ID matches the regex (§2.4) and a canonical domain prefix (§3).
2. No duplicate IDs in the registry.
3. The registry is non-empty and contains the expected Phase A project IDs.
4. Code→registry: every ParameterSchema defined in code has a registry row.
5. Registry→defaults: every parameter ID used in jurisdiction defaults is registered.

Checks 4-5 activate once the design-criteria contracts exist (DO 004); they skip
cleanly before then so each commit stays green.

Build-failing.
"""

from __future__ import annotations

import pytest

from civil_toolbox.design_criteria.parameter_registry import (
    is_valid_parameter_id,
    load_registry,
    registered_parameter_ids,
)

EXPECTED_PHASE_A_IDS = {
    "project_name",
    "project_jurisdiction_id",
    "project_design_storms_years",
    "project_status",
}


class TestRegistryFile:
    def test_all_ids_valid_format(self):
        bad = [
            e.parameter_id
            for e in load_registry()
            if not is_valid_parameter_id(e.parameter_id)
        ]
        assert not bad, f"Registry IDs failing format/prefix rules: {bad}"

    def test_no_duplicate_ids(self):
        ids = [e.parameter_id for e in load_registry()]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        assert not dupes, f"Duplicate registry IDs: {dupes}"

    def test_registry_non_empty(self):
        assert registered_parameter_ids(), "Parameter registry is empty."

    def test_expected_phase_a_ids_present(self):
        registered = registered_parameter_ids()
        missing = EXPECTED_PHASE_A_IDS - registered
        assert not missing, f"Expected Phase A IDs missing from registry: {missing}"

    def test_header_not_captured(self):
        # The backticked table header cell must not leak in as an entry.
        assert "parameter_id" not in {e.parameter_id for e in load_registry()}


class TestCodeRegistrySynchrony:
    """Code↔registry checks (active once DO 004 contracts exist)."""

    def _schemas(self):
        params = pytest.importorskip(
            "civil_toolbox.design_criteria.parameters"
        )
        if not hasattr(params, "PHASE_A_PARAMETERS"):
            pytest.skip("parameters.PHASE_A_PARAMETERS not defined yet")
        return params.PHASE_A_PARAMETERS

    def test_every_schema_id_is_registered(self):
        schemas = self._schemas()
        registered = registered_parameter_ids()
        unregistered = [
            s.parameter_id for s in schemas if s.parameter_id not in registered
        ]
        assert not unregistered, (
            f"ParameterSchema IDs not in registry: {unregistered}"
        )

    def test_every_jurisdiction_default_id_is_registered(self):
        pytest.importorskip("civil_toolbox.design_criteria.jurisdictions.hcfcd")
        from civil_toolbox.design_criteria.jurisdictions.generic import (
            GenericAuthority,
        )
        from civil_toolbox.design_criteria.jurisdictions.hcfcd import HCFCDAuthority

        registered = registered_parameter_ids()
        for authority in (HCFCDAuthority(), GenericAuthority()):
            for param_id in authority.default_parameter_ids():
                assert param_id in registered, (
                    f"{authority.jurisdiction_id} default '{param_id}' not registered"
                )
