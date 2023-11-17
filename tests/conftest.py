import pathlib
import os
import utils
import pytest
import logging

logger = logging.getLogger(__file__)


PROJECT_PATH = pathlib.Path(__file__).parents[2]


@pytest.fixture
def config_path() -> str:
    path = str(PROJECT_PATH / ".configs")
    yield path


@pytest.fixture
def config(config_path: str) -> dict[str, any]:
    config = utils.load_config_from_files(config_path)
    logger.info(config)
    yield config


config_path_ = str(PROJECT_PATH / ".configs")
config_ = utils.load_config_from_files(config_path_)
logger.info(config_)
