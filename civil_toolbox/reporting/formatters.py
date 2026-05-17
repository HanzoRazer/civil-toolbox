"""Value formatters for report output."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def format_number(
    value: float | None,
    precision: int = 2,
    thousands_separator: bool = True,
) -> str:
    """Format a number with specified precision.

    Args:
        value: The number to format.
        precision: Decimal places.
        thousands_separator: Whether to include comma separators.

    Returns:
        Formatted string, or "—" if value is None.
    """
    if value is None:
        return "—"

    if thousands_separator:
        return f"{value:,.{precision}f}"
    return f"{value:.{precision}f}"


def format_percent(
    value: float | None,
    precision: int = 1,
    include_sign: bool = True,
) -> str:
    """Format a percentage value.

    Args:
        value: The percentage value (e.g., 25.0 for 25%).
        precision: Decimal places.
        include_sign: Whether to include +/- prefix.

    Returns:
        Formatted string like "+25.0%" or "—" if None.
    """
    if value is None:
        return "—"

    if include_sign and value > 0:
        return f"+{value:.{precision}f}%"
    return f"{value:.{precision}f}%"


def format_delta(
    value: float | None,
    unit: str = "",
    precision: int = 2,
) -> str:
    """Format a delta value with +/- sign.

    Args:
        value: The delta value.
        unit: Unit suffix.
        precision: Decimal places.

    Returns:
        Formatted string like "+20.00 cfs" or "—" if None.
    """
    if value is None:
        return "—"

    sign = "+" if value > 0 else ""
    unit_suffix = f" {unit}" if unit else ""
    return f"{sign}{value:,.{precision}f}{unit_suffix}"


def format_value_with_unit(
    value: float | None,
    unit: str,
    precision: int = 2,
) -> str:
    """Format a value with its unit.

    Args:
        value: The value to format.
        unit: Unit suffix.
        precision: Decimal places.

    Returns:
        Formatted string like "100.00 cfs" or "—" if None.
    """
    if value is None:
        return "—"

    return f"{value:,.{precision}f} {unit}"


def format_datetime(
    dt: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S UTC",
) -> str:
    """Format a datetime for display.

    Args:
        dt: The datetime to format.
        format_string: strftime format string.

    Returns:
        Formatted datetime string.
    """
    return dt.strftime(format_string)


def format_date(
    dt: datetime,
    format_string: str = "%B %d, %Y",
) -> str:
    """Format a date for display.

    Args:
        dt: The datetime to format.
        format_string: strftime format string.

    Returns:
        Formatted date string like "May 17, 2026".
    """
    return dt.strftime(format_string)


def format_status(
    status: str,
    status_labels: dict[str, str] | None = None,
) -> str:
    """Format a status string for display.

    Args:
        status: The status value.
        status_labels: Optional mapping of status values to labels.

    Returns:
        Human-readable status label.
    """
    default_labels = {
        "ok": "OK",
        "missing_baseline": "Missing (Baseline)",
        "missing_comparison": "Missing (Comparison)",
        "undefined_zero_baseline": "N/A (Zero Baseline)",
        "not_applicable": "N/A",
    }
    labels = {**default_labels, **(status_labels or {})}
    return labels.get(status, status.replace("_", " ").title())


def format_metric_name(metric_key: str) -> str:
    """Format a metric key as a human-readable name.

    Args:
        metric_key: The metric key (e.g., "peak_flow_cfs").

    Returns:
        Human-readable name (e.g., "Peak Flow (cfs)").
    """
    metric_names = {
        "peak_flow_cfs": "Peak Flow (cfs)",
        "runoff_depth_in": "Runoff Depth (in)",
        "runoff_volume_cuft": "Runoff Volume (cf)",
        "time_of_concentration_min": "Time of Concentration (min)",
    }
    if metric_key in metric_names:
        return metric_names[metric_key]

    parts = metric_key.rsplit("_", 1)
    if len(parts) == 2:
        name, unit = parts
        return f"{name.replace('_', ' ').title()} ({unit})"
    return metric_key.replace("_", " ").title()


def escape_markdown(text: str) -> str:
    """Escape special markdown characters.

    Args:
        text: The text to escape.

    Returns:
        Text with markdown characters escaped.
    """
    chars_to_escape = ["\\", "`", "*", "_", "{", "}", "[", "]", "(", ")", "#", "+", "-", ".", "!", "|"]
    for char in chars_to_escape:
        text = text.replace(char, f"\\{char}")
    return text


def truncate(
    text: str,
    max_length: int = 100,
    suffix: str = "...",
) -> str:
    """Truncate text to a maximum length.

    Args:
        text: The text to truncate.
        max_length: Maximum length including suffix.
        suffix: Suffix to append when truncated.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
