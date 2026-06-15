"""Concrete jurisdiction authorities (Phase A).

Each authority implements the JurisdictionAuthority protocol. They resolve the
SAME registered parameter IDs to jurisdiction-specific defaults (never different
IDs for the same concept) — see PARAMETER_NAMESPACE.md §6.
"""

from civil_toolbox.design_criteria.jurisdictions.generic import GenericAuthority
from civil_toolbox.design_criteria.jurisdictions.hcfcd import HCFCDAuthority

__all__ = ["GenericAuthority", "HCFCDAuthority"]
