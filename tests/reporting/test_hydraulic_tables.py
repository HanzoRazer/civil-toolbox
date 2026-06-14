"""Tests for HGL report table builders."""

from civil_toolbox.hydraulics.models import (
    HydraulicProfileResult,
    HydraulicWarning,
    PipeReachHydraulicResult,
)
from civil_toolbox.reporting.hydraulic_tables import (
    build_hgl_assumption_table,
    build_hgl_profile_summary_table,
    build_hgl_reach_table,
    build_hgl_warning_table,
)


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
        warnings=[HydraulicWarning(code="profile_warn", message="profile msg",
                                   severity="info", entity_id="PROF1")],
        assumptions=["Steady flow", "Steady flow", "No minor losses"],
        references=["FHWA HEC-22", "Chow 1959"],
    )
    defaults.update(kw)
    return HydraulicProfileResult(**defaults)


class TestSummaryTable:
    def test_renders_profile_metadata(self):
        table = build_hgl_profile_summary_table(_profile())
        assert table.rows[0][0] == "PROF1"
        assert table.rows[0][1] == "Test Profile"
        assert table.rows[0][2] == "1"  # reach count
        assert "100.5" in table.rows[0][3]

    def test_missing_ending_hgl_renders_dash(self):
        table = build_hgl_profile_summary_table(_profile(ending_upstream_hgl_ft=None))
        assert table.rows[0][4] == "—"

    def test_warning_count(self):
        # 1 profile warning + 0 reach warnings on the default reach
        table = build_hgl_profile_summary_table(_profile())
        assert table.rows[0][5] == "1"


class TestReachTable:
    def test_renders_all_reaches(self):
        profile = _profile(reaches=[_reach("R1"), _reach("R2")])
        table = build_hgl_reach_table(profile)
        assert len(table.rows) == 2
        assert table.rows[0][0] == "R1"
        assert table.rows[1][0] == "R2"

    def test_surcharge_status_is_upstream(self):
        table = build_hgl_reach_table(_profile())
        # Surcharge Status column index 9
        assert table.rows[0][9] == "free_surface"

    def test_missing_freeboard_renders_dash(self):
        profile = _profile(reaches=[_reach(upstream_freeboard_ft=None)])
        table = build_hgl_reach_table(profile)
        assert table.rows[0][10] == "—"


class TestWarningTable:
    def test_includes_profile_warnings(self):
        table = build_hgl_warning_table(_profile())
        codes = [r[1] for r in table.rows]
        assert "profile_warn" in codes

    def test_includes_reach_warnings_with_reach_fallback(self):
        reach = _reach("R9", warnings=[
            HydraulicWarning(code="reach_warn", message="rw", severity="warning")
        ])
        table = build_hgl_warning_table(_profile(reaches=[reach]))
        reach_rows = [r for r in table.rows if r[1] == "reach_warn"]
        assert reach_rows
        assert reach_rows[0][0] == "R9"  # entity_id fell back to reach_id


class TestAssumptionTable:
    def test_deduplicates_deterministically(self):
        table = build_hgl_assumption_table(_profile())
        assumptions = [r[1] for r in table.rows]
        # "Steady flow" appeared twice in input; deduped + sorted
        assert assumptions == ["No minor losses", "Steady flow"]
