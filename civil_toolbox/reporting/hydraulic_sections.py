"""Hydraulic (HGL) section builders for reports.

Builds ReportSection objects from HydraulicProfileResult data. Does not run
calculations — only formats existing data.

HGL references are plain strings (``list[str]``) on the hydraulics result, so the
references section renders them directly rather than routing through the generic
dict-based reference machinery.

Example:
    >>> from civil_toolbox.reporting.hydraulic_sections import (
    ...     build_hgl_profile_summary_section,
    ...     build_hgl_reach_table_section,
    ... )
    >>> sections = build_hgl_profile_summary_section(profile)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.reporting.hydraulic_tables import (
    build_hgl_assumption_table,
    build_hgl_profile_summary_table,
    build_hgl_reach_table,
    build_hgl_warning_table,
)
from civil_toolbox.reporting.models import ReportSection, SectionType
from civil_toolbox.reporting.sections import (
    create_heading,
    create_list,
    create_table_section,
    create_text,
)

if TYPE_CHECKING:
    from civil_toolbox.hydraulics.models import HydraulicProfileResult


def build_hgl_profile_summary_section(
    profile: HydraulicProfileResult,
    title: str = "HGL Profile Summary",
    level: int = 2,
) -> list[ReportSection]:
    """Build the HGL profile summary section."""
    sections = [create_heading(title, level=level)]
    sections.append(create_table_section(build_hgl_profile_summary_table(profile)))
    return sections


def build_hgl_reach_table_section(
    profile: HydraulicProfileResult,
    title: str = "HGL Reach Results",
    level: int = 2,
) -> list[ReportSection]:
    """Build the reach-by-reach HGL results section."""
    sections = [create_heading(title, level=level)]
    if not profile.reaches:
        sections.append(create_text("No reaches in profile."))
        return sections
    sections.append(create_table_section(build_hgl_reach_table(profile)))
    return sections


def build_hgl_warnings_section(
    profile: HydraulicProfileResult,
    title: str = "HGL Warnings",
    level: int = 2,
) -> list[ReportSection]:
    """Build the HGL warnings section (profile + reach warnings)."""
    sections = [create_heading(title, level=level)]
    if not profile.all_warnings():
        sections.append(create_text("No warnings generated."))
        return sections
    sections.append(create_table_section(build_hgl_warning_table(profile)))
    return sections


def build_hgl_assumptions_section(
    profile: HydraulicProfileResult,
    title: str = "HGL Assumptions",
    level: int = 2,
) -> list[ReportSection]:
    """Build the HGL assumptions section (deduplicated)."""
    sections = [create_heading(title, level=level)]
    assumptions = sorted(set(profile.assumptions))
    if not assumptions:
        sections.append(create_text("No assumptions recorded."))
        return sections
    sections.append(create_list(assumptions))
    return sections


def build_hgl_references_section(
    profile: HydraulicProfileResult,
    title: str = "References",
    level: int = 2,
) -> list[ReportSection]:
    """Build the HGL references section from the result's ``list[str]``.

    Deduplicates while preserving first-seen order.
    """
    sections = [create_heading(title, level=level)]

    seen: set[str] = set()
    deduped: list[str] = []
    for ref in profile.references:
        if ref not in seen:
            seen.add(ref)
            deduped.append(ref)

    if not deduped:
        sections.append(create_text("No references recorded."))
        return sections

    sections.append(
        ReportSection(section_type=SectionType.REFERENCES, items=deduped)
    )
    return sections
