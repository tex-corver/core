from collections.abc import Callable
import logging
import os
import pytest
import sqlalchemy
from sqlalchemy import (
    orm as sqlalchemy_orm,
    Table,
    Column,
    Integer,
    String,
    MetaData,
    ForeignKey,
)
import pathlib

import core
from core import orm, abstract, adapters, models, unit_of_work
import utils

logger = logging.getLogger(__file__)

PROJECT_PATH = pathlib.Path(__file__).parents[2]

utils.load_config_from_files(str(PROJECT_PATH / ".configs"))


@pytest.fixture
def config_path() -> str:
    path = str(PROJECT_PATH / ".configs")
    yield path


@pytest.fixture
def config(config_path: str) -> dict[str, any]:
    config = utils.load_config_from_files(config_path)
    logger.info(config)
    yield config


@pytest.fixture
def component_factory(config: dict[str, any]) -> abstract.ComponentFactory:
    factory = adapters.create_component_factory()
    yield factory


@pytest.fixture
def metadata(component_factory: abstract.ComponentFactory) -> sqlalchemy.MetaData:
    metadata = component_factory.create_metadata()
    yield metadata


@orm.map_once
def start_mappers():
    component_factory: adapters.sqlalchemy_adapter.ComponentFactory = (
        adapters.create_component_factory()
    )
    metadata = component_factory.create_metadata()
    registry = component_factory.create_orm_registry()
    model_table = Table(
        "models",
        metadata,
        Column("id", String, primary_key=True),
        Column("name", String),
        Column("created_time", sqlalchemy.DateTime),
    )
    registry.map_imperatively(models.BaseModel, model_table)
    engine = component_factory.create_engine()
    metadata.create_all(bind=engine._core_engine)


def bootstrap(
    config: dict[str, any] = utils.get_config(),
    use_orm: bool = True,
    uow: unit_of_work.UnitOfWork = unit_of_work.UnitOfWork(),
    component_factory: abstract.ComponentFactory = adapters.create_component_factory(),
    command_handlers: dict[str, Callable[..., None]] = {},
    event_handlers: dict[str, Callable[..., None]] = {},
):
    if config is None:
        config_path = os.environ.get("CONFIG_PATH", str(PROJECT_PATH / ".configs"))
        config = utils.load_config_from_files(config_path)
    if use_orm:
        start_mappers()
    metadata = component_factory.create_metadata()
    start_mappers(metadata=metadata)
    command_handlers = {}
    event_handlers = {}
    return core.InternalMessageBus(
        config=config,
        uow=uow,
        component_factory=component_factory,
        command_handlers=command_handlers,
        event_handlers=event_handlers,
    )


def test_bootstrap(
    config: dict[str, any],
):
    bus = bootstrap(config)
    with bus.uow as uow:
        model = models.BaseModel()
        uow.repo.add(model)
        uow.commit()

    with bus.uow as uow:
        model = uow.repo.get(models.BaseModel, 1)
        logger.info(model)
