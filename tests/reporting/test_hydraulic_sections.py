"""Tests for HGL report section builders."""

from civil_toolbox.hydraulics.models import (
    HydraulicProfileResult,
    HydraulicWarning,
    PipeReachHydraulicResult,
)
from civil_toolbox.reporting.hydraulic_sections import (
    build_hgl_assumptions_section,
    build_hgl_profile_summary_section,
    build_hgl_reach_table_section,
    build_hgl_references_section,
    build_hgl_warnings_section,
)
from civil_toolbox.reporting.models import SectionType


def _reach(reach_id="R1", **kw):
    defaults = dict(
        reach_id=reach_id, pipe_id="P1", design_flow_cfs=10.0, flow_area_sqft=1.77,
        velocity_fps=5.66, velocity_head_ft=0.50, friction_slope_ft_per_ft=0.004,
        friction_loss_ft=0.80, downstream_hgl_ft=100.5, upstream_hgl_ft=101.3,
        downstream_egl_ft=101.0, upstream_egl_ft=101.8,
        upstream_freeboard_ft=3.7, upstream_surcharge_status="free_surface",
    )
    defaults.update(kw)
    return PipeReachHydraulicResult(**defaults)


def _profile(**kw):
    defaults = dict(
        id="PROF1", name="Test Profile", reaches=[_reach()],
        starting_downstream_hgl_ft=100.5, ending_upstream_hgl_ft=101.3,
        assumptions=["Steady flow", "Steady flow", "No minor losses"],
        references=["FHWA HEC-22", "FHWA HEC-22", "Chow 1959"],
    )
    defaults.update(kw)
    return HydraulicProfileResult(**defaults)


def _types(sections):
    return [s.section_type for s in sections]


class TestSummarySection:
    def test_contains_heading_and_table(self):
        sections = build_hgl_profile_summary_section(_profile())
        assert SectionType.HEADING in _types(sections)
        assert SectionType.TABLE in _types(sections)


class TestReachSection:
    def test_contains_table(self):
        sections = build_hgl_reach_table_section(_profile())
        assert SectionType.TABLE in _types(sections)

    def test_empty_reaches_handled(self):
        sections = build_hgl_reach_table_section(_profile(reaches=[]))
        assert SectionType.TABLE not in _types(sections)
        assert SectionType.TEXT in _types(sections)


class TestWarningsSection:
    def test_aggregates_warnings(self):
        reach = _reach(warnings=[
            HydraulicWarning(code="rw", message="rw", severity="warning")
        ])
        profile = _profile(
            reaches=[reach],
            warnings=[HydraulicWarning(code="pw", message="pw", severity="info")],
        )
        sections = build_hgl_warnings_section(profile)
        assert SectionType.TABLE in _types(sections)

    def test_empty_warnings_clean(self):
        sections = build_hgl_warnings_section(_profile(warnings=[]))
        assert SectionType.TABLE not in _types(sections)
        assert SectionType.TEXT in _types(sections)


class TestAssumptionsSection:
    def test_deduplicates(self):
        sections = build_hgl_assumptions_section(_profile())
        list_sections = [s for s in sections if s.section_type == SectionType.LIST]
        assert list_sections
        assert list_sections[0].items == ["No minor losses", "Steady flow"]


class TestReferencesSection:
    def test_renders_string_references_deduped(self):
        sections = build_hgl_references_section(_profile())
        ref_sections = [s for s in sections if s.section_type == SectionType.REFERENCES]
        assert ref_sections
        # list[str], dedup preserving first-seen order
        assert ref_sections[0].items == ["FHWA HEC-22", "Chow 1959"]

    def test_empty_references_clean(self):
        sections = build_hgl_references_section(_profile(references=[]))
        assert SectionType.REFERENCES not in _types(sections)
        assert SectionType.TEXT in _types(sections)
