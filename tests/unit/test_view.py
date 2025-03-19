from unittest import mock

import pytest

import core
from core import views
from tests.double import fake


class TestView:
    @pytest.fixture
    def view(
        self,
    ):
        with mock.patch("utils.get_config") as mock_get_config:
            mock_get_config.return_value = {
                "database": {
                    "connection": {
                        "url": "mysql+pymysql://root:admin@192.168.0.100:3306/core",
                    }
                }
            }
            yield views.View()

    def test_fetch_model(
        self,
        mock_bootstrap: mock.MagicMock,
        mock_bus: mock.MagicMock,
        view: core.View,
    ):
        # arrange
        mock_bootstrap.return_value = mock_bus
        mock_bus.uow.repo.get.return_value = [fake.Model(name="test")]
        # act
        with view.fetch_model(fake.Model, id=1) as model:
            assert model is not None

    def test_fetch_models(
        self,
        mock_component_factory: mock.MagicMock,
        mock_session: mock.MagicMock,
        view: core.View,
    ):
        # act
        with view.fetch_models(fake.Model) as models:
            assert models is not None
            # assert
            mock_session.core_session.query.assert_called_once()
