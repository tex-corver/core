import logging
import os

from core import abstract, adapters, messages
import utils
from utils import creational

logger = logging.getLogger(__file__)


@creational.singleton
class UnitOfWork:
    def __init__(self, *args, **kwargs):
        self.config = utils.get_config()
        self.init_component_factory()
        
    def init_component_factory(self) -> abstract.ComponentFactory:
        framework = self.config["database"].get("framework", "sqlalchemy")
        if framework not in adapters.adapter_routers:
            raise ValueError
        self.component_factory = adapters.adapter_routers[framework](config=self.config)
    