"""Parameter namespace registry parser (companion to docs/PARAMETER_NAMESPACE.md).

Parses the canonical parameter registry from ``docs/PARAMETER_NAMESPACE.md`` and
exposes the registered parameter IDs plus the format rules. This is the single
source of truth join key for the defaults system (SPEC v0.2.1 §3.8).

Pure, headless, kernel-side — no app dependencies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Regex from PARAMETER_NAMESPACE.md §2.4.
PARAMETER_ID_REGEX = re.compile(r"^[a-z][a-z0-9_]{6,58}[a-z0-9]$")

# Canonical domain prefixes from PARAMETER_NAMESPACE.md §3.
DOMAIN_PREFIXES = frozenset(
    {
        "project_",
        "hydrology_",
        "hydraulics_",
        "inlet_",
        "culvert_",
        "infrastructure_",
        "floodplain_",
        "gis_",
        "common_",
    }
)

# Repo root → docs/PARAMETER_NAMESPACE.md
_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "PARAMETER_NAMESPACE.md"
)


@dataclass(frozen=True)
class RegistryEntry:
    """A registered parameter from the namespace document."""

    parameter_id: str
    value_type: str
    deprecated: bool = False


def is_valid_parameter_id(parameter_id: str) -> bool:
    """Return True if the ID matches the regex and a canonical domain prefix."""
    if not PARAMETER_ID_REGEX.match(parameter_id):
        return False
    return any(parameter_id.startswith(prefix) for prefix in DOMAIN_PREFIXES)


def _registry_path() -> Path:
    return _REGISTRY_PATH


def parse_registry(markdown_text: str) -> list[RegistryEntry]:
    """Extract registry entries from the namespace markdown.

    Only the registry tables under the "## 4. ... registry" section are parsed.
    Section 4.2 (Phase B+ examples) is a fenced code block, not a table, so it is
    naturally excluded — those IDs are illustrative, not registered.

    A registry row looks like::

        | `project_name` | str | Always | None | Free text |

    The first backticked cell is the parameter_id; the second cell is the type.
    """
    entries: list[RegistryEntry] = []
    in_registry_section = False

    for raw in markdown_text.splitlines():
        line = raw.strip()

        if line.startswith("## "):
            # Enter on the "## 4. ... registry" heading, exit on the next "## ".
            in_registry_section = line.startswith("## 4.") and "registry" in line.lower()
            continue

        if not in_registry_section or not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue

        first = cells[0]
        # Skip header / separator rows.
        if not (first.startswith("`") and first.endswith("`")):
            continue

        parameter_id = first.strip("`").strip()
        # Skip the backticked table header cell (`parameter_id`).
        if parameter_id == "parameter_id":
            continue
        value_type = cells[1].strip("`").strip() if len(cells) > 1 else ""
        deprecated = "deprecated" in line.lower()
        entries.append(
            RegistryEntry(
                parameter_id=parameter_id,
                value_type=value_type,
                deprecated=deprecated,
            )
        )

    return entries


def load_registry(path: Path | None = None) -> list[RegistryEntry]:
    """Load and parse the registry document."""
    registry_path = path or _registry_path()
    return parse_registry(registry_path.read_text(encoding="utf-8"))


def registered_parameter_ids(path: Path | None = None) -> frozenset[str]:
    """Return the set of registered (non-deprecated) parameter IDs."""
    return frozenset(
        entry.parameter_id for entry in load_registry(path) if not entry.deprecated
    )


def require_registered_parameter_id(
    parameter_id: str, path: Path | None = None
) -> str:
    """Return the ID if registered; raise ValueError otherwise.

    Use on write paths (defaults, overrides) to reject unregistered IDs before
    they reach persistence (PARAMETER_NAMESPACE.md §5).
    """
    if parameter_id not in registered_parameter_ids(path):
        raise ValueError(
            f"Unregistered parameter_id: {parameter_id!r}. "
            "Add it to docs/PARAMETER_NAMESPACE.md before use."
        )
    return parameter_id


# --- Handoff-compatible name aliases (do not break the current names) ---
load_registered_parameter_ids = registered_parameter_ids
validate_parameter_id = is_valid_parameter_id
