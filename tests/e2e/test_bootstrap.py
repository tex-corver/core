import pathlib
from typing import Any

import core
import pytest
import utils
from core import adapters, models, unit_of_work
from loguru import logger
from sqlalchemy import Column, DateTime, String, Table


@pytest.fixture
def config(tmp_path: pathlib.Path):
    sqlite_path = tmp_path / "test.db"
    config = utils.Configuration(
        {
            "database": {
                "framework": "sqlalchemy",
                "connection": {"url": "sqlite:///" + sqlite_path.as_posix()},
            },
        }
    )

    yield config


def start_mappers(config: dict[str, Any]):
    component_factory = adapters.create_component_factory(config)
    assert isinstance(component_factory, adapters.sqlalchemy_adapter.ComponentFactory)

    registry = component_factory.create_orm_registry()

    model_table = Table(
        "models",
        registry.metadata,
        Column("id", String, primary_key=True),
        Column("name", String),
        Column("created_time", DateTime),
    )

    registry.map_imperatively(models.BaseModel, model_table)

    engine = component_factory.engine
    registry.metadata.create_all(bind=engine)


def bootstrap(
    config: dict[str, Any],
    use_orm: bool = False,
):
    if use_orm:
        start_mappers(config)

    return core.MessageBus(
        uow=unit_of_work.UnitOfWork(config),
        command_handlers={},
        event_handlers={},
    )


def test_bootstrap(
    config: dict[str, Any],
):
    bus = bootstrap(config, True)

    model = models.BaseModel()
    logger.info(model)

    with bus.uow as uow:
        uow.repo.add(model)
        uow.commit()

    with bus.uow as uow:
        results = uow.repo.get(models.BaseModel)
        logger.info(results)
        assert all(result.id == model.id for result in results)
