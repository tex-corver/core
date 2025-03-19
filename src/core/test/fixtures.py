from typing import Any, Generator
from unittest import mock

import pytest

from core import abstract, bootstrap, message_bus, unit_of_work


@pytest.fixture
def mock_session() -> Generator[mock.MagicMock, Any, None]:
    session = mock.MagicMock(spec=abstract.Session)
    session.core_session = mock.MagicMock()
    yield session


@pytest.fixture
def mock_component_factory(
    mock_session: mock.MagicMock,
) -> Generator[mock.MagicMock, Any, None]:
    factory = mock.MagicMock(spec=abstract.ComponentFactory)
    factory.create_session.return_value = mock_session
    with mock.patch(
        "core.sqlalchemy_adapter.ComponentFactory",
        return_value=factory,
    ) as mock_factory:
        yield mock_factory


@pytest.fixture
def mock_repo() -> Generator[mock.MagicMock, Any, None]:
    repo = mock.MagicMock(spec=abstract.Repository)
    return repo


@pytest.fixture
def mock_uow(mock_repo: mock.MagicMock) -> Generator[mock.MagicMock, Any, None]:
    uow = mock.MagicMock(spec=unit_of_work.UnitOfWork)
    uow.repo = mock_repo
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    return uow


@pytest.fixture
def mock_bus(mock_uow: mock.MagicMock) -> Generator[mock.MagicMock, Any, None]:
    bus = mock.MagicMock(spec=message_bus.MessageBus)
    bus.uow = mock_uow
    return bus


@pytest.fixture
def mock_bootstrap(mock_bus: mock.MagicMock) -> Generator[mock.MagicMock, Any, None]:
    with mock.patch(
        "core.bootstrap.bootstrap",
        return_value=mock_bus,
    ) as mock_bootstrap:
        mock_bootstrap.return_value = mock_bus
        yield mock_bootstrap


@pytest.fixture
def bootstrapper(
    bootstrapper_kwargs: dict[str, Any],
) -> Generator[bootstrap.Bootstrapper, Any, None]:
    bootstrapper_ = bootstrap.Bootstrapper(**bootstrapper_kwargs)
    yield bootstrapper_
