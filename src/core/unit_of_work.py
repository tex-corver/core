from typing import Any

import utils

from core import abstract, adapters


class UnsupportedDatabaseFrameworkException(Exception):
    """UnsupportedDatabaseFrameworkException."""


class UnitOfWork:
    """UnitOfWork."""

    repo: abstract.Repository | None = None
    factory: abstract.ComponentFactory
    session: abstract.Session | None = None

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or utils.get_config()
        self.factory = adapters.create_component_factory(self.config)

    def __enter__(self):
        """
        Enters the unit of work context.

        Returns:
            SqlAlchemyUnitOfWork: The current instance of the unit of work.
        """
        self.session = self.factory.create_session()
        self.repo = self.factory.create_repository(session=self.session)
        return self

    def __exit__(self, *_):
        """
        Exits the unit of work context.

        Args:
            *args: A variable-length list of positional arguments.
        """
        if self.session:
            self.session.close()

    def commit(self):
        """
        Commits the session's transaction.
        """
        if self.session:
            self.session.commit()

    def rollback(self):
        """
        Rollback the session's transaction.
        """
        if self.session:
            self.session.rollback()

    def collect_event(self):
        """collect_event."""
        if self.repo is None:
            return

        for model in self.repo.cached.values():
            while model.events:
                yield model.events.pop(0)
