from typing import Any, Generator, Callable, NoReturn
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


def test_init(
    bootstrapper: core.Bootstrapper,
    bootstrapper_kwargs: dict[str, Any],
):
    logger.info(bootstrapper._injected_command_handlers)
    # TODO: write more assertions
    assert bootstrapper._injected_command_handlers


class TestBootstrapper:

    @pytest.mark.parametrize(
        "orm_func",
        [
            pytest.param(
                "start_orm_func",
                id="test_start_orm_with_orm_func",
            ),
            pytest.param(
                None,
                id="start_orm_without_orm_func",
                marks=pytest.mark.xfail(
                    raises=ValueError,
                ),
            ),
        ],
    )
    def test_start_orm(
        self,
        orm_func: Callable[..., NoReturn],
        request,
    ):
        if orm_func:
            orm_func = request.getfixturevalue(orm_func)
            bootstrapper = core.Bootstrapper(use_orm=True, orm_func=orm_func)
        else:
            bootstrapper = core.Bootstrapper(use_orm=True)

        ic(bootstrapper.orm_func)
        assert bootstrapper.orm_func == orm_func

    def test_inject_command_handlers(
        self,
        bootstrapper: core.Bootstrapper,
    ):
        for command_type, handler in bootstrapper.command_router.items():
            assert (
                bootstrapper._injected_command_handlers[command_type].__wrapped__
                == handler
            )

    def test_inject_event_handlers(
        self,
        bootstrapper: core.Bootstrapper,
    ):
        for event_type, handlers in bootstrapper.event_router.items():
            for _ in range(len(handlers)):
                assert (
                    bootstrapper._injected_event_handlers[event_type][_].__wrapped__
                    == handlers[_]
                )

    def test_bootstrap(
        self,
        bootstrapper: core.Bootstrapper,
    ):
        bus = bootstrapper.bootstrap()
        assert isinstance(bus, core.MessageBus)
        assert bus.command_handlers == bootstrapper._injected_command_handlers
        assert bus.event_handlers == bootstrapper._injected_event_handlers
