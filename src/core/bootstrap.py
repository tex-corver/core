__all__ = [
    "Bootstrapper",
    "CommandRouter",
    "EventRouter",
    "Dependencies",
]
import os
from typing import Callable, NewType, NoReturn

import pydantic
import utils

import core
import core.dependency_injection

CommandRouter = NewType(
    "CommandRouter", dict[type[core.Command], Callable[..., NoReturn]]
)

EventRouter = NewType(
    "EventRouter", dict[type[core.Event], list[Callable[..., NoReturn]]]
)

Dependencies = NewType("Dependencies", dict[str, object])


class Bootstrapper(pydantic.BaseModel):
    use_orm: bool = False
    orm_func: Callable[..., NoReturn] = None
    command_router: CommandRouter = pydantic.Field(default_factory=dict)
    event_router: EventRouter = pydantic.Field(default_factory=dict)
    dependencies: dict[str, Callable[..., NoReturn]] = pydantic.Field(
        default_factory=dict
    )
    _injected_command_handlers: dict[type[core.Command], Callable[..., NoReturn]] = (
        pydantic.PrivateAttr(default_factory=dict)
    )
    _injected_event_handlers: dict[type[core.Event], list[Callable[..., NoReturn]]] = (
        pydantic.PrivateAttr(default_factory=dict)
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_orm()
        self._injected_command_handlers = self.inject_command_handlers()
        self._injected_event_handlers = self.inject_event_handlers()

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

    def bootstrap(self) -> core.MessageBus:
        # Setup dependencies
        bus = core.MessageBus(
            self.dependencies["uow"],
            self._injected_command_handlers,
            self._injected_event_handlers,
        )
        return bus

BOOTSTRAPPER: Bootstrapper = None

def get_bootstrapper() -> Bootstrapper:
    global BOOTSTRAPPER
    return BOOTSTRAPPER

def set_bootstrapper(bootstrapper: Bootstrapper):
    global BOOTSTRAPPER
    BOOTSTRAPPER = bootstrapper

def bootstrap() -> core.MessageBus:
    global BOOTSTRAPPER
    if BOOTSTRAPPER is None:
        raise ValueError("Bootstrapper is not set")
    return BOOTSTRAPPER.bootstrap()