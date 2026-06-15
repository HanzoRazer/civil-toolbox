"""FastAPI application factory for the opt-in app layer.

Phase A DO 001 establishes the factory and a health endpoint. Middleware, DB
session dependency, auth stub, and routers are layered on in later dev orders
(013+). Importing this module requires the ``[app]`` optional dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from civil_toolbox.app.config import AppConfig

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_app(config: AppConfig | None = None) -> "FastAPI":
    """Create and configure the FastAPI application.

    Args:
        config: Optional application configuration; defaults to env-derived.

    Returns:
        A configured FastAPI instance.
    """
    from fastapi import FastAPI

    app_config = config or AppConfig.from_env()

    app = FastAPI(
        title="Civil Toolbox App Layer",
        version="0.2.1",
        description="Phase A — project setup, defaults, audit (opt-in app layer).",
    )
    app.state.config = app_config

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "phase": "A"}

    return app
