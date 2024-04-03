from typing import Any

import pydantic

DEFAULT_DATABASE_FRAMEWORK = "sqlalchemy"


class UnsupportedDatabaseFrameworkException(Exception):
    """UnsupportedDatabaseFrameworkException."""


class DatabaseConnectionConfig(pydantic.BaseModel):
    """DatabaseConnectionConfig."""

    url: str
    args: dict[str, Any] = pydantic.Field(default_factory=dict)


class DatabaseConfig(pydantic.BaseModel):
    """DatabaseConfig."""

    framework: str = DEFAULT_DATABASE_FRAMEWORK
    connection: DatabaseConnectionConfig
