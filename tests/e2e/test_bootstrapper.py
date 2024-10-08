from typing import Any, Generator
from unittest import mock

import pytest
import utils
from icecream import ic

import core
from core import adapters, models
from tests.double import fake

logger = utils.get_logger()


class TestBootstrapper:
    def test_init(self, bootstrapper: core.Bootstrapper):
        bootstrapper

    def test_bootstrap(self, bootstrapper: core.Bootstrapper):
        bus = bootstrapper.bootstrap()
        assert isinstance(bus, core.MessageBus)
        assert bus.command_handlers == bootstrapper._injected_command_handlers
        assert bus.event_handlers == bootstrapper._injected_event_handlers
