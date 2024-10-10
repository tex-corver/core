from typing import Any, Generator
from unittest import mock

import pytest
import utils
from icecream import ic

import core
from core import adapters, models, views
from tests.double import fake

logger = utils.get_logger()


class TestMessageBus:
    def test_init(
        self,
        bus: core.MessageBus,
    ):
        assert bus

    def test_handle(
        self,
        bus: core.MessageBus,
    ):
        command = fake.CreateModelCommand(name="test")
        bus.handle(command)

        model = views.fetch_model(fake.Model, message_id=command._id)

        assert model
        assert model.name == "test"

    def test_handle_error_command(
        self,
        bus: core.MessageBus,
    ):
        command = fake.CreateModelErrorCommand(name="test")
        with pytest.raises(
            ValueError, match="Error while handling create model command"
        ):
            bus.handle(command)

        model = views.fetch_model(fake.Model, message_id=command._id)

        assert not model
