"""Smoke tests for the opt-in app layer.

These require the ``[app]`` optional dependencies; they skip cleanly when those
are not installed (e.g. the kernel-only CI job), which keeps the kernel install
provably dependency-light.
"""

import pytest

# The app layer needs FastAPI; skip the whole module without it.
pytest.importorskip("fastapi")


def test_app_package_imports():
    import civil_toolbox.app as app

    assert hasattr(app, "create_app")
    assert hasattr(app, "AppConfig")


def test_app_factory_creates_app():
    from civil_toolbox.app import create_app

    app = create_app()
    # FastAPI app exposes a routes collection.
    assert app.title == "Civil Toolbox App Layer"
    assert any(getattr(r, "path", None) == "/health" for r in app.routes)


def test_config_default_db_url_is_sqlite():
    from civil_toolbox.app.config import default_database_url

    assert default_database_url().startswith("sqlite:///")
