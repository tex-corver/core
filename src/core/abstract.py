from __future__ import annotations

import abc
from collections.abc import Callable
from typing import Any

from core import models


class Engine(abc.ABC):
    """
    Abstract base class for creating and managing a database engine.
    """


def return_model(query_func: Callable[..., list[models.BaseModel]]):
    """Decorator for ensuring that the query function always return model"""

    def _return_model(*args, **kwargs):
        models = query_func(*args, **kwargs)
        for model in models:
            if not hasattr(model, "events"):
                setattr(model, "events", [])

        many = kwargs.get("many", False)
        if many:
            return models

        return models[0] if len(models) > 0 else None

    return _return_model


def return_list(query_func: Callable[..., Any]):
    """Decorator that ensures the query function always returns a list"""

    def _return_list(*args, **kwargs):
        models = query_func(*args, **kwargs)
        return models or []

    return _return_list


class Repository(abc.ABC):
    def __init__(self):
        self.cached: dict[Any, models.BaseModel] = {}

    def cache(self, models: list[models.BaseModel]):
        for model in models:
            model_id = getattr(model, "id")
            self.cached[model_id] = model

    def add(
        self,
        models: list[models.BaseModel] | models.BaseModel,
        *args,
        **kwargs,
    ):
        if not isinstance(models, list):
            models = [models]
        self._add(models, *args, **kwargs)
        self.cache(models)

    def get(
        self,
        model_class: type[models.BaseModel],
        many: bool = False,
        **identities,
    ) -> list[models.BaseModel] | models.BaseModel | None:
        models = self._get(model_class, **identities)
        self.cache(models)
        if many:
            return models or []

        return models[0] if len(models) > 0 else None

    def filter(self, model_class: type[models.BaseModel], *args, **kwargs):
        models = self._filter(model_class, *args, **kwargs)
        self.cache(models)
        return models

    def remove(self, model: models.BaseModel, *args, **kwargs):
        return self._remove(model, *args, **kwargs)

    @abc.abstractmethod
    def _get(
        self,
        model_class: type[models.BaseModel],
        **identities,
    ) -> list[models.BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(
        self,
        models: list[models.BaseModel],
        *args,
        **kwargs,
    ) -> list[models.BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(
        self,
        model: models.BaseModel,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _filter(
        self,
        model_class: type[models.BaseModel],
        *args,
        **kwargs,
    ) -> list[models.BaseModel]:
        raise NotImplementedError


class Session(abc.ABC):
    def create_repository(self, *args, **kwargs):
        repo = self._create_repository(*args, **kwargs)
        return repo

    def commit(self):
        self._commit()

    def rollback(self):
        self._rollback()

    def close(self):
        self._close()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _close(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _create_repository(self, *args, **kwargs) -> Repository:
        raise NotImplementedError


class ComponentFactory(abc.ABC):
    @abc.abstractmethod
    def create_session(self, *args, **kwargs) -> Session:
        raise NotImplementedError

    @abc.abstractmethod
    def create_repository(self, *args, **kwargs) -> Repository:
        raise NotImplementedError
