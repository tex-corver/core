import pathlib

import pytest
import utils
from loguru import logger

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
