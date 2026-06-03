"""Synthetic culvert examples for testing and demonstration.

These return ``Culvert`` domain objects ready to pass to
:func:`civil_toolbox.culverts.analysis.analyze_culvert`.

Note on multi-barrel: barrel interaction is out of scope for this foundation.
The multi-barrel example carries a ``barrel_count`` in metadata and represents a
single representative barrel; callers analyze one barrel with the per-barrel
flow.
"""

from __future__ import annotations

from civil_toolbox.infrastructure import Culvert


def create_single_circular_culvert() -> Culvert:
    """A 36-inch circular culvert, projecting inlet, on a mild slope."""
    return Culvert(
        id="culvert_circular_001",
        name="Single Circular Culvert",
        shape="circular",
        diameter_in=36.0,
        length_ft=100.0,
        slope_ft_per_ft=0.01,
        mannings_n=0.024,
        material="corrugated_metal",
        inlet_type="projecting",
        upstream_invert_ft=101.0,
        downstream_invert_ft=100.0,
        embankment_height_ft=8.0,
        allowable_headwater_ft=6.0,
    )


def create_box_culvert() -> Culvert:
    """A 4 ft x 3 ft concrete box culvert with a headwall inlet."""
    return Culvert(
        id="culvert_box_001",
        name="Box Culvert",
        shape="box",
        width_in=48.0,
        height_in=36.0,
        length_ft=80.0,
        slope_ft_per_ft=0.005,
        mannings_n=0.013,
        material="concrete",
        inlet_type="headwall",
        upstream_invert_ft=96.5,
        downstream_invert_ft=96.1,
        embankment_height_ft=7.0,
        allowable_headwater_ft=5.0,
    )


def create_multi_barrel_culvert() -> Culvert:
    """A representative barrel of a 2-barrel box culvert.

    Barrel interaction is out of scope; ``metadata['barrel_count']`` records the
    intended count. Analyze one barrel with the per-barrel design flow.
    """
    return Culvert(
        id="culvert_multibarrel_001",
        name="Multi-Barrel Box Culvert (representative barrel)",
        shape="box",
        width_in=60.0,
        height_in=48.0,
        length_ft=120.0,
        slope_ft_per_ft=0.008,
        mannings_n=0.013,
        material="concrete",
        inlet_type="wingwall",
        upstream_invert_ft=98.96,
        downstream_invert_ft=98.0,
        embankment_height_ft=10.0,
        allowable_headwater_ft=8.0,
        metadata={
            "barrel_count": 2,
            "note": "Single representative barrel; split total flow per barrel.",
        },
    )
