"""Builders for constructing hydraulic inputs from domain models."""

from __future__ import annotations

from civil_toolbox.domain.infrastructure import InfrastructureElement
from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError
from civil_toolbox.hydraulics.models import PipeReachInput


def build_pipe_reach_from_infrastructure(
    element: InfrastructureElement,
    design_flow_cfs: float,
    upstream_invert_elevation_ft: float | None = None,
    downstream_invert_elevation_ft: float | None = None,
    upstream_rim_elevation_ft: float | None = None,
    downstream_rim_elevation_ft: float | None = None,
    reach_id: str | None = None,
) -> PipeReachInput:
    """Build a PipeReachInput from an InfrastructureElement.

    Extracts geometry and roughness from the infrastructure element
    and combines with provided flow and elevation data.

    Args:
        element: InfrastructureElement (must be pipe or culvert type).
        design_flow_cfs: Design flow rate in cfs.
        upstream_invert_elevation_ft: Upstream invert elevation.
        downstream_invert_elevation_ft: Downstream invert elevation.
        upstream_rim_elevation_ft: Upstream rim/ground elevation.
        downstream_rim_elevation_ft: Downstream rim/ground elevation.
        reach_id: Optional custom reach ID (defaults to element.id).

    Returns:
        PipeReachInput ready for hydraulic calculation.

    Raises:
        InvalidHydraulicInputError: If element type is unsupported or
            required attributes are missing.
    """
    if element.element_type not in ("pipe", "culvert"):
        raise InvalidHydraulicInputError(
            f"element_type must be 'pipe' or 'culvert', got '{element.element_type}'"
        )

    if element.length_ft is None:
        raise InvalidHydraulicInputError(
            f"length_ft is required for hydraulic analysis on '{element.name}'"
        )

    if element.mannings_n is None:
        raise InvalidHydraulicInputError(
            f"mannings_n is required for hydraulic analysis on '{element.name}'"
        )

    if element.diameter_in is None:
        raise InvalidHydraulicInputError(
            f"diameter_in is required for hydraulic analysis on '{element.name}'"
        )

    return PipeReachInput(
        id=reach_id or element.id,
        pipe_id=element.id,
        name=element.name,
        design_flow_cfs=design_flow_cfs,
        length_ft=element.length_ft,
        roughness_n=element.mannings_n,
        slope_ft_per_ft=element.slope_ft_per_ft,
        diameter_in=element.diameter_in,
        upstream_invert_elevation_ft=upstream_invert_elevation_ft,
        downstream_invert_elevation_ft=downstream_invert_elevation_ft,
        upstream_rim_elevation_ft=upstream_rim_elevation_ft,
        downstream_rim_elevation_ft=downstream_rim_elevation_ft,
    )


def build_pipe_reaches_from_infrastructure(
    elements: list[InfrastructureElement],
    design_flows_cfs: list[float] | float,
) -> list[PipeReachInput]:
    """Build PipeReachInputs from a list of InfrastructureElements.

    Args:
        elements: List of InfrastructureElements ordered downstream to upstream.
        design_flows_cfs: Either a single flow value (applied to all reaches)
            or a list of flows matching the elements list.

    Returns:
        List of PipeReachInputs ready for profile calculation.

    Raises:
        InvalidHydraulicInputError: If flows list length doesn't match
            elements list length.
    """
    if isinstance(design_flows_cfs, (int, float)):
        flows = [float(design_flows_cfs)] * len(elements)
    else:
        flows = design_flows_cfs
        if len(flows) != len(elements):
            raise InvalidHydraulicInputError(
                f"design_flows_cfs length ({len(flows)}) must match "
                f"elements length ({len(elements)})"
            )

    reaches = []
    for element, flow in zip(elements, flows):
        reach = build_pipe_reach_from_infrastructure(element, flow)
        reaches.append(reach)

    return reaches
