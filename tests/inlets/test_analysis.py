"""Tests for the inlet capacity orchestrator (dispatch by inlet type)."""

import pytest

from civil_toolbox.inlets.analysis import analyze_inlet_capacity
from civil_toolbox.inlets.errors import UnsupportedInletTypeError
from civil_toolbox.inlets.models import InletCapacityResult
from civil_toolbox.infrastructure import Inlet


def test_dispatch_grate():
    inlet = Inlet(id="g", name="g", inlet_type="grate", grate_length_in=24.0, grate_width_in=24.0)
    r = analyze_inlet_capacity(inlet, design_flow_cfs=8.0, head_ft=0.5)
    assert isinstance(r, InletCapacityResult)
    assert r.inlet_type == "grate"
    assert r.status == "pass"


def test_dispatch_curb():
    inlet = Inlet(id="c", name="c", inlet_type="curb_opening", opening_length_ft=5.0)
    r = analyze_inlet_capacity(inlet, design_flow_cfs=4.0, head_ft=0.5)
    assert r.inlet_type == "curb_opening"
    assert r.capacity_cfs == pytest.approx(5.3033, abs=1e-3)


def test_dispatch_combination():
    inlet = Inlet(id="co", name="co", inlet_type="combination",
                  grate_length_in=24.0, grate_width_in=24.0, opening_length_ft=5.0)
    r = analyze_inlet_capacity(inlet, design_flow_cfs=15.0, head_ft=0.5)
    assert r.capacity_cfs == pytest.approx(18.9221, abs=1e-3)


def test_dispatch_slotted():
    inlet = Inlet(id="s", name="s", inlet_type="slotted", opening_length_ft=10.0)
    r = analyze_inlet_capacity(inlet, design_flow_cfs=5.0, head_ft=0.4)
    assert r.capacity_cfs == pytest.approx(7.5895, abs=1e-3)


def test_unsupported_type_raises():
    inlet = Inlet(id="g", name="g", inlet_type="grate", grate_length_in=24.0, grate_width_in=24.0)
    inlet.inlet_type = "mystery"  # bypass domain validation post-construction
    with pytest.raises(UnsupportedInletTypeError, match="Unsupported inlet_type"):
        analyze_inlet_capacity(inlet, design_flow_cfs=8.0, head_ft=0.5)


def test_roundtrip_from_orchestrator():
    inlet = Inlet(id="g", name="g", inlet_type="grate", grate_length_in=24.0, grate_width_in=24.0)
    r = analyze_inlet_capacity(inlet, design_flow_cfs=8.0, head_ft=0.5)
    assert InletCapacityResult.from_dict(r.to_dict()).to_dict() == r.to_dict()
