from . import sqlalchemy_adapter
from .. import abstract
import utils

adapter_routers = {"sqlalchemy": sqlalchemy_adapter.ComponentFactory}


def create_component_factory(
    config: dict[str, any] = None
) -> abstract.ComponentFactory:
    if config is None:
        config = utils.get_config()
        config = config["database"]
    framework = config.get("framework", "sqlalchemy")
    if framework not in adapter_routers:
        raise ValueError
    return adapter_routers[framework](config=config)
