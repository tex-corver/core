import logging
from typing import Any

import utils
from utils import creational

from core import abstract, adapters

logger = logging.getLogger(__file__)


class UnsupportedDatabaseFrameworkException(Exception):
    pass


@creational.singleton
class UnitOfWork:
    repo: abstract.Repository
    factory: abstract.ComponentFactory
    session: abstract.Session

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
        self.session.close()

    def commit(self):
        """
        Commits the session's transaction.
        """
        self.session.commit()

    def rollback(self):
        """
        Rollback the session's transaction.
        """
        self.session.rollback()

    def collect_event(self):
        for model in self.repo.cached.values():
            while model.events:
                yield model.events.pop(0)
