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


def test_init(
    bootstrapper: core.Bootstrapper,
    bootstrapper_kwargs: dict[str, Any],
):
    logger.info(bootstrapper._injected_command_handlers)
    # TODO: write more assertions
    assert bootstrapper._injected_command_handlers


class TestBootstrapper:

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
