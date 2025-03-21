import pytest
from typing import Any

from sqlalchemy import orm as sqlalchemy_orm

from core.adapters import sqlalchemy_adapter as saa
from core.configurations import DatabaseConfig


@pytest.fixture
def factory(component_factory: saa.ComponentFactory):
    return component_factory


class TestComponentFactory:
    """TestComponentFactory."""

    @pytest.mark.parametrize(
        "database_config",
        [
            pytest.param({}, id="success:from-dict"),
            pytest.param({}, id="success:from-database-config"),
            pytest.param({}, id="success:from-sqlalchemy-config"),
        ],
        indirect=["database_config"],
    )
    def test_init(self, database_config):
        """"""
        factory = saa.ComponentFactory(database_config)
        assert isinstance(factory.config, saa.SQLAlchemyConfig)

    def test_create_session(self, factory: saa.ComponentFactory):
        """"""
        session = factory.create_session()
        assert isinstance(session, saa.Session)

    def test_create_repository(self, factory: saa.ComponentFactory):
        """"""
        repo = factory.create_repository()
        assert isinstance(repo, saa.Repository)

    def test_create_orm_registry(self, factory: saa.ComponentFactory):
        """"""
        registry = factory.create_orm_registry()
        assert isinstance(registry, sqlalchemy_orm.registry)
