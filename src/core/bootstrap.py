__all__ = ["Bootstrapper"]
import os
from typing import Callable, NewType, NoReturn

import pydantic
import utils

import core
import core.dependency_injection
from core.adapters import orm

CommandRouter = NewType(
    "CommandRouter", dict[type[core.Command], Callable[..., NoReturn]]
)

EventRouter = NewType(
    "EventRouter", dict[type[core.Event], list[Callable[..., NoReturn]]]
)


class Bootstrapper(pydantic.BaseModel):
    use_orm: bool = False
    command_router: CommandRouter = pydantic.Field(default_factory=dict)
    event_router: EventRouter = pydantic.Field(default_factory=dict)
    dependencies: dict[str, Callable[..., NoReturn]] = {}

    # @property
    # def use_orm(self):
    #     return self._use_orm

    # @use_orm.setter
    # def use_orm(
    #     self,
    #     new_use_orm: bool,
    # ):
    #     self._use_orm = new_use_orm

    # @property
    # def command_router(self) -> CommandRouter:
    #     return self._command_router

    # @command_router.setter
    # def command_router(
    #     self,
    #     new_command_router: CommandRouter,
    # ):
    #     self._command_router = new_command_router

    # @property
    # def event_router(self) -> EventRouter:
    #     return self._event_router

    # @event_router.setter
    # def event_router(self, new_event_router: dict[type, list[Callable[..., NoReturn]]]):
    #     self._event_router = new_event_router

    # @property
    # def dependencies(self):
    #     return self._dependencies

    # @dependencies.setter
    # def dependencies(self, new_dependencies: dict[str, Callable[..., NoReturn]]):
    #     self._dependencies = new_dependencies

    def setup_dependencies(self):
        for name, dependency in self._dependencies.items():
            setattr(self, name, dependency)

    def bootstrap(self) -> core.MessageBus:
        # Load config
        config_path = os.environ.get("CONFIG_PATH", "/etc/config")
        config = utils.load_config(config_path)

        # Setup dependencies
        uow = core.UnitOfWork(config["database"])
        object_store = data_store.ObjectStore(config["data_store"])
        dependencies = {
            "uow": uow,
            "object_store": object_store,
        }
        command_handler_router = self.command_router
        event_handler_router = self.event_router
        injected_command_handlers = {
            command_type: core.dependency_injection.inject_dependencies(
                handler, dependencies
            )
            for command_type, handler in command_handler_router.items()
        }
        injected_event_handlers = {
            event_type: [
                core.dependency_injection.inject_dependencies(handler, dependencies)
                for handler in handlers
            ]
            for event_type, handlers in event_handler_router.items()
        }
        bus = core.MessageBus(uow, injected_command_handlers, injected_event_handlers)
        return bus

def boostrap():
    ...