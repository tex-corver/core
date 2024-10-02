from __future__ import annotations

from typing import Any, Callable

import utils

from core import messages, unit_of_work

logger = utils.get_logger()


class MessageBus:
    """MessageBus."""

    def __init__(
        self,
        uow: unit_of_work.UnitOfWork,
        command_handlers: dict[
            type[messages.Command],
            Callable[[messages.Command], Any],
        ],
        event_handlers: dict[
            type[messages.Event],
            list[Callable[[messages.Event], Any]],
        ],
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.queue: list[messages.Message] = []
        self.logger = logger

    def handle(self, message: messages.Message):
        """handle.

        Args:
            message (messages.Message): message
        """
        self.queue = [message]
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, messages.Event):
                self.handle_event(message)
            elif isinstance(message, messages.Command):
                self.handle_command(message)
            else:
                raise ValueError(f"{message} was not an Event or Command")

    def handle_event(self, event: messages.Event):
        """handle_event.

        Args:
            event (messages.Event): event
        """
        for handler in self.event_handlers[type(event)]:
            try:
                self.logger.debug(
                    "handling event %s with handler %s",
                    event,
                    handler.__name__,
                )
                handler(event)
                self.queue.extend(self.uow.collect_event())
            except Exception:  # pylint: disable=broad-except
                self.logger.exception(
                    "Exception handling event %s with handler %s",
                    event,
                    handler.__name__,
                )
                continue

    def handle_command(self, command: messages.Command):
        """handle_command.

        Args:
            command (messages.Command): command
        """
        handler = self.command_handlers[type(command)]
        self.logger.debug(
            "handling command %s with handler %s",
            command,
            handler.__name__,
        )
        try:
            handler(command)
            self.queue.extend(self.uow.collect_event())
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Exception handling command %s", command)
            raise
