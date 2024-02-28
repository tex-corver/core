from __future__ import annotations

import logging
from typing import Any, Callable, Type

from utils import creational

from core import messages, unit_of_work

logger = logging.getLogger(__file__)


@creational.singleton
class MessageBus:
    def __init__(
        self,
        config: dict[Any, Any],
        uow: unit_of_work.UnitOfWork,
        command_handlers: dict[Type[messages.Command], Callable],
        event_handlers: dict[Type[messages.Event], list[Callable]],
        **dependencies,
    ):
        self.config = config
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        for name, dependency in dependencies.items():
            setattr(self, name, dependency)

    def handle(self, message: messages.Message):
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, messages.Event):
                self.handle_event(message)
            elif isinstance(message, messages.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

    def handle_event(self, event: messages.Event):
        for handler in self.event_handlers[type(event)]:
            try:
                logger.debug("handling event %s", event)
                handler(event)
                self.queue.extend(self.uow.collect_event())
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(self, command: messages.Command):
        logger.debug("handling command %s", command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_event())
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
