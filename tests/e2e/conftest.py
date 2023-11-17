import pytest

from core import abstract, adapters


@pytest.fixture
def component_factory() -> abstract.ComponentFactory:
    adapters.create_component_factory()
