from __future__ import annotations

import logging
from typing import Any

import sqlalchemy
from sqlalchemy import orm as sqlalchemy_orm

from core import abstract, models

logger = logging.getLogger(__file__)


class Session(abstract.Session):
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
        repo = Repository(self)
        return repo


class Repository(abstract.Repository):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session._core_session

    def _add(
        self, models: list[models.BaseModel], *args, **kwargs
    ) -> list[models.BaseModel]:
        self.session.add_all(models)
        return models

    @abstract.return_list
    def _get(
        self,
        model_class: type[models.BaseModel],
        **identities,
    ) -> list[models.BaseModel]:
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
        model_class: type[models.BaseModel],
        *args,
        **kwargs,
    ) -> list[models.BaseModel]:
        models = self.session.query(model_class).filter(*args).all()
        return models

    def _remove(self, model: models.BaseModel, *args, **kwargs):
        table = type(model)
        self.session.execute(
            sqlalchemy.delete(table).where(getattr(table, "id") == getattr(model, "id"))
        )


class SessionFactory:
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
        core_session = self.__core_factory()
        session = Session(_core_session=core_session, *args, **kwargs)
        return session


class Database:
    def __init__(self, engine: sqlalchemy.engine.Engine) -> None:
        self.engine = engine
        self.cached: dict[str, set] = {}

    def get(self, table: str, id: str):
        with self.engine.connect() as conn:
            if table not in self.cached:
                self.cached[table] = set()
            self.cached[table].add(id)
            stm = sqlalchemy.text(f'SELECT * FROM {table} WHERE id = "{id}";')
            model = conn.execute(stm).mappings().fetchone()
            return model

    def remove(self, table: str, id: str):
        with self.engine.connect() as conn:
            conn.execute(sqlalchemy.text(f'DELETE FROM {table} WHERE id = "{id}";'))

    def clear(self):
        for table, models_ids in self.cached.items():
            for id in models_ids:
                self.remove(table, id)


class ComponentFactory(abstract.ComponentFactory):
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.session_factory = SessionFactory(**config["connection"])

    def create_engine(self):
        engine = sqlalchemy.create_engine(**self.config["connection"])
        return engine

    def create_session(self, *args, **kwargs) -> Session:
        session = self.session_factory.create_session(*args, **kwargs)
        return session

    def create_repository(self, session: Session | None = None, *args, **kwargs):
        session = session or self.create_session()
        repo = Repository(session)
        return repo

    def create_metadata(self) -> sqlalchemy.MetaData:
        metadata = sqlalchemy.MetaData()
        return metadata

    def create_orm_registry(self) -> sqlalchemy_orm.registry:
        registry = sqlalchemy_orm.registry()
        return registry
