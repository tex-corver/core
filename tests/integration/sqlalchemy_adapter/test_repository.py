import pytest

from core.adapters import sqlalchemy_adapter
from tests.double import fake


@pytest.fixture
def repository(component_factory: sqlalchemy_adapter.ComponentFactory):
    return component_factory.create_repository()


@pytest.mark.usefixtures("start_orm")
class TestRepository:
    def test_add(self, repository: sqlalchemy_adapter.Repository):
        repository.add(fake.Model(name="test"))
        assert repository.get_model(fake.Model, name="test") is not None
