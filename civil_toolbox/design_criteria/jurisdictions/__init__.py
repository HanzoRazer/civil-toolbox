"""Concrete jurisdiction authorities (Phase A).

Each authority implements the JurisdictionAuthority protocol. They resolve the
SAME registered parameter IDs to jurisdiction-specific defaults (never different
IDs for the same concept) — see PARAMETER_NAMESPACE.md §6.
"""

from civil_toolbox.design_criteria.jurisdictions.generic import GenericAuthority
from civil_toolbox.design_criteria.jurisdictions.hcfcd import HCFCDAuthority

# Registry of available jurisdiction authorities, keyed by jurisdiction_id.
_AUTHORITIES = {
    authority.jurisdiction_id: authority
    for authority in (GenericAuthority(), HCFCDAuthority())
}


def get_authority(jurisdiction_id: str):
    """Return the authority for a jurisdiction ID, or None if unknown."""
    return _AUTHORITIES.get(jurisdiction_id)


def available_jurisdiction_ids() -> tuple[str, ...]:
    """Return the registered jurisdiction IDs, sorted."""
    return tuple(sorted(_AUTHORITIES))


__all__ = [
    "GenericAuthority",
    "HCFCDAuthority",
    "get_authority",
    "available_jurisdiction_ids",
]
