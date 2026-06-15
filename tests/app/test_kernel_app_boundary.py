"""Constitutional kernel/app boundary enforcement (SPEC v0.2.1 D8).

The kernel (everything in ``civil_toolbox/`` outside ``app/``) MUST NOT import
the app layer. The app may import the kernel; never the reverse. This keeps the
kernel headless and installable without the ``[app]`` optional dependencies.

This test parses source with ``ast`` (no imports executed), so it runs in both
CI tracks — including the kernel-only track that lacks app dependencies.
"""

from __future__ import annotations

import ast
from pathlib import Path

# civil_toolbox/ package root (…/civil_toolbox).
KERNEL_ROOT = Path(__file__).resolve().parents[2] / "civil_toolbox"
APP_DIR = KERNEL_ROOT / "app"

FORBIDDEN_PREFIX = "civil_toolbox.app"


def _kernel_python_files() -> list[Path]:
    """All kernel .py files (everything under civil_toolbox/ except app/)."""
    files = []
    for path in KERNEL_ROOT.rglob("*.py"):
        if APP_DIR in path.parents or path == APP_DIR:
            continue
        files.append(path)
    return files


def _imports_app(tree: ast.AST) -> bool:
    """Return True if the AST imports civil_toolbox.app (in any form)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == FORBIDDEN_PREFIX or alias.name.startswith(
                    FORBIDDEN_PREFIX + "."
                ):
                    return True
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == FORBIDDEN_PREFIX or module.startswith(
                FORBIDDEN_PREFIX + "."
            ):
                return True
            # Catch `from civil_toolbox import app`
            if module == "civil_toolbox":
                if any(alias.name == "app" for alias in node.names):
                    return True
    return False


def test_kernel_does_not_import_app():
    """No kernel module may import civil_toolbox.app."""
    offenders = []
    for path in _kernel_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if _imports_app(tree):
            offenders.append(str(path.relative_to(KERNEL_ROOT.parent)))

    assert not offenders, (
        "Kernel modules must not import the app layer "
        f"(civil_toolbox.app). Offenders:\n  " + "\n  ".join(offenders)
    )


def test_boundary_scan_found_kernel_files():
    """Guard against a vacuous pass if the walk finds nothing."""
    assert len(_kernel_python_files()) > 50, "Kernel file walk found too few files."
