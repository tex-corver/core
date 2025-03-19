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


@pytest.fixture(params=["builtin", "on_the_fly"])
def view(request):
    case_name = request.param
    match case_name:
        case "builtin":
            yield core.get_view()
        case "on_the_fly":
            yield core.View()


@pytest.mark.usefixtures("start_orm")
class TestView:

    @pytest.fixture
    def identities(self, request):
        case_name = request.node.callspec.id
        match case_name:
            case "success:builtin":
                yield {}

    @pytest.fixture
    def expected_model(
        self,
        add_model: fake.Model,
        request,
    ):
        case_name = request.node.callspec.id
        match case_name:
            case "success:builtin":
                yield fake.Model(name="test")
            case "fail:wrong_identities":
                yield fake.Model(name="test")

    @pytest.mark.parametrize(
        "identities, expected_model",
        [
            pytest.param({}, id="success:default"),
            pytest.param({}, id="fail:wrong_identities"),
        ],
        indirect=["identities", "expected_model"],
    )
    def test_fetch_model(
        self,
        add_model: fake.Model,
        view: core.View,
        identities: dict[str, Any],
        expected_model: fake.Model,
    ):
        """Test that the default view can fetch models correctly."""
        with view.fetch_model(fake.Model, **identities) as model:
            assert model.name == expected_model.name
