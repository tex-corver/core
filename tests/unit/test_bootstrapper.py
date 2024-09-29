from typing import Any, Generator
from unittest import mock

import pytest
import utils
from icecream import ic
from sqlalchemy import Column, DateTime, String, Table

import core
from core import adapters, models, unit_of_work

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


class FakeModel(core.BaseModel):
    name: str

    def __init__(
        self,
        name: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.events.append(CreatedModelEvent(model=self))


class CreateModelCommand(core.Command):
    name: str


class CreatedModelEvent(core.Event):
    model: FakeModel


def create_model(
    command: CreatedModelEvent,
    uow: unit_of_work.UnitOfWork,
):
    uow.models.add(FakeModel(name=command.name))


def handle_created_model_1(event: CreatedModelEvent):
    logger.info(event.model)


def handle_created_model_2(event: CreatedModelEvent):
    logger.info(event.model)


@pytest.fixture
def command_router() -> core.CommandRouter:
    return {
        CreateModelCommand: create_model,
    }


@pytest.fixture
def event_router() -> core.EventRouter:
    return {
        CreatedModelEvent: [
            handle_created_model_1,
            handle_created_model_2,
        ],
    }


@pytest.fixture
def uow(config: dict[str, Any]) -> unit_of_work.UnitOfWork:
    return mock.MagicMock(spec=unit_of_work.UnitOfWork)


@pytest.fixture
def dependencies(
    uow: mock.MagicMock,
) -> Generator[core.Dependencies, Any, None]:
    yield {
        "uow": uow,
    }


class TestBootstrapper:
    @pytest.fixture
    def bootstrapper_kwargs(
        self,
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

    @pytest.fixture
    def bootstrapper(
        self,
        bootstrapper_kwargs: dict[str, Any],
    ) -> Generator[core.Bootstrapper, Any, None]:
        bootstrapper_ = core.Bootstrapper(**bootstrapper_kwargs)
        yield bootstrapper_

    def test_init(
        self,
        bootstrapper: core.Bootstrapper,
        bootstrapper_kwargs: dict[str, Any],
    ):
        logger.info(bootstrapper._injected_command_handlers)
        # TODO: write more assertions
        assert bootstrapper._injected_command_handlers

    def test_start_orm_without_orm_func(self):
        with pytest.raises(
            ValueError,
            match="ORM function is required when use_orm is True",
        ):
            core.Bootstrapper(use_orm=True)

    def test_bootstrap(self, bootstrapper: core.Bootstrapper):
        bus = bootstrapper.bootstrap()
        assert isinstance(bus, core.MessageBus)
        assert bus.command_handlers == bootstrapper._injected_command_handlers
        assert bus.event_handlers == bootstrapper._injected_event_handlers
