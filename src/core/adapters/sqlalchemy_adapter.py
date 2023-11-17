from __future__ import annotations
from collections.abc import Callable
import logging
import sqlalchemy
from sqlalchemy import orm as sqlalchemy_orm

import core
from core import models, abstract
from utils import creational

from core.abstract import Repository, Session

logger = logging.getLogger(__file__)


class Engine(abstract.Engine):
    def __init__(
        self,
        url: str = None,
        core_engine: sqlalchemy.engine.Engine = None,
        *args,
        **kwargs,
    ):
        if url is None and core_engine is None:
            raise ValueError("Either url or core_engine must be provided")
        if url is not None:
            core_engine = sqlalchemy.create_engine(url, **kwargs)
        self.__core_engine = core_engine
        super().__init__()

    @property
    def _core_engine(self) -> sqlalchemy.engine.Engine:
        return self.__core_engine

    @_core_engine.setter
    def _core_engine(self, core_engine: sqlalchemy.engine.Engine):
        self.__core_engine = core_engine

    def create_metadata(self) -> sqlalchemy.MetaData:
        metadata = sqlalchemy.MetaData()
        metadata.bind = self._core_engine
        return metadata


def return_list(query_function: Callable[..., list[models.BaseModel]]):
    def _return_list(*args, **kwargs):
        models_ = query_function(*args, **kwargs)
        if models_ is None:
            return []
        return models_

    return _return_list


class Repository(abstract.Repository):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session._core_session

    def _add(
        self, models: list[models.BaseModel], *args, **kwargs
    ) -> list[models.BaseModel]:
        self.session.add_all(models)
        return models

    @return_list
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
        return models_


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

    def close(self):
        self._core_session.close()

    def _commit(self):
        self._core_session.commit()

    def _rollback(self):
        self._core_session.rollback()

    def _create_repository(self, *args, **kwargs) -> Repository:
        repo = Repository(self)
        return repo


class SessionFactory:
    def __init__(
        self,
        url: str = None,
        engine: Engine | sqlalchemy.engine.Engine = None,
        **kwargs,
    ):
        if engine is None:
            if url is None:
                raise ValueError("Either url or engine must be provided")
            engine = Engine(url, **kwargs)
        self.engine = engine
        self.__core_factory = sqlalchemy_orm.sessionmaker(
            bind=engine._core_engine, **kwargs
        )

    @property
    def _core_factory(self) -> sqlalchemy_orm.sessionmaker:
        return self.__core_factory

    @_core_factory.setter
    def _core_factory(self, core_factory: sqlalchemy_orm.sessionmaker):
        self.__core_factory = core_factory

    def create_session(self, *args, **kwargs) -> Session:
        core_session = self.__core_factory()
        session = Session(core_session, *args, **kwargs)
        return session


class ComponentFactory(abstract.ComponentFactory):
    def __init__(self, config: dict[str, any]):
        self.config = config
        self.session_factory = SessionFactory(**config["connection"])

    def create_session(self, *args, **kwargs) -> Session:
        session = self.session_factory.create_session(*args, **kwargs)
        return session

    def create_engine(self) -> Engine:
        engine = Engine(**self.config["connection"])
        return engine

    def create_repository(self, session: Session = None) -> Repository:
        if session is None:
            session = self.create_session()
        repo = session.create_repository(session=session)
        return repo

    def create_metadata(self) -> sqlalchemy.MetaData:
        engine = self.create_engine()
        metadata = engine.create_metadata()
        return metadata

    def create_orm_registry(self) -> sqlalchemy_orm.registry:
        metadata = self.create_metadata()
        registry = sqlalchemy_orm.registry(metadata=metadata)
        return registry
