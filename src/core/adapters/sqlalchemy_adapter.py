from __future__ import annotations

import logging
from typing import Any

import sqlalchemy
from sqlalchemy import orm as sqlalchemy_orm

from core import abstract, models as base_model

logger = logging.getLogger(__file__)


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
    def _core_session(self) -> sqlalchemy_orm.Session:
        return self.__core_session

    @_core_session.setter
    def _core_session(self, core_session: sqlalchemy_orm.Session):
        self.__core_session = core_session

    def _close(self):
        self._core_session.close()

    def _commit(self):
        self._core_session.commit()

    def _rollback(self):
        self._core_session.rollback()

    def _create_repository(self, *args, **kwargs) -> Repository:
        repo = Repository(self, *args, **kwargs)
        return repo


class Repository(abstract.Repository):
    """Repository."""

    def __init__(self, session: Session):
        super().__init__()
        self.session = session._core_session

    def _add(
        self,
        models: list[base_model.BaseModel],
        *args,
        **kwargs,
    ) -> list[base_model.BaseModel]:
        self.session.add_all(models, *args, **kwargs)
        return models

    @abstract.return_list
    def _get(
        self,
        model_class: type[base_model.BaseModel],
        **identities,
    ) -> list[base_model.BaseModel]:
        models_ = []
        if identities is not None:
            models_ = self.session.scalars(
                sqlalchemy.select(model_class).filter_by(**identities)
            ).all()
        else:
            models_ = self.session.scalars(sqlalchemy.select(model_class)).all()
        return list(models_)

    @abstract.return_list
    def _filter(
        self,
        model_class: type[base_model.BaseModel],
        *args,
        **kwargs,
    ) -> list[base_model.BaseModel]:
        models = self.session.query(model_class).filter(*args, **kwargs).all()
        return models

    def _remove(self, model: base_model.BaseModel, *args, **kwargs):
        table = type(model)
        self.session.execute(
            sqlalchemy.delete(table).where(
                getattr(table, "id") == getattr(model, "id"),
                *args,
                **kwargs,
            )
        )


class SessionFactory:
    """SessionFactory."""

    def __init__(
        self,
        engine: sqlalchemy.engine.Engine,
        **kwargs,
    ):
        self.engine = engine
        self.__core_factory = sqlalchemy_orm.sessionmaker(bind=engine, **kwargs)

    @property
    def _core_factory(self) -> sqlalchemy_orm.sessionmaker:
        return self.__core_factory

    @_core_factory.setter
    def _core_factory(self, core_factory: sqlalchemy_orm.sessionmaker):
        self.__core_factory = core_factory

    def create_session(self, *args, **kwargs) -> Session:
        """create_session.

        Args:
            args:
            kwargs:

        Returns:
            Session:
        """
        core_session = self.__core_factory()
        session = Session(_core_session=core_session, *args, **kwargs)
        return session


class Database:
    """Database."""

    def __init__(self, engine: sqlalchemy.engine.Engine) -> None:
        self.engine = engine
        self.cached: dict[str, set] = {}

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
            conn.execute(sqlalchemy.text(f'DELETE FROM {table} WHERE id = "{model_id}";'))

    def clear(self):
        """clear."""
        for table, models_ids in self.cached.items():
            for model_id in models_ids:
                self.remove(table, model_id)


class ComponentFactory(abstract.ComponentFactory):
    """ComponentFactory."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.session_factory = SessionFactory(**config["connection"])

    def create_engine(self):
        """create_engine."""
        engine = sqlalchemy.create_engine(**self.config["connection"])
        return engine

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

    def create_metadata(self) -> sqlalchemy.MetaData:
        """create_metadata.

        Args:

        Returns:
            sqlalchemy.MetaData:
        """
        metadata = sqlalchemy.MetaData()
        return metadata

    def create_orm_registry(self) -> sqlalchemy_orm.registry:
        """create_orm_registry.

        Args:

        Returns:
            sqlalchemy_orm.registry:
        """
        registry = sqlalchemy_orm.registry()
        return registry
