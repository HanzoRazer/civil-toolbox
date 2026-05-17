"""Tests for value formatters."""

import pytest
from datetime import datetime, timezone

from civil_toolbox.reporting.formatters import (
    format_number,
    format_percent,
    format_delta,
    format_value_with_unit,
    format_datetime,
    format_date,
    format_status,
    format_metric_name,
    escape_markdown,
    truncate,
)


class TestFormatNumber:
    """Tests for format_number."""

    def test_formats_with_precision(self):
        """Formats number with specified precision."""
        assert format_number(123.456, precision=2) == "123.46"
        assert format_number(123.456, precision=1) == "123.5"
        assert format_number(123.456, precision=0) == "123"

    def test_includes_thousands_separator(self):
        """Includes thousands separator by default."""
        assert format_number(1234567.89, precision=2) == "1,234,567.89"

    def test_without_thousands_separator(self):
        """Can disable thousands separator."""
        assert format_number(1234567.89, precision=2, thousands_separator=False) == "1234567.89"

    def test_returns_dash_for_none(self):
        """Returns em-dash for None."""
        assert format_number(None) == "—"

    def test_handles_zero(self):
        """Handles zero correctly."""
        assert format_number(0.0, precision=2) == "0.00"

    def test_handles_negative(self):
        """Handles negative numbers."""
        assert format_number(-123.45, precision=2) == "-123.45"


class TestFormatPercent:
    """Tests for format_percent."""

    def test_formats_positive_with_sign(self):
        """Formats positive percent with + sign."""
        assert format_percent(25.0, precision=1) == "+25.0%"

    def test_formats_negative(self):
        """Formats negative percent."""
        assert format_percent(-15.5, precision=1) == "-15.5%"

    def test_formats_zero(self):
        """Formats zero percent."""
        assert format_percent(0.0, precision=1) == "0.0%"

    def test_without_sign(self):
        """Can disable sign prefix."""
        assert format_percent(25.0, precision=1, include_sign=False) == "25.0%"

    def test_returns_dash_for_none(self):
        """Returns em-dash for None."""
        assert format_percent(None) == "—"

    def test_custom_precision(self):
        """Supports custom precision."""
        assert format_percent(33.333, precision=2) == "+33.33%"


class TestFormatDelta:
    """Tests for format_delta."""

    def test_formats_positive_delta(self):
        """Formats positive delta with + sign."""
        assert format_delta(20.0, unit="cfs", precision=2) == "+20.00 cfs"

    def test_formats_negative_delta(self):
        """Formats negative delta."""
        assert format_delta(-15.5, unit="cfs", precision=2) == "-15.50 cfs"

    def test_formats_zero(self):
        """Formats zero delta."""
        assert format_delta(0.0, unit="cfs", precision=2) == "0.00 cfs"

    def test_without_unit(self):
        """Formats without unit."""
        assert format_delta(10.0, precision=1) == "+10.0"

    def test_returns_dash_for_none(self):
        """Returns em-dash for None."""
        assert format_delta(None, unit="cfs") == "—"

    def test_includes_thousands_separator(self):
        """Includes thousands separator."""
        assert format_delta(1500.0, unit="cf", precision=0) == "+1,500 cf"


class TestFormatValueWithUnit:
    """Tests for format_value_with_unit."""

    def test_formats_with_unit(self):
        """Formats value with unit suffix."""
        assert format_value_with_unit(100.0, "cfs", precision=2) == "100.00 cfs"

    def test_returns_dash_for_none(self):
        """Returns em-dash for None."""
        assert format_value_with_unit(None, "cfs") == "—"

    def test_includes_thousands_separator(self):
        """Includes thousands separator."""
        assert format_value_with_unit(50000.0, "cf", precision=0) == "50,000 cf"


class TestFormatDatetime:
    """Tests for format_datetime."""

    def test_default_format(self):
        """Uses default format."""
        dt = datetime(2026, 5, 17, 14, 30, 0, tzinfo=timezone.utc)
        result = format_datetime(dt)
        assert result == "2026-05-17 14:30:00 UTC"

    def test_custom_format(self):
        """Supports custom format."""
        dt = datetime(2026, 5, 17, 14, 30, 0)
        result = format_datetime(dt, "%Y/%m/%d")
        assert result == "2026/05/17"


class TestFormatDate:
    """Tests for format_date."""

    def test_default_format(self):
        """Uses default format."""
        dt = datetime(2026, 5, 17)
        result = format_date(dt)
        assert result == "May 17, 2026"

    def test_custom_format(self):
        """Supports custom format."""
        dt = datetime(2026, 5, 17)
        result = format_date(dt, "%m/%d/%Y")
        assert result == "05/17/2026"


class TestFormatStatus:
    """Tests for format_status."""

    def test_known_status(self):
        """Formats known status values."""
        assert format_status("ok") == "OK"
        assert format_status("missing_baseline") == "Missing (Baseline)"
        assert format_status("missing_comparison") == "Missing (Comparison)"

    def test_unknown_status(self):
        """Formats unknown status by titlecasing."""
        assert format_status("custom_status") == "Custom Status"

    def test_custom_labels(self):
        """Supports custom labels."""
        labels = {"ok": "Good", "error": "Bad"}
        assert format_status("ok", labels) == "Good"
        assert format_status("error", labels) == "Bad"


class TestFormatMetricName:
    """Tests for format_metric_name."""

    def test_known_metrics(self):
        """Formats known metric keys."""
        assert format_metric_name("peak_flow_cfs") == "Peak Flow (cfs)"
        assert format_metric_name("runoff_depth_in") == "Runoff Depth (in)"
        assert format_metric_name("runoff_volume_cuft") == "Runoff Volume (cf)"
        assert format_metric_name("time_of_concentration_min") == "Time of Concentration (min)"

    def test_unknown_metric_with_unit(self):
        """Formats unknown metric with unit suffix."""
        assert format_metric_name("velocity_fps") == "Velocity (fps)"

    def test_unknown_metric_infers_unit(self):
        """Formats unknown metric by inferring unit from suffix."""
        assert format_metric_name("custom_value") == "Custom (value)"
        assert format_metric_name("area_sqft") == "Area (sqft)"


class TestEscapeMarkdown:
    """Tests for escape_markdown."""

    def test_escapes_special_chars(self):
        """Escapes markdown special characters."""
        assert escape_markdown("*bold*") == "\\*bold\\*"
        assert escape_markdown("_italic_") == "\\_italic\\_"
        assert escape_markdown("[link]") == "\\[link\\]"
        assert escape_markdown("`code`") == "\\`code\\`"

    def test_escapes_backslash(self):
        """Escapes backslash."""
        assert escape_markdown("a\\b") == "a\\\\b"

    def test_plain_text_unchanged(self):
        """Plain text is unchanged."""
        assert escape_markdown("Hello World") == "Hello World"


class TestTruncate:
    """Tests for truncate."""

    def test_short_text_unchanged(self):
        """Short text is unchanged."""
        assert truncate("Hello", max_length=10) == "Hello"

    def test_truncates_long_text(self):
        """Truncates long text with suffix."""
        assert truncate("Hello World", max_length=8) == "Hello..."

    def test_custom_suffix(self):
        """Supports custom suffix."""
        assert truncate("Hello World", max_length=9, suffix="…") == "Hello Wo…"

    def test_exact_length(self):
        """Exact length is unchanged."""
        assert truncate("12345", max_length=5) == "12345"
