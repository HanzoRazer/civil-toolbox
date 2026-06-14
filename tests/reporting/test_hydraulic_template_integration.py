"""Tests for HGL integration into the report template system."""

import pytest

from civil_toolbox.hydraulics.models import (
    HydraulicProfileResult,
    PipeReachHydraulicResult,
)
from civil_toolbox.reporting.builtins import get_builtin_templates
from civil_toolbox.reporting.models import Report
from civil_toolbox.reporting.report_templates import (
    ReportTemplate,
    SectionTemplate,
    SUPPORTED_SECTION_TYPES,
)
from civil_toolbox.reporting.template_builders import build_report_from_template
from civil_toolbox.reporting.template_context import ReportTemplateContext
from civil_toolbox.reporting.template_validation import (
    ContextValidationError,
    validate_template_context,
)

HGL_SECTION_TYPES = [
    "hgl_profile_summary",
    "hgl_reach_table",
    "hgl_warnings",
    "hgl_assumptions",
    "hgl_references",
]


def _profile():
    reach = PipeReachHydraulicResult(
        reach_id="R1", pipe_id="P1", design_flow_cfs=10.0, flow_area_sqft=1.77,
        velocity_fps=5.66, velocity_head_ft=0.50, friction_slope_ft_per_ft=0.004,
        friction_loss_ft=0.80, downstream_hgl_ft=100.5, upstream_hgl_ft=101.3,
        downstream_egl_ft=101.0, upstream_egl_ft=101.8,
        upstream_freeboard_ft=3.7, upstream_surcharge_status="free_surface",
    )
    return HydraulicProfileResult(
        id="PROF1", name="Test Profile", reaches=[reach],
        starting_downstream_hgl_ft=100.5, ending_upstream_hgl_ft=101.3,
        assumptions=["Steady flow"], references=["FHWA HEC-22"],
    )


class TestContext:
    def test_accepts_hydraulic_profile(self):
        ctx = ReportTemplateContext(hydraulic_profile=_profile())
        assert ctx.has_hydraulic_profile() is True

    def test_no_profile(self):
        ctx = ReportTemplateContext()
        assert ctx.has_hydraulic_profile() is False
        assert ctx.has_hydraulic_profiles() is False

    def test_has_hydraulic_profiles(self):
        ctx = ReportTemplateContext(hydraulic_profiles=[_profile()])
        assert ctx.has_hydraulic_profiles() is True


class TestSectionTypes:
    @pytest.mark.parametrize("section_type", HGL_SECTION_TYPES)
    def test_section_types_supported(self, section_type):
        assert section_type in SUPPORTED_SECTION_TYPES


def _template_with(section_type, required=True):
    return ReportTemplate(
        id="t", name="t", version="1.0",
        sections=[SectionTemplate(id="s", title="S", section_type=section_type,
                                  required=required)],
    )


class TestContextValidation:
    def test_required_hgl_section_without_context_fails(self):
        template = _template_with("hgl_reach_table", required=True)
        with pytest.raises(ContextValidationError):
            validate_template_context(template, ReportTemplateContext())

    def test_optional_hgl_section_without_context_warns(self):
        template = _template_with("hgl_reach_table", required=False)
        warnings = validate_template_context(template, ReportTemplateContext())
        assert any("hydraulic_profile" in w for w in warnings)


class TestBuiltinTemplate:
    def test_builtin_exists(self):
        ids = {t.id for t in get_builtin_templates()}
        assert "hydraulic_profile_report" in ids

    def test_builtin_builds_report(self):
        template = next(
            t for t in get_builtin_templates() if t.id == "hydraulic_profile_report"
        )
        ctx = ReportTemplateContext(hydraulic_profile=_profile())
        report = build_report_from_template(template, ctx)
        assert isinstance(report, Report)
        assert len(report.sections) > 0
