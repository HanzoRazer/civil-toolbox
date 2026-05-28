"""Infrastructure table builders for reports.

Builds ReportTable objects from infrastructure data. Does not run
calculations — only formats existing data from InfrastructureNetwork
and InfrastructureCheckResult objects.

Example:
    >>> from civil_toolbox.reporting.infrastructure_tables import (
    ...     build_infrastructure_summary_table,
    ...     build_pipe_schedule_table,
    ... )
    >>> summary_table = build_infrastructure_summary_table(network)
    >>> pipe_table = build_pipe_schedule_table(network)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.models import ReportTable
from civil_toolbox.reporting.formatters import format_number

if TYPE_CHECKING:
    from civil_toolbox.infrastructure import InfrastructureNetwork
    from civil_toolbox.infrastructure_sizing import InfrastructureCheckResult


def _format_optional(value: float | None, precision: int = 2) -> str:
    """Format an optional numeric value."""
    if value is None:
        return "—"
    return format_number(value, precision=precision)


def _format_optional_str(value: str | None) -> str:
    """Format an optional string value."""
    if value is None or value == "":
        return "—"
    return value


def _count_by_status(elements: list, status_attr: str = "status") -> dict[str, int]:
    """Count elements by status."""
    counts: dict[str, int] = {
        "existing": 0,
        "proposed": 0,
        "future": 0,
        "other": 0,
    }
    for elem in elements:
        status = getattr(elem, status_attr, None)
        if status is None:
            status = elem.metadata.get("status", "other") if hasattr(elem, "metadata") else "other"
        status = status.lower() if isinstance(status, str) else "other"
        if status in counts:
            counts[status] += 1
        else:
            counts["other"] += 1
    return counts


def build_infrastructure_summary_table(
    network: InfrastructureNetwork,
) -> ReportTable:
    """Build infrastructure summary table.

    Summarizes element counts by type and status.

    Args:
        network: The infrastructure network.

    Returns:
        ReportTable with element type counts.
    """
    headers = [
        "Element Type",
        "Count",
        "Existing",
        "Proposed",
        "Future",
        "Other",
    ]

    rows = []

    element_types = [
        ("Pipes", list(network.iter_pipes())),
        ("Culverts", list(network.iter_culverts())),
        ("Channels", list(network.iter_channels())),
        ("Inlets", list(network.iter_inlets())),
        ("Detention Facilities", list(network.iter_detention())),
        ("Outlet Structures", list(network.iter_outlets())),
        ("Swales", list(network.iter_swales())),
    ]

    for type_name, elements in element_types:
        if not elements:
            continue
        counts = _count_by_status(elements)
        rows.append([
            type_name,
            str(len(elements)),
            str(counts["existing"]) if counts["existing"] > 0 else "—",
            str(counts["proposed"]) if counts["proposed"] > 0 else "—",
            str(counts["future"]) if counts["future"] > 0 else "—",
            str(counts["other"]) if counts["other"] > 0 else "—",
        ])

    node_count = len(list(network.iter_nodes()))
    if node_count > 0:
        rows.append([
            "Nodes",
            str(node_count),
            "—",
            "—",
            "—",
            "—",
        ])

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "right", "right", "right", "right", "right"],
        title="Infrastructure Summary",
    )


def build_pipe_schedule_table(
    network: InfrastructureNetwork,
) -> ReportTable:
    """Build pipe schedule table.

    Lists all pipes with their properties.

    Args:
        network: The infrastructure network.

    Returns:
        ReportTable with pipe schedule.
    """
    headers = [
        "ID",
        "Name",
        "Status",
        "Upstream Node",
        "Downstream Node",
        "Length (ft)",
        "Diameter (in)",
        "Material",
        "Slope (ft/ft)",
    ]

    rows = []
    pipes = sorted(network.iter_pipes(), key=lambda p: (p.name, p.id))

    for pipe in pipes:
        status = pipe.metadata.get("status", "—") if hasattr(pipe, "metadata") else "—"
        diameter = pipe.diameter_in if pipe.diameter_in else (
            f"{pipe.width_in}x{pipe.height_in}" if pipe.width_in else "—"
        )

        rows.append([
            pipe.id,
            pipe.name,
            _format_optional_str(status if isinstance(status, str) else None),
            _format_optional_str(pipe.upstream_node_id),
            _format_optional_str(pipe.downstream_node_id),
            _format_optional(pipe.length_ft, precision=1),
            str(diameter) if diameter != "—" else "—",
            _format_optional_str(pipe.material),
            _format_optional(pipe.slope_ft_per_ft, precision=4),
        ])

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "left", "left", "left", "left", "right", "right", "left", "right"],
        title="Pipe Schedule",
    )


def build_inlet_schedule_table(
    network: InfrastructureNetwork,
) -> ReportTable:
    """Build inlet schedule table.

    Lists all inlets with their properties.

    Args:
        network: The infrastructure network.

    Returns:
        ReportTable with inlet schedule.
    """
    headers = [
        "ID",
        "Name",
        "Status",
        "Node",
        "Type",
        "Connected Drainage Areas",
    ]

    rows = []
    inlets = sorted(network.iter_inlets(), key=lambda i: (i.name, i.id))

    for inlet in inlets:
        status = inlet.metadata.get("status", "—") if hasattr(inlet, "metadata") else "—"
        connected_areas = inlet.metadata.get("connected_drainage_areas", [])
        areas_str = ", ".join(connected_areas) if connected_areas else "—"

        rows.append([
            inlet.id,
            inlet.name,
            _format_optional_str(status if isinstance(status, str) else None),
            _format_optional_str(inlet.node_id),
            inlet.inlet_type,
            areas_str,
        ])

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "left", "left", "left", "left", "left"],
        title="Inlet Schedule",
    )


def build_detention_schedule_table(
    network: InfrastructureNetwork,
) -> ReportTable:
    """Build detention facility schedule table.

    Lists all detention facilities with their properties.

    Args:
        network: The infrastructure network.

    Returns:
        ReportTable with detention schedule.
    """
    headers = [
        "ID",
        "Name",
        "Status",
        "Type",
        "Storage Volume (cu ft)",
        "Outlet Structure",
    ]

    rows = []
    facilities = sorted(network.iter_detention(), key=lambda d: (d.name, d.id))

    for facility in facilities:
        status = facility.metadata.get("status", "—") if hasattr(facility, "metadata") else "—"
        storage = facility.total_storage_cuft
        outlet = facility.outlet_node_id

        rows.append([
            facility.id,
            facility.name,
            _format_optional_str(status if isinstance(status, str) else None),
            facility.facility_type,
            _format_optional(storage, precision=0) if storage else "—",
            _format_optional_str(outlet),
        ])

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "left", "left", "left", "right", "left"],
        title="Detention Facility Schedule",
    )


def build_infrastructure_check_summary_table(
    check_results: list[InfrastructureCheckResult],
) -> ReportTable:
    """Build infrastructure sizing check summary table.

    Summarizes capacity check results for all elements.

    Args:
        check_results: List of infrastructure check results.

    Returns:
        ReportTable with check summary.
    """
    headers = [
        "Entity ID",
        "Entity Type",
        "Check Type",
        "Status",
        "Capacity / Provided",
        "Demand / Required",
        "Margin",
        "Warnings",
    ]

    rows = []
    sorted_results = sorted(check_results, key=lambda r: (r.element_type, r.element_name, r.element_id))

    for result in sorted_results:
        status = "PASS" if result.passes else "FAIL"

        if result.capacity_cfs is not None:
            capacity = f"{result.capacity_cfs:.1f} cfs"
        elif result.storage_cuft is not None:
            capacity = f"{result.storage_cuft:,.0f} cu ft"
        else:
            capacity = "—"

        if result.design_flow_cfs is not None:
            demand = f"{result.design_flow_cfs:.1f} cfs"
        elif result.required_storage_cuft is not None:
            demand = f"{result.required_storage_cuft:,.0f} cu ft"
        else:
            demand = "—"

        if result.utilization_ratio is not None:
            margin_pct = (1.0 - result.utilization_ratio) * 100
            margin = f"{margin_pct:+.0f}%"
        elif result.storage_cuft is not None and result.required_storage_cuft is not None:
            if result.required_storage_cuft > 0:
                margin_pct = ((result.storage_cuft - result.required_storage_cuft) / result.required_storage_cuft) * 100
                margin = f"{margin_pct:+.0f}%"
            else:
                margin = "—"
        else:
            margin = "—"

        warning_count = len(result.warnings)
        warnings_str = str(warning_count) if warning_count > 0 else "—"

        check_type = result.method if result.method else "Capacity Check"

        rows.append([
            result.element_id,
            result.element_type,
            check_type,
            status,
            capacity,
            demand,
            margin,
            warnings_str,
        ])

    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "left", "left", "center", "right", "right", "right", "center"],
        title="Infrastructure Sizing Check Summary",
    )
