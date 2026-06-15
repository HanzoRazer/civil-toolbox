"""Application configuration for the opt-in app layer.

Pure configuration — no FastAPI/SQLAlchemy imports here, so config stays cheap
to construct and free of heavy dependencies. The database path follows SPEC
v0.2.1 Q1: ``~/.civil-toolbox/app.db`` by default, env-overridable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB_DIR = Path.home() / ".civil-toolbox"
DEFAULT_DB_FILENAME = "app.db"

# Environment variables.
ENV_DATABASE_URL = "CIVIL_TOOLBOX_APP_DATABASE_URL"
ENV_DB_PATH = "CIVIL_TOOLBOX_APP_DB_PATH"


def default_database_url() -> str:
    """Return the default SQLite URL (``~/.civil-toolbox/app.db``), env-overridable.

    Resolution order:
        1. ``CIVIL_TOOLBOX_APP_DATABASE_URL`` (full SQLAlchemy URL) if set.
        2. ``CIVIL_TOOLBOX_APP_DB_PATH`` (filesystem path) -> sqlite URL.
        3. ``~/.civil-toolbox/app.db`` -> sqlite URL.
    """
    explicit_url = os.environ.get(ENV_DATABASE_URL)
    if explicit_url:
        return explicit_url

    db_path = os.environ.get(ENV_DB_PATH)
    if db_path:
        return f"sqlite:///{Path(db_path).expanduser()}"

    return f"sqlite:///{DEFAULT_DB_DIR / DEFAULT_DB_FILENAME}"


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration.

    Attributes:
        database_url: SQLAlchemy database URL.
        echo_sql: Whether SQLAlchemy should echo SQL (debug).
        seed_user_email: Email for the single-user seed fallback.
        seed_user_name: Display name for the seed user.
        seed_user_role: Role for the seed user (Phase A defaults to PE).
    """

    database_url: str = ""
    echo_sql: bool = False
    seed_user_email: str = "engineer@example.com"
    seed_user_name: str = "Seed Engineer"
    seed_user_role: str = "pe"

    @classmethod
    def from_env(cls) -> AppConfig:
        """Build configuration from environment variables (with defaults)."""
        return cls(
            database_url=default_database_url(),
            echo_sql=os.environ.get("CIVIL_TOOLBOX_APP_ECHO_SQL", "").lower()
            in {"1", "true", "yes"},
            seed_user_email=os.environ.get(
                "CIVIL_TOOLBOX_APP_SEED_EMAIL", "engineer@example.com"
            ),
            seed_user_name=os.environ.get(
                "CIVIL_TOOLBOX_APP_SEED_NAME", "Seed Engineer"
            ),
            seed_user_role=os.environ.get("CIVIL_TOOLBOX_APP_SEED_ROLE", "pe"),
        )
