from typing import Any, Generator
from unittest import mock

import pytest
import utils
from icecream import ic
from sqlalchemy import Column, DateTime, String, Table

import core
from core import adapters, models
from tests.double import fake

logger = utils.get_logger()


@pytest.fixture
def start_orm_func(config: dict[str, Any]):
    def _start_orm_func():
        component_factory = adapters.create_component_factory(config)
        assert isinstance(
            component_factory, adapters.sqlalchemy_adapter.ComponentFactory
        )

        registry = component_factory.create_orm_registry()

        model_table = Table(
            "models",
            registry.metadata,
            Column("id", String, primary_key=True),
            Column("name", String),
            Column("created_time", DateTime),
        )

        registry.map_imperatively(models.BaseModel, model_table)

        engine = component_factory.engine
        registry.metadata.create_all(bind=engine)

    yield _start_orm_func




@pytest.fixture
def dependencies(
    uow: core.UnitOfWork,
) -> Generator[core.Dependencies, Any, None]:
    yield {
        "uow": uow,
    }


@pytest.fixture
def bootstrapper_kwargs(
    start_orm_func: Any,
    command_router: core.CommandRouter,
    event_router: core.EventRouter,
    dependencies: core.Dependencies,
):
    yield {
        "start_orm_func": start_orm_func,
        "command_router": command_router,
        "event_router": event_router,
        "dependencies": dependencies,
    }


class TestBootstrapper:
    def test_init(self, bootstrapper: core.Bootstrapper):
        bootstrapper

    def test_bootstrap(self, bootstrapper: core.Bootstrapper):
        bus = bootstrapper.bootstrap()
        assert isinstance(bus, core.MessageBus)
        assert bus.command_handlers == bootstrapper._injected_command_handlers
        assert bus.event_handlers == bootstrapper._injected_event_handlers
