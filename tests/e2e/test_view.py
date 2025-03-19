import uuid
from typing import Any, Callable, Generator

import pytest
import utils

import core
from core import orm
from tests.double import fake


@pytest.fixture
def model(bus: core.MessageBus) -> fake.Model:
    yield fake.Model(name=str(uuid.uuid4()))


@pytest.fixture
def add_model(
    model: fake.Model,
    bus: core.MessageBus,
) -> Generator[fake.Model, None, None]:
    with bus.uow as uow:
        uow.repo.add(model)
        uow.commit()
    yield model




@pytest.fixture(params=["builtin", "on_the_fly"])
def view(request: pytest.FixtureRequest) -> core.View:
    case_name = request.param
    match case_name:
        case "builtin":
            yield core.get_view()
        case "on_the_fly":
            yield core.View()


@pytest.mark.usefixtures("start_orm")
class TestView:

    @pytest.fixture
    def identities(
        self,
        add_model: fake.Model,
        request: pytest.FixtureRequest,
    ) -> Generator[dict[str, Any], None, None]:
        case_name = request.node.callspec.id
        match case_name:
            case case_name if case_name.endswith("success:default"):
                yield {"name": add_model.name}
            case case_name if case_name.endswith("fail:wrong-identities"):
                yield {"name": "wrong_name"}

    @pytest.fixture
    def expected_model(
        self,
        add_model: fake.Model,
        request: pytest.FixtureRequest,
    ) -> Generator[fake.Model | None, None, None]:
        case_name = request.node.callspec.id
        match case_name:
            case case_name if case_name.endswith("success:default"):
                yield add_model
            case case_name if case_name.endswith("fail:wrong-identities"):
                yield None
            case _:
                breakpoint()

    @pytest.mark.parametrize(
        "identities, expected_model",
        [
            pytest.param({}, {}, id="success:default"),
            pytest.param({}, {}, id="fail:wrong-identities"),
        ],
        indirect=["identities", "expected_model"],
    )
    def test_fetch_model(
        self,
        view: core.View,
        identities: dict[str, Any],
        expected_model: fake.Model | None,
    ) -> None:
        """Test that the default view can fetch models correctly."""
        with view.fetch_model(fake.Model, **identities) as model:
            assert model == expected_model
