import pathlib
from core import unit_of_work
from typing import Any, Generator
from unittest import mock

import pytest
import utils

import core
from tests.double import fake

logger = utils.get_logger()


@pytest.fixture
def session():
    session = mock.MagicMock(spec=core.sqlalchemy_adapter.Session)
    session.core_session = mock.MagicMock()
    yield session


@pytest.fixture
def component_factory(session):
    factory = mock.MagicMock(spec=core.sqlalchemy_adapter.ComponentFactory)
    factory.create_session.return_value = session
    with mock.patch(
        "core.sqlalchemy_adapter.ComponentFactory", return_value=factory
    ) as mock_factory:
        yield factory


@pytest.fixture
def repo():
    repo = mock.MagicMock(spec=core.sqlalchemy_adapter.Repository)
    yield repo


@pytest.fixture
def uow(repo):
    uow = mock.MagicMock(spec=core.UnitOfWork)
    uow.repo = repo
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    yield uow


@pytest.fixture
def bus(uow):
    bus = mock.MagicMock(spec=core.MessageBus)
    bus.uow = uow
    with mock.patch("core.bootstrap.bootstrap", return_value=bus) as mock_bootstrap:
        mock_bootstrap.return_value = bus
    yield bus


@pytest.fixture
def bootstrap(bus):
    with mock.patch("core.bootstrap.bootstrap", return_value=bus) as mock_bootstrap:
        yield mock_bootstrap
