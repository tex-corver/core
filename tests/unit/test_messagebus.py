from typing import Any, Generator
from unittest import mock

import pytest
import utils
from icecream import ic
from sqlalchemy import Column, DateTime, String, Table

import core
from core import orm
from tests.double import fake

logger = utils.get_logger()


@pytest.fixture
def start_orm_func(config: dict[str, Any]):
    yield mock.MagicMock(orm.map_once(lambda: None))


@pytest.fixture
def dependencies(
    uow: mock.MagicMock,
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


@pytest.fixture
def message_bus(
    bootstrapper: core.Bootstrapper,
) -> Generator[core.MessageBus, Any, None]:
    bus = bootstrapper.bootstrap()
    yield bus


class TestMessageBus:
    def test_init(
        self,
        message_bus: core.MessageBus,
    ):
        assert message_bus

    def test_handle_command(
        self,
        message_bus: core.MessageBus,
    ):
        message = fake.CreateModelCommand(name="test")
        message_bus.handle(message)
        assert True

    def test_handle_event(
        self,
        message_bus: core.MessageBus,
    ):
        message = fake.CreatedModelEvent(model=fake.Model(name="test"))
        message_bus.handle(message)
        assert True

    def test_handle_object_is_not_message(
        self,
        message_bus: core.MessageBus,
    ):
        message = "test"
        with pytest.raises(ValueError, match=f"{message} was not an Event or Command"):
            message_bus.handle(message)

    def test_handle_command_with_error(
        self,
        message_bus: core.MessageBus,
    ):
        message = fake.CreateModelErrorCommand(name="test")
        with pytest.raises(
            ValueError, match="Error while handling create model command"
        ):
            message_bus.handle(message)

    def test_handle_event_with_error(
        self,
        message_bus: core.MessageBus,
    ):
        message = fake.CreatedModelErrorEvent(model=fake.Model(name="test"))
        message_bus.handle(message)
