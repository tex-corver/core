__all__ = [
    "View",
    "VIEW",
]
from typing import Any

import sqlalchemy.orm
import utils

import core
from core import bootstrap

directions = {
    "+": sqlalchemy.asc,
    "-": sqlalchemy.desc,
}


class View:
    config: dict[str, Any]

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or utils.get_config()["database"]

    def fetch_model(self, model_cls, **identities) -> core.BaseModel:
        bus = bootstrap.bootstrap()
        with bus.uow:
            models = bus.uow.repo.get(
                model_cls,
                **identities,
            )
            return models[0] if len(models) else None

    def fetch_models(
        self,
        model_cls,
        load_strategy: str = "noload",
        exclude_relationships: list[str] = None,
        orders: list[str] = None,
        limit: int = 20,
        offset: int = 0,
        **filters,
    ) -> list[core.BaseModel]:
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
        config = utils.get_config()
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
            query = query.options(
                strategy[load_strategy](getattr(model_cls, relationship))
            )
        return query.all()


VIEW: View = View(config=utils.get_config())


def get_view() -> View:
    global VIEW
    return VIEW


def set_view(new_view: View):
    global VIEW
    VIEW = new_view


def fetch_model(model_cls, **identities) -> core.BaseModel:
    return get_view().fetch_model(model_cls, **identities)


def fetch_models(
    model_cls,
    load_strategy: str = "noload",
    exclude_relationships: list[str] = None,
    orders: list[str] = None,
    limit: int = 20,
    offset: int = 0,
    **filters,
) -> list[core.BaseModel]:
    return get_view().fetch_models(
        model_cls,
        load_strategy,
        exclude_relationships,
        orders,
        limit,
        offset,
        **filters,
    )
