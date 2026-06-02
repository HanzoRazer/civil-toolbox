"""
Contract test: every CalculationResult emitted by an adapter must carry a
complete, non-empty audit trail. Guards the "results are auditable" guardrail
(ENGINEERING_STANDARDS.md) against silent degradation.

Audit trail lives at the ADAPTER -> CalculationResult seam (via ResultBuilder),
NOT in calculator kernels (kernels are pure by design — guardrail #1). Adapters
require domain-entity inputs, so targets are EXERCISED via minimal fixtures,
not introspected.

Units are keyed by input/output NAME and are intentionally absent for
dimensionless quantities (e.g. runoff_coefficient). The unit-coverage check is
therefore scoped to OUTPUTS only — broadening it to inputs would wrongly flag
correct dimensionless handling.
"""
from __future__ import annotations

import pytest

from civil_toolbox.domain.calculation import CalculationResult
from civil_toolbox.domain.drainage import DrainageArea
from civil_toolbox.domain.storm import StormEvent
from civil_toolbox.domain.flow_path import FlowPath, FlowPathSegment
from civil_toolbox.adapters.rational_method import RationalMethodAdapter
from civil_toolbox.adapters.tr55 import TR55Adapter
from civil_toolbox.adapters.time_of_concentration import TimeOfConcentrationAdapter

NON_EMPTY_FIELDS = ("method", "inputs", "outputs", "units", "references")


def _rational_method_result() -> CalculationResult:
    area = DrainageArea(name="A1", area_acres=10.0, runoff_coefficient=0.65)
    storm = StormEvent(name="10yr", rainfall_intensity_in_per_hr=4.5)
    return RationalMethodAdapter.calculate(area, storm)


def _tr55_runoff_depth_result() -> CalculationResult:
    area = DrainageArea(name="A1", area_acres=10.0, curve_number=80)
    storm = StormEvent(name="10yr", rainfall_depth_in=4.5)
    return TR55Adapter.calculate_runoff_depth(area, storm)


def _toc_kirpich_result() -> CalculationResult:
    fp = FlowPath(
        name="FP1",
        segments=[
            FlowPathSegment(segment_type="channel", length_ft=1500.0, slope_ft_per_ft=0.01),
        ],
    )
    return TimeOfConcentrationAdapter.calculate_kirpich(fp)


# (label, factory) — one entry per adapter construction path. Extend this list
# when an adapter is added; do NOT collapse it (a one-adapter test gives false
# coverage). Known gap: this table is hand-maintained, so a newly added adapter
# is silently untested until someone registers a fixture here. To close it, add
# a companion test that walks civil_toolbox/adapters/ and asserts every adapter
# class appears above — it can't build fixtures, but it turns "silently forgot"
# into a CI failure that names the missing adapter.
RESULT_FACTORIES = [
    ("rational_method", _rational_method_result),
    ("tr55_runoff_depth", _tr55_runoff_depth_result),
    ("toc_kirpich", _toc_kirpich_result),
]


def test_factory_table_is_populated():
    assert RESULT_FACTORIES, "No adapter fixtures registered — reconcile coverage."


@pytest.mark.parametrize("label,factory", RESULT_FACTORIES, ids=[f[0] for f in RESULT_FACTORIES])
def test_calculation_result_audit_trail_complete(label, factory):
    result = factory()
    assert isinstance(result, CalculationResult), f"{label}: not a CalculationResult"
    for field_name in NON_EMPTY_FIELDS:
        val = getattr(result, field_name)
        assert val, f"{label}: '{field_name}' is empty — incomplete audit trail"
    assert len(result.references) >= 1, (
        f"{label}: no references — every method must cite >= 1 source"
    )
    for output_name in result.outputs:
        assert output_name in result.units, (
            f"{label}: output '{output_name}' has no unit in the audit record"
        )
