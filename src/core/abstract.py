from __future__ import annotations

import abc
from collections.abc import Callable
from typing import Any

from core import models as base_model


class Engine(abc.ABC):
    """
    Abstract base class for creating and managing a database engine.
    """


def return_model(query_func: Callable[..., list[base_model.BaseModel]]):
    """Decorator for ensuring that the query function always return model"""

    def _return_model(*args, **kwargs):
        """_return_model.

        Args:
            args:
            kwargs:
        """
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
        """_return_list.

        Args:
            args:
            kwargs:
        """
        models = query_func(*args, **kwargs)
        return models or []

    return _return_list


class Repository(abc.ABC):
    """Repository."""

    def __init__(self):
        self.cached: dict[Any, base_model.BaseModel] = {}

    def cache(self, models: list[base_model.BaseModel]):
        """cache.

        Args:
            models (list[base_model.BaseModel]): models
        """
        for model in models:
            model_id = getattr(model, "id")
            self.cached[model_id] = model

    def add(
        self,
        models: list[base_model.BaseModel] | base_model.BaseModel,
        *args,
        **kwargs,
    ):
        """add.

        Args:
            models (list[base_model.BaseModel] | base_model.BaseModel): models
            args:
            kwargs:
        """
        if not isinstance(models, list):
            models = [models]
        self._add(models, *args, **kwargs)
        self.cache(models)

    def get(
        self,
        model_class: type[base_model.BaseModel],
        many: bool = False,
        **identities,
    ) -> list[base_model.BaseModel] | base_model.BaseModel | None:
        """get.

        Args:
            model_class (type[base_model.BaseModel]): model_class
            many (bool): many
            identities:

        Returns:
            list[base_model.BaseModel] | base_model.BaseModel | None:
        """
        models = self._get(model_class, **identities)
        self.cache(models)
        if many:
            return models or []

        return models[0] if len(models) > 0 else None

    def filter(self, model_class: type[base_model.BaseModel], *args, **kwargs):
        """filter.

        Args:
            model_class (type[base_model.BaseModel]): model_class
            args:
            kwargs:
        """
        models = self._filter(model_class, *args, **kwargs)
        self.cache(models)
        return models

    def remove(self, model: base_model.BaseModel, *args, **kwargs):
        """remove.

        Args:
            model (base_model.BaseModel): model
            args:
            kwargs:
        """
        return self._remove(model, *args, **kwargs)

    @abc.abstractmethod
    def _get(
        self,
        model_class: type[base_model.BaseModel],
        **identities,
    ) -> list[base_model.BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(
        self,
        models: list[base_model.BaseModel],
        *args,
        **kwargs,
    ) -> list[base_model.BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(
        self,
        model: base_model.BaseModel,
        *args,
        **kwargs,
    ):
        raise NotImplementedError

    @abc.abstractmethod
    def _filter(
        self,
        model_class: type[base_model.BaseModel],
        *args,
        **kwargs,
    ) -> list[base_model.BaseModel]:
        raise NotImplementedError


class Session(abc.ABC):
    """Session."""

    def create_repository(self, *args, **kwargs):
        """create_repository.

        Args:
            args:
            kwargs:
        """
        repo = self._create_repository(*args, **kwargs)
        return repo

    def commit(self):
        """commit."""
        self._commit()

    def rollback(self):
        """rollback."""
        self._rollback()

    def close(self):
        """close."""
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
    """ComponentFactory."""

    @abc.abstractmethod
    def create_session(self, *args, **kwargs) -> Session:
        """create_session.

        Args:
            args:
            kwargs:

        Returns:
            Session:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_repository(self, *args, **kwargs) -> Repository:
        """create_repository.

        Args:
            args:
            kwargs:

        Returns:
            Repository:
        """
        raise NotImplementedError
