"""Tests for rendering HGL reports to Markdown (and PDF when available)."""

import pytest

from civil_toolbox.hydraulics.models import (
    HydraulicProfileResult,
    HydraulicWarning,
    PipeReachHydraulicResult,
)
from civil_toolbox.reporting.builtins import get_builtin_templates
from civil_toolbox.reporting.markdown import render_report_markdown
from civil_toolbox.reporting.template_builders import build_report_from_template
from civil_toolbox.reporting.template_context import ReportTemplateContext


def _profile():
    reach = PipeReachHydraulicResult(
        reach_id="R1", pipe_id="P1", design_flow_cfs=10.0, flow_area_sqft=1.77,
        velocity_fps=5.66, velocity_head_ft=0.50, friction_slope_ft_per_ft=0.004,
        friction_loss_ft=0.80, downstream_hgl_ft=100.5, upstream_hgl_ft=101.3,
        downstream_egl_ft=101.0, upstream_egl_ft=101.8,
        upstream_freeboard_ft=3.7, upstream_surcharge_status="free_surface",
        warnings=[HydraulicWarning(code="reach_warn", message="reach msg",
                                   severity="warning")],
    )
    return HydraulicProfileResult(
        id="PROF1", name="Test Profile", reaches=[reach],
        starting_downstream_hgl_ft=100.5, ending_upstream_hgl_ft=101.3,
        warnings=[HydraulicWarning(code="profile_warn", message="profile msg",
                                   severity="info", entity_id="PROF1")],
        assumptions=["Steady flow", "No minor losses"],
        references=["FHWA HEC-22", "Chow 1959"],
    )


def _build_report():
    template = next(
        t for t in get_builtin_templates() if t.id == "hydraulic_profile_report"
    )
    ctx = ReportTemplateContext(hydraulic_profile=_profile())
    return build_report_from_template(template, ctx)


class TestMarkdownRendering:
    def test_renders_to_markdown(self):
        md = render_report_markdown(_build_report())
        assert isinstance(md, str)
        assert md

    def test_includes_summary_heading(self):
        md = render_report_markdown(_build_report())
        assert "HGL Profile Summary" in md

    def test_includes_reach_table(self):
        md = render_report_markdown(_build_report())
        assert "R1" in md
        assert "Upstream EGL (ft)" in md

    def test_includes_surcharge_status(self):
        md = render_report_markdown(_build_report())
        assert "free_surface" in md

    def test_warnings_not_duplicated(self):
        # Split body/appendix: warnings live only in the appendix, once each.
        md = render_report_markdown(_build_report())
        assert md.count("profile msg") == 1
        assert md.count("reach msg") == 1


class TestPdfRendering:
    def test_pdf_smoke(self, tmp_path):
        pytest.importorskip("weasyprint")
        from civil_toolbox.reporting.pdf import export_report_to_pdf

        out = export_report_to_pdf(_build_report(), tmp_path / "hgl.pdf")
        assert out.exists()
        assert out.stat().st_size > 0
