import pathlib
from typing import Any, Generator
from unittest import mock

import pytest
import utils

import core
from core import unit_of_work
from core.test.fixtures import bootstrapper
from tests.double import fake

logger = utils.get_logger()

PROJECT_PATH = pathlib.Path(__file__).parents[1]


@pytest.fixture
def config_path():
    path = str(PROJECT_PATH / ".configs")
    yield path


@pytest.fixture
def config(config_path: str):
    config = utils.load_config(config_path)
    yield config


@pytest.fixture
def fake_model() -> Generator[fake.Model, Any, None]:
    yield fake.Model(name="test")


@pytest.fixture
def fake_ignore_keys_model() -> Generator[fake.IgnoreKeysModel, Any, None]:
    yield fake.IgnoreKeysModel(name="test", pin="123456")


@pytest.fixture
def command_router() -> core.CommandRouter:
    return {
        fake.CreateModelCommand: fake.create_model,
        fake.CreateModelErrorCommand: fake.create_model_with_error,
    }


@pytest.fixture
def event_router() -> core.EventRouter:
    return {
        fake.CreatedModelEvent: [
            fake.handle_created_model_1,
            fake.handle_created_model_2,
        ],
        fake.CreatedModelErrorEvent: [
            fake.handle_created_model_3,
        ],
    }
