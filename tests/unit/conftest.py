import pathlib
from typing import Any, Generator
from unittest import mock

import pytest
import utils

import core
from core import message_bus, unit_of_work
from core.test.fixtures import (
    mock_bootstrap,
    mock_bus,
    mock_component_factory,
    mock_repo,
    mock_session,
    mock_uow,
)
from tests.double import fake

logger = utils.get_logger()


@pytest.fixture
def command_router() -> core.CommandRouter:
    return {
        fake.CreateModelCommand: mock.Mock(),
        fake.CreateModelErrorCommand: mock.Mock(side_effect=ValueError),
    }


@pytest.fixture
def event_router() -> core.EventRouter:
    return {
        fake.CreatedModelEvent: [
            mock.Mock(),
            mock.Mock(),
        ],
        fake.CreatedModelErrorEvent: [
            mock.Mock(),
        ],
    }
