import pathlib
from typing import Any, Generator
from unittest import mock
from typing import Any, Callable, Generator

import pytest
from sqlalchemy import Column, DateTime, String, Table

from core.adapters import sqlalchemy_adapter as saa
from core.configurations import DatabaseConfig
import core
from core import abstract, adapters, orm
from tests.double import fake

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
def ignore_keys(request: pytest.FixtureRequest) -> set[str] | None:
    if hasattr(request.node, "callspec"):
        case_name = request.node.callspec.id
        match case_name:
            case case_name if "success:override-ignore-keys" in case_name:
                return set(["pin"])
    return {}


@pytest.fixture
def model(
    ignore_keys: set[str], request: pytest.FixtureRequest
) -> Generator[fake.Model, Any, None]:
    if hasattr(request.node, "callspec"):
        case_name = request.node.callspec.id
        match case_name:
            case case_name if "success:base" in case_name:
                yield fake.Model(name="test")
            case case_name if "success:all-fields" in case_name:
                yield fake.Model(name="test", password="123456")
            case case_name if "success:override-ignore-keys" in case_name:
                yield fake.Model(name="test", ignore_keys=ignore_keys)
            case _:
                raise ValueError(f"Invalid case name: {case_name}")
    else:
        yield fake.Model(name="test")


@pytest.fixture
def fake_ignore_keys_model() -> Generator[fake.IgnoreKeysModel, Any, None]:
    yield fake.IgnoreKeysModel(name="test", pin="123456", ignore_keys=set(["pin"]))


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


@pytest.fixture
def uow(config: dict[str, Any]) -> Generator[core.UnitOfWork, Any, None]:
    uow = core.UnitOfWork(config["database"])
    yield uow


@pytest.fixture
def database_config(
    request: pytest.FixtureRequest,
) -> dict[str, Any] | DatabaseConfig | saa.SQLAlchemyConfig:
    """"""
    config_dict = {
        "framework": "sqlalchemy",
        "connection": {
            "url": "mysql+pymysql://root:admin@192.168.0.100:3306/core",
        },
    }
    if hasattr(request.node, "callspec"):
        case_name = request.node.callspec.id
        match case_name:
            case "success:from-dict":
                return config_dict
            case "success:from-database-config":
                return DatabaseConfig(**config_dict)
            case "success:from-sqlalchemy-config":
                return saa.SQLAlchemyConfig(**config_dict)
            case _:
                raise ValueError(f"Invalid case name: {case_name}")
    return config_dict


@pytest.fixture
def component_factory(
    database_config: DatabaseConfig | dict[str, Any] | saa.SQLAlchemyConfig,
):
    """"""
    factory = saa.ComponentFactory(database_config)
    yield factory


@pytest.fixture
def dependencies(
    uow: core.UnitOfWork,
) -> Generator[core.Dependencies, Any, None]:
    yield {
        "uow": uow,
    }


@pytest.fixture
def start_orm_func(config: dict[str, Any]):
    @orm.map_once
    def _start_orm_func():
        component_factory = adapters.create_component_factory(config["database"])
        assert isinstance(
            component_factory, adapters.sqlalchemy_adapter.ComponentFactory
        )

        registry = component_factory.create_orm_registry()

        model_table = Table(
            "models",
            registry.metadata,
            Column("id", String(200), primary_key=True),
            Column("created_time", DateTime),
            Column("updated_time", DateTime),
            Column("message_id", String(200)),
            Column("name", String(200)),
        )

        registry.map_imperatively(fake.Model, model_table)

        engine = component_factory.engine
        registry.metadata.create_all(bind=engine)

    yield _start_orm_func


@pytest.fixture
def start_orm(start_orm_func: Callable[..., Any]):
    start_mapper = orm.map_once(start_orm_func)
    yield


@pytest.fixture
def bootstrapper_kwargs(
    start_orm_func: Any,
    command_router: core.CommandRouter,
    event_router: core.EventRouter,
    dependencies: core.Dependencies,
):
    yield {
        "use_orm": True,
        "orm_func": start_orm_func,
        "command_router": command_router,
        "event_router": event_router,
        "dependencies": dependencies,
    }


@pytest.fixture
def bus(bootstrapper: core.Bootstrapper) -> Generator[core.MessageBus, Any, None]:
    yield bootstrapper.bootstrap()
