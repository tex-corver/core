from typing import Any

import utils

from .. import abstract
from . import sqlalchemy_adapter

adapter_routers = {"sqlalchemy": sqlalchemy_adapter.ComponentFactory}


def create_component_factory(
    config: dict[str, Any] | None = None
) -> abstract.ComponentFactory:
    if config is None:
        config = utils.get_config()
        config = config["database"]
    framework = config.get("framework", "sqlalchemy")
    if framework not in adapter_routers:
        raise ValueError
    return adapter_routers[framework](config=config)
