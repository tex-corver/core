from typing import Callable

import sqlalchemy.orm
import utils
from icecream import ic

import core
from core import message_bus
from core.abstract import Session

config_path = utils.get_config_path()
config = utils.load_config(config_path=config_path)

BOOTSTRAP_FUNC = None


def set_bootstrap_func(f: Callable[..., message_bus.MessageBus]):
    global BOOTSTRAP_FUNC
    BOOTSTRAP_FUNC = f


def get_bootstrap_func() -> Callable[..., MessageBus]:
    return BOOTSTRAP_FUNC


def fetch_model(model_cls, **identities) -> core.BaseModel:
    bus = BOOTSTRAP_FUNC()
    with bus.uow:
        models = bus.uow.repo.get(
            model_cls,
            **identities,
        )
        return models[0] if len(models) else None


directions = {
    "+": sqlalchemy.asc,
    "-": sqlalchemy.desc,
}


def fetch_models(
    model_cls,
    load_strategy: str = "noload",
    exclude_relationships: list[str] = None,
    orders: list[str] = None,
    limit: int = 20,
    offset: int = 0,
    **filters,
) -> list[core.BaseModel]:
    bus = BOOTSTRAP_FUNC()
    filters = filters or {}
    if orders is None:
        orders = []
    else:
        orders = orders.split(",")
        orders = [
            directions[order[0]](getattr(model_cls, order[1:])) for order in orders
        ]
    strategy = {
        "noload": sqlalchemy.orm.noload,
        "subquery": sqlalchemy.orm.subqueryload,
    }
    factory = core.sqlalchemy_adapter.ComponentFactory(config["database"])
    session = factory.create_session()
    exclude_relationships = exclude_relationships or []
    query = (
        session.core_session.query(model_cls)
        .filter_by(**filters)
        .order_by(*orders)
        .slice(offset, offset + limit)
    )
    for relationship in exclude_relationships:
        query = query.options(strategy[load_strategy](getattr(model_cls, relationship)))
    return query.all()
    return query.all()
