from __future__ import annotations

from typing import Any, override, TypeVar, Type

import sqlalchemy
from sqlalchemy import orm as sqlalchemy_orm

from core import abstract
from core import models as base_models

__all__ = [
    "Session",
    "ComponentFactory",
    "Repository",
]

T = TypeVar("T", bound=base_models.BaseModel)


class Session(abstract.Session):
    """Session."""

    def __init__(
        self,
        core_session: sqlalchemy_orm.Session,
        *args,
        **kwargs,
    ):
        self.__core_session = core_session
        super().__init__(*args, **kwargs)

    @property
    def core_session(self) -> sqlalchemy_orm.Session:
        """Getter method for core_session property."""
        return self.__core_session

    @core_session.setter
    def core_session(self, core_session: sqlalchemy_orm.Session):
        """Setter method for core_session property."""
        self.__core_session = core_session

    @override
    def _close(self):
        self.__core_session.close()

    @override
    def _commit(self):
        self.__core_session.commit()

    @override
    def _rollback(self):
        self.__core_session.rollback()

    @override
    def _create_repository(self, *args, **kwargs) -> Repository:
        repo = Repository(self, *args, **kwargs)
        return repo


class Repository(abstract.Repository):
    """Repository."""

    def __init__(self, session: Session):
        super().__init__()
        self.session = session.core_session

    @override
    def _add(
        self,
        models: list[T],
        *args,
        **kwargs,
    ) -> list[T]:
        self.session.add_all(models, *args, **kwargs)
        return models

    @override
    def _get(
        self,
        model_class: Type[T],
        **identities,
    ) -> list[T]:
        return self.session.query(model_class).filter_by(**identities).all()

    @override
    def _remove(self, model: T, *args, **kwargs):
        self.session.delete(model, *args, **kwargs)


class SessionFactory:
    """SessionFactory."""

    def __init__(
        self,
        engine: sqlalchemy.engine.Engine,
        **kwargs,
    ):
        self.engine = engine
        self.core_factory = sqlalchemy_orm.sessionmaker(
            bind=engine, expire_on_commit=False, **kwargs
        )

    def create_session(self, *args, **kwargs) -> Session:
        """create_session.

        Args:
            args:
            kwargs:

        Returns:
            Session:
        """
        core_session = self.core_factory()
        session = Session(core_session, *args, **kwargs)
        return session


class Database:
    """Database."""

    def __init__(self, engine: sqlalchemy.engine.Engine) -> None:
        self.engine = engine
        self.cached: dict[str, set[str]] = {}

    def get(self, table: str, model_id: str):
        """get.

        Args:
            table (str): table
            model_id (str): model_id
        """
        with self.engine.connect() as conn:
            if table not in self.cached:
                self.cached[table] = set()
            self.cached[table].add(model_id)
            stm = sqlalchemy.text(f'SELECT * FROM {table} WHERE id = "{model_id}";')
            model = conn.execute(stm).mappings().fetchone()
            return model

    def remove(self, table: str, model_id: str):
        """remove.

        Args:
            table (str): table
            model_id (str): model_id
        """
        with self.engine.connect() as conn:
            conn.execute(
                sqlalchemy.text(f'DELETE FROM {table} WHERE id = "{model_id}";')
            )

    def clear(self):
        """clear."""
        for table, models_ids in self.cached.items():
            for model_id in models_ids:
                self.remove(table, model_id)


class ComponentFactory(abstract.ComponentFactory):
    """ComponentFactory."""

    def __init__(self, config: dict[str, Any]):
        self.engine = sqlalchemy.create_engine(**config["connection"])
        self.session_factory = SessionFactory(self.engine)

    @override
    def create_session(self, *args, **kwargs) -> Session:
        """create_session.

        Args:
            args:
            kwargs:

        Returns:
            Session:
        """
        session = self.session_factory.create_session(*args, **kwargs)
        return session

    @override
    def create_repository(
        self,
        *args,
        session: Session | None = None,
        **kwargs,
    ):
        """create_repository.

        Args:
            session (Session | None): session
            args:
            kwargs:
        """
        session = session or self.create_session()
        repo = Repository(session, *args, **kwargs)
        return repo

    def create_orm_registry(self) -> sqlalchemy_orm.registry:
        """create_orm_registry.

        Args:

        Returns:
            sqlalchemy_orm.registry:
        """
        registry = sqlalchemy_orm.registry()
        return registry
