import pathlib
from core import unit_of_work
from typing import Any, Generator
from unittest import mock

import pytest
import utils

import core
from tests.double import fake

logger = utils.get_logger()

PROJECT_PATH = pathlib.Path(__file__).parents[2]


@pytest.fixture
def config_path():
    path = str(PROJECT_PATH / ".configs")
    logger.info(path)
    yield path


@pytest.fixture
def config(config_path: str):
    config = utils.load_config(config_path)
    logger.info(config)
    yield config


@pytest.fixture
def mock_session():
    session = mock.MagicMock(spec=core.sqlalchemy_adapter.Session)
    session.core_session = mock.MagicMock()
    yield session


@pytest.fixture
def mock_component_factory(mock_session):
    factory = mock.MagicMock(spec=core.sqlalchemy_adapter.ComponentFactory)
    factory.create_session.return_value = mock_session
    with mock.patch(
        "core.sqlalchemy_adapter.ComponentFactory", return_value=factory
    ) as mock_factory:
        yield factory


@pytest.fixture
def mock_repo():
    repo = mock.MagicMock(spec=core.sqlalchemy_adapter.Repository)
    yield repo


@pytest.fixture
def mock_uow(mock_repo):
    uow = mock.MagicMock(spec=core.UnitOfWork)
    uow.repo = mock_repo
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    yield uow


@pytest.fixture
def mock_bus(mock_uow):
    bus = mock.MagicMock(spec=core.MessageBus)
    bus.uow = mock_uow
    with mock.patch("core.bootstrap.bootstrap", return_value=bus) as mock_bootstrap:
        mock_bootstrap.return_value = bus
    yield bus


@pytest.fixture
def mock_bootstrap(mock_bus):
    with mock.patch(
        "core.bootstrap.bootstrap", return_value=mock_bus
    ) as mock_bootstrap:
        yield mock_bootstrap


@pytest.fixture
def bootstrapper(
    bootstrapper_kwargs: dict[str, Any],
) -> Generator[core.Bootstrapper, Any, None]:
    bootstrapper_ = core.Bootstrapper(**bootstrapper_kwargs)
    yield bootstrapper_


def create_model(
    command: fake.CreatedModelEvent,
    mock_uow: unit_of_work.UnitOfWork,
):
    mock_uow.models.add(fake.Model(name=command.name))


def handle_created_model_1(event: fake.CreatedModelEvent):
    logger.info(event.model)


def handle_created_model_2(event: fake.CreatedModelEvent):
    logger.info(event.model)


@pytest.fixture
def command_router() -> core.CommandRouter:
    return {
        fake.CreateModelCommand: create_model,
    }


@pytest.fixture
def event_router() -> core.EventRouter:
    return {
        fake.CreatedModelEvent: [
            handle_created_model_1,
            handle_created_model_2,
        ],
    }
