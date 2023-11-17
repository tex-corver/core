from __future__ import annotations
import logging
import traceback
from typing import Type
import logging

from core import messages, unit_of_work
from utils import creational

logger = logging.getLogger(__file__)


@creational.singleton
class InternalMessageBus:
    def __init__(
        self,
        config: dict[any, any],
        uow: unit_of_work.UnitOfWork,
        command_handlers: dict[Type[messages.Command], callable] = None,
        event_handlers: dict[Type[messages.Event], list[callable]] = None,
        *args,
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
                self.queue.extend(self.uow.collect_new_messages())
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(self, command: messages.Command):
        logger.debug("handling command %s", command)
        try:
            handler = self.command_handlers[type(command)]
            handler(command)
            self.queue.extend(self.uow.collect_new_messages())
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
