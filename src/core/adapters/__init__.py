import sqlalchemy
from . import sqlalchemy_adapter

adapter_routers = {"sqlalchemy": sqlalchemy_adapter.ComponentFactory}
