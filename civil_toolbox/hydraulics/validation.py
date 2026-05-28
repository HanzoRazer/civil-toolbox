"""Validation utilities for hydraulics module."""

from __future__ import annotations

from typing import Any

from civil_toolbox.hydraulics.errors import InvalidHydraulicInputError, MissingHydraulicDataError


SUPPORTED_SEVERITIES = {"info", "warning", "error"}

SUPPORTED_SURCHARGE_STATUSES = {
    "free_surface",
    "pressurized",
    "surcharged_above_crown",
    "surcharged_above_rim",
    "unknown",
}
