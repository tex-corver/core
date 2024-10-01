import uuid

import pytest
import utils

import core
from tests.double import fake


@pytest.fixture
def model():
    yield fake.Model(name=str(uuid.uuid4()))


@pytest.fixture
def add_model(model: fake.Model, uow: core.UnitOfWork):
    with uow:
        uow.repo.add(model)
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
        model = view.fetch_model(fake.Model, name="a")
        assert model.name == added_model.name

    _test_fetch_model(
        view,
        model,
    )


class TestView:
    def test_default_view(
        self,
        add_model,
    ):
        view = core.VIEW
        _test_view(view, add_model)
