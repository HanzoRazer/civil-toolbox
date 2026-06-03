"""Tests for synthetic culvert examples."""

import pytest

from civil_toolbox.culverts.analysis import analyze_culvert
from civil_toolbox.culverts.examples import (
    create_box_culvert,
    create_multi_barrel_culvert,
    create_single_circular_culvert,
)
from civil_toolbox.infrastructure import Culvert


@pytest.mark.parametrize(
    "factory",
    [create_single_circular_culvert, create_box_culvert, create_multi_barrel_culvert],
)
def test_example_returns_culvert(factory):
    assert isinstance(factory(), Culvert)


@pytest.mark.parametrize(
    "factory",
    [create_single_circular_culvert, create_box_culvert, create_multi_barrel_culvert],
)
def test_example_is_analyzable(factory):
    result = analyze_culvert(factory(), design_flow_cfs=40.0)
    assert result.headwater_depth_ft is not None
    assert result.governing_control in ("inlet", "outlet")


def test_circular_shape():
    assert create_single_circular_culvert().shape == "circular"


def test_box_shape():
    assert create_box_culvert().shape == "box"


def test_multi_barrel_metadata():
    c = create_multi_barrel_culvert()
    assert c.metadata.get("barrel_count") == 2
