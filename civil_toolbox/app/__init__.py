"""Civil Toolbox opt-in application layer (Phase A).

This package is the **workflow layer**: project setup, defaults/overrides, audit,
revisions, lifecycle, and the FastAPI/HTMX surface. It depends on the kernel; the
kernel must never depend on it (enforced by tests/app/test_kernel_app_boundary.py).

Requires the optional ``[app]`` dependencies:

    pip install -e ".[app]"

The kernel (everything in ``civil_toolbox/`` outside ``app/``) stays headless and
installs without these dependencies.
"""

from civil_toolbox.app.config import AppConfig
from civil_toolbox.app.main import create_app

__all__ = ["AppConfig", "create_app"]
