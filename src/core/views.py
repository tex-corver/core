import contextlib
from typing import Any, TypeVar, Type, Generator

import sqlalchemy.orm
import utils

import core
from core import bootstrap

__all__ = [
    "View",
    "VIEW",
    "get_view",
    "set_view",
]
T = TypeVar("T", bound=core.BaseModel)

SORT_DIRECTION = {
    "+": sqlalchemy.asc,
    "-": sqlalchemy.desc,
}


class View:
    """View.

    Attributes:
        config (dict[str, Any]): A dictionary indicating configurations of the application. Defaults to utils database.
    """

    config: dict[str, Any]

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or utils.get_config()["database"]

    @contextlib.contextmanager
    def fetch_model(self, model_cls: Type[T], **identities) -> Generator[T, Any, None]:
        """fetch_model.

        Args:
            model_cls (Type[T]): The class of the model.
            identities (kwargs): Identities of the model.

        Returns:
            T: An instance of the BaseModel.
        """
        factory = core.sqlalchemy_adapter.ComponentFactory(self.config)
        session = factory.create_session()
        with session.core_session:
            query = session.core_session.query(model_cls).filter_by(**identities)
            models = [model for model in query.all() if model]
            yield models[0] if len(models) else None

    @contextlib.contextmanager
    def fetch_models(
        self,
        model_cls: Type[T],
        load_strategy: str = "noload",
        exclude_relationships: list[str] | None = None,
        orders: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        **filters,
    ) -> Generator[list[T], Any, None]:
        """fetch_models

        Args:
            model_cls (Type[T]): The class of the models.
            load_strategy (str, optional): Defaults to "noload".
            exclude_relationships (list[str], optional): Defaults to None.
            orders (list[str], optional): Defaults to None.
            limit (int, optional): Defaults to 20.
            offset (int, optional): Defaults to 0.
            filters (kwargs): Filters of the query.

        Returns:
            list[T]: A list of instances of the BaseModel.
        """
        filters = filters or {}
        if orders is None:
            orders = []
        else:
            orders = orders.split(",")
            orders = [
                SORT_DIRECTION[order[0]](getattr(model_cls, order[1:]))
                for order in orders
            ]
        strategy = {
            "noload": sqlalchemy.orm.noload,
            "subquery": sqlalchemy.orm.subqueryload,
        }
        config = utils.get_config()
        factory = core.sqlalchemy_adapter.ComponentFactory(config["database"])
        session = factory.create_session()
        with session.core_session:
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
            yield query.all()


VIEW: View = View(config=utils.get_config()["database"])


def get_view() -> View:
    global VIEW
    return VIEW


def set_view(new_view: View):
    global VIEW
    VIEW = new_view
