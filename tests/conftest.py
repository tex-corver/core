import pathlib
from core import unit_of_work
from typing import Any, Generator
from unittest import mock

import pytest
import utils

import core
from tests.double import fake

logger = utils.get_logger()

PROJECT_PATH = pathlib.Path(__file__).parents[1]


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
def bootstrapper(
    bootstrapper_kwargs: dict[str, Any],
) -> Generator[core.Bootstrapper, Any, None]:
    bootstrapper_ = core.Bootstrapper(**bootstrapper_kwargs)
    yield bootstrapper_


def create_model(
    command: fake.CreateModelCommand,
    uow: unit_of_work.UnitOfWork,
):
    with uow:
        uow.repo.add(fake.Model(name=command.name, message_id=command._id))
        uow.commit()


def create_model_with_error(
    command: fake.CreateModelErrorCommand,
    uow: unit_of_work.UnitOfWork,
):
    with uow:
        try:
            uow.repo.add(fake.Model(name=command.name, message_id=command._id))
            raise ValueError("Error while handling create model command")
        except ValueError as e:
            uow.rollback()
            raise


def handle_created_model_1(event: fake.CreatedModelEvent):
    logger.info(event.model)


def handle_created_model_2(event: fake.CreatedModelEvent):
    logger.info(event.model)


def handle_created_model_3(event: fake.CreatedModelErrorEvent):
    logger.info(event.model)
    raise ValueError("Error while handling created model event")


@pytest.fixture
def command_router() -> core.CommandRouter:
    return {
        fake.CreateModelCommand: create_model,
        fake.CreateModelErrorCommand: create_model_with_error,
    }


@pytest.fixture
def event_router() -> core.EventRouter:
    return {
        fake.CreatedModelEvent: [
            handle_created_model_1,
            handle_created_model_2,
        ],
        fake.CreatedModelErrorEvent: [
            handle_created_model_3,
        ],
    }
