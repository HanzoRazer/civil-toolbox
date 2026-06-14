"""Hydraulic (HGL) table builders for reports.

Builds ReportTable objects from HydraulicProfileResult data. Does not run
calculations — only formats existing data from the hydraulics foundation.

Example:
    >>> from civil_toolbox.reporting.hydraulic_tables import (
    ...     build_hgl_profile_summary_table,
    ...     build_hgl_reach_table,
    ... )
    >>> summary = build_hgl_profile_summary_table(profile)
    >>> reaches = build_hgl_reach_table(profile)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.formatters import format_number
from civil_toolbox.reporting.models import ReportTable

if TYPE_CHECKING:
    from civil_toolbox.hydraulics.models import HydraulicProfileResult


def _fmt(value: float | None, precision: int = 2) -> str:
    """Format an optional numeric value ('—' when missing)."""
    return format_number(value, precision=precision)


def _fmt_str(value: str | None) -> str:
    """Format an optional string value ('—' when missing)."""
    if value is None or value == "":
        return "—"
    return value


def build_hgl_profile_summary_table(profile: HydraulicProfileResult) -> ReportTable:
    """Build the HGL profile summary table (one row per profile)."""
    headers = [
        "Profile ID",
        "Name",
        "Reach Count",
        "Starting Downstream HGL (ft)",
        "Ending Upstream HGL (ft)",
        "Warnings",
    ]
    warning_count = len(profile.all_warnings())
    rows = [[
        profile.id,
        _fmt_str(profile.name),
        str(len(profile.reaches)),
        _fmt(profile.starting_downstream_hgl_ft),
        _fmt(profile.ending_upstream_hgl_ft),
        str(warning_count) if warning_count else "—",
    ]]
    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "left", "right", "right", "right", "right"],
        title="HGL Profile Summary",
    )


def build_hgl_reach_table(profile: HydraulicProfileResult) -> ReportTable:
    """Build the reach-by-reach HGL results table.

    Surcharge status and freeboard are reported for the upstream end of each
    reach (the controlling end as the profile is computed downstream to upstream).
    """
    headers = [
        "Reach ID",
        "Pipe ID",
        "Design Flow (cfs)",
        "Velocity (fps)",
        "Velocity Head (ft)",
        "Friction Loss (ft)",
        "Downstream HGL (ft)",
        "Upstream HGL (ft)",
        "Upstream EGL (ft)",
        "Surcharge Status",
        "Freeboard to Rim (ft)",
    ]
    rows = []
    for reach in profile.reaches:
        rows.append([
            reach.reach_id,
            reach.pipe_id,
            _fmt(reach.design_flow_cfs),
            _fmt(reach.velocity_fps),
            _fmt(reach.velocity_head_ft),
            _fmt(reach.friction_loss_ft, precision=3),
            _fmt(reach.downstream_hgl_ft),
            _fmt(reach.upstream_hgl_ft),
            _fmt(reach.upstream_egl_ft),
            _fmt_str(reach.upstream_surcharge_status),
            _fmt(reach.upstream_freeboard_ft),
        ])
    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=[
            "left", "left", "right", "right", "right", "right",
            "right", "right", "right", "left", "right",
        ],
        title="HGL Reach Results",
    )


def build_hgl_warning_table(profile: HydraulicProfileResult) -> ReportTable:
    """Build the HGL warning table.

    Includes profile-level and reach-level warnings. Reach-level warnings that
    carry no entity_id fall back to the reach ID so they are not orphaned.
    """
    headers = ["Entity ID", "Code", "Severity", "Message"]
    rows = []
    for warning in profile.warnings:
        rows.append([
            _fmt_str(warning.entity_id),
            warning.code,
            warning.severity,
            warning.message,
        ])
    for reach in profile.reaches:
        for warning in reach.warnings:
            entity = warning.entity_id or reach.reach_id
            rows.append([
                _fmt_str(entity),
                warning.code,
                warning.severity,
                warning.message,
            ])
    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["left", "left", "center", "left"],
        title="HGL Warnings",
    )


def build_hgl_assumption_table(profile: HydraulicProfileResult) -> ReportTable:
    """Build the HGL assumptions table (deduplicated, deterministic order)."""
    headers = ["#", "Assumption"]
    deduped = sorted(set(profile.assumptions))
    rows = [[str(i + 1), assumption] for i, assumption in enumerate(deduped)]
    return ReportTable(
        headers=headers,
        rows=rows,
        alignments=["right", "left"],
        title="HGL Assumptions",
    )
