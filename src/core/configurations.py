from typing import Any

import pydantic

DEFAULT_DATABASE_FRAMEWORK = "sqlalchemy"


class UnsupportedDatabaseFrameworkException(Exception):
    pass


class DatabaseConnectionConfig(pydantic.BaseModel):
    url: str
    args: dict[str, Any] = pydantic.Field(default_factory=dict)


class DatabaseConfig(pydantic.BaseModel):
    framework: str = DEFAULT_DATABASE_FRAMEWORK
    connection: DatabaseConnectionConfig
