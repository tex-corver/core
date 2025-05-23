from typing import Any

import utils

from core import abstract
from core.adapters import sqlalchemy_adapter

adapter_routers: dict[str, type[abstract.ComponentFactory]] = {
    "sqlalchemy": sqlalchemy_adapter.ComponentFactory,
}


def create_component_factory(
    config: dict[str, Any] | None = None,
) -> abstract.ComponentFactory:
    """create_component_factory.

    Args:
        config (dict[str, Any] | None): config

    Returns:
        abstract.ComponentFactory:
    """
    config = config or utils.get_config()["database"]

    assert config, "Database configuration is required."

    framework = config["framework"]
    if framework not in adapter_routers:
        raise ValueError

    return adapter_routers[framework](config)
