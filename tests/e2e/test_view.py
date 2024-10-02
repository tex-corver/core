import uuid
from typing import Any, Callable

import pytest
import utils

import core
from core import orm
from tests.double import fake


@pytest.fixture
def model(bus: core.MessageBus):
    yield fake.Model(name=str(uuid.uuid4()))


@pytest.fixture
def add_model(
    model: fake.Model,
    bus: core.MessageBus,
):
    with bus.uow as uow:
        uow.repo.add(model)
        uow.commit()
    yield model


def _test_view(
    view: core.View,
    model: fake.Model,
):
    __test__ = False

    def _test_fetch_model(
        view: core.View,
        added_model: fake.Model,
    ):
        model = view.fetch_model(
            fake.Model,
            name=added_model.name,
        )
        assert model.name == added_model.name

    _test_fetch_model(
        view,
        model,
    )


@pytest.mark.usefixtures("start_orm")
class TestView:
    def test_default_view(
        self,
        add_model,
    ):
        view = core.VIEW
        _test_view(view, add_model)
