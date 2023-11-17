import logging
import os

from core import abstract, adapters, messages
import utils
from utils import creational

logger = logging.getLogger(__file__)


@creational.singleton
class UnitOfWork:
    repo: abstract.Repository

    def __init__(self, config: dict[str, any] = None, *args, **kwargs):
        if config is None:
            config = utils.get_config()
        self.config = config
        self.factory = adapters.create_component_factory()

    def __enter__(self):
        """
        Enters the unit of work context.

        Returns:
            SqlAlchemyUnitOfWork: The current instance of the unit of work.
        """
        self.session = self.factory.create_session()
        self.repo = self.factory.create_repository(session=self.session)
        return self

    def __exit__(self, *args):
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
