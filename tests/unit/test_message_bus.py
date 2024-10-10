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
    mock_uow: mock.MagicMock,
) -> Generator[core.Dependencies, Any, None]:
    yield {
        "uow": mock_uow,
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


def assert_handle_create_model_command(
    message,
    message_bus,
    **kwargs,
):
    message_bus.command_router
    # message_bus.uow.__enter__.assert_called_once()
    # message_bus.uow.repo.add.assert_called_once()
    # added_model = message_bus.uow.repo.add.call_args[0][0]
    # assert added_model.name == message.name
    # assert added_model.message_id == message._id
    # message_bus.uow.commit.assert_called_once()
    # message_bus.uow.__exit__.assert_called_once()


@pytest.fixture
def assert_func(
    request,
):
    d = {
        "handle_create_model_command": assert_handle_create_model_command,
        "handle_create_model_error_command": lambda **kwargs: True,
    }
    ic(request.param)
    yield d[request.param]


class TestMessageBus:
    def test_init(
        self,
        message_bus: core.MessageBus,
    ):
        assert message_bus

    @pytest.mark.parametrize(
        "message",
        [
            pytest.param(
                fake.CreateModelCommand(name="test"),
                # "handle_create_model_command",
                id="handle_command_success",
            ),
            pytest.param(
                fake.CreateModelErrorCommand(name="test"),
                # "handle_create_model_error_command",
                id="handle_command_error",
                marks=pytest.mark.xfail(raises=ValueError),
            ),
        ],
    )
    def test_handle_command(
        self,
        message_bus: core.MessageBus,
        message: core.Message,
    ):
        with mock.patch.object(
            message_bus,
            "logger",
            new_callable=mock.PropertyMock,
        ) as mock_logger:
            # act
            message_bus.handle_command(message)
            # assert
            mock_logger.debug.assert_called_once()
            ic(message_bus.command_handlers[type(message)].__name__)

    @pytest.mark.skip()
    @pytest.mark.parametrize(
        "message,assert_func",
        [
            pytest.param(
                fake.CreatedModelEvent(model=fake.Model(name="test")),
                "handle_created_model_event",
                id="handle_event_success",
            ),
        ],
    )
    def test_handle_event(
        self,
        message_bus: core.MessageBus,
        message,
        mock_logger: mock.MagicMock,
        assert_func,
    ):
        message = fake.CreatedModelEvent(model=fake.Model(name="test"))
        message_bus.handle(message)
        assert_func(message=message, message_bus=message_bus)

    def test_handle_object_is_not_message(
        self,
        message_bus: core.MessageBus,
    ):
        message = "test"
        with pytest.raises(ValueError, match=f"{message} was not an Event or Command"):
            message_bus.handle(message)


    def test_handle_event_with_error(
        self,
        message_bus: core.MessageBus,
    ):
        message = fake.CreatedModelErrorEvent(model=fake.Model(name="test"))
        message_bus.handle(message)
