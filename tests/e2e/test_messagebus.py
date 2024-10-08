from typing import Any, Generator
from unittest import mock

import pytest
import utils
from icecream import ic

import core
from core import adapters, models
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
