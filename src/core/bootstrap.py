from __future__ import annotations
import os
from typing import Callable, NewType, NoReturn

import pydantic
import utils
from utils import creational

import core.dependency_injection
from core import message_bus, messages

__all__ = [
    "Bootstrapper",
    "CommandRouter",
    "EventRouter",
    "Dependencies",
]

CommandRouter = NewType(
    "CommandRouter", dict[type[messages.Command], Callable[..., NoReturn]]
)

EventRouter = NewType(
    "EventRouter", dict[type[messages.Event], list[Callable[..., NoReturn]]]
)

Dependencies = NewType("Dependencies", dict[str, object])

BOOTSTRAPPER: Bootstrapper = None


# @creational.singleton
class Bootstrapper(pydantic.BaseModel):
    use_orm: bool = False
    orm_func: Callable[..., NoReturn] = None
    command_router: CommandRouter = pydantic.Field(default_factory=dict)
    event_router: EventRouter = pydantic.Field(default_factory=dict)
    dependencies: dict[str, object] = pydantic.Field(default_factory=dict)
    _injected_command_handlers: dict[
        type[messages.Command], Callable[..., NoReturn]
    ] = pydantic.PrivateAttr(default_factory=dict)
    _injected_event_handlers: dict[
        type[messages.Event], list[Callable[..., NoReturn]]
    ] = pydantic.PrivateAttr(default_factory=dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_orm()
        self._injected_command_handlers = self.inject_command_handlers()
        self._injected_event_handlers = self.inject_event_handlers()
        global BOOTSTRAPPER
        BOOTSTRAPPER = self

    def start_orm(self):
        if self.use_orm:
            if self.orm_func is None:
                raise ValueError("ORM function is required when use_orm is True")
            self.orm_func()

    def inject_command_handlers(self):
        injected_command_handlers = {
            command_type: core.dependency_injection.inject_dependencies(
                handler,
                self.dependencies,
            )
            for command_type, handler in self.command_router.items()
        }
        return injected_command_handlers

    def inject_event_handlers(self):
        injected_event_handlers = {
            event_type: [
                core.dependency_injection.inject_dependencies(
                    handler,
                    self.dependencies,
                )
                for handler in handlers
            ]
            for event_type, handlers in self.event_router.items()
        }
        return injected_event_handlers

    def bootstrap(self) -> message_bus.MessageBus:
        # Setup dependencies
        bus = message_bus.MessageBus(
            self.dependencies["uow"],
            self._injected_command_handlers,
            self._injected_event_handlers,
        )
        return bus


def get_bootstrapper() -> Bootstrapper:
    global BOOTSTRAPPER
    return BOOTSTRAPPER


def set_bootstrapper(bootstrapper: Bootstrapper):
    global BOOTSTRAPPER
    BOOTSTRAPPER = bootstrapper


def bootstrap() -> message_bus.MessageBus:
    global BOOTSTRAPPER
    if BOOTSTRAPPER is None:
        raise ValueError("Bootstrapper is not set")
    return BOOTSTRAPPER.bootstrap()
