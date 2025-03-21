from __future__ import annotations

import abc
from typing import Any, Generic, TypeVar, Type

from core.configurations import DatabaseConfig
from core.models import BaseModel


T = TypeVar("T", bound=BaseModel)


class Repository(abc.ABC):
    """Repository."""

    def __init__(self):
        self.cached: dict[Any, T] = {}

    def cache(self, models: list[T]):
        """cache.

        Args:
            models (list[T]): models
        """
        for model in models:
            model_id = model.id
            self.cached[model_id] = model

    def add(
        self,
        models: list[T] | T,
        *args,
        **kwargs,
    ):
        """add.

        Args:
            models (list[T] | T): models
            args:
            kwargs:
        """
        if not isinstance(models, list):
            models = [models]

        self._add(models, *args, **kwargs)
        self.cache(models)

    def get(
        self,
        model_cls: Type[T],
        **identities,
    ) -> list[T]:
        """get.

        Args:
            model_cls (type[T]): model_class
            many (bool): many
            identities:

        Returns:
            list[T] | T | None:
        """
        models = self._get(model_cls, **identities)
        self.cache(models)
        return models

    def get_model(self, model_cls: Type[T], **identities) -> T | None:
        model = self._get(model_cls, **identities)
        if len(model) == 0:
            return None
        return model[0]

    def get_models(self, model_cls: Type[T], **identities) -> list[T]:
        models = self._get(model_cls, **identities)
        self.cache(models)
        return models

    def remove(self, model: T, *args, **kwargs):
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
        model_cls: Type[T],
        **identities,
    ) -> list[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(
        self,
        models: list[T],
        *args,
        **kwargs,
    ) -> list[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(
        self,
        model: T,
        *args,
        **kwargs,
    ):
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

    config_cls: Type[DatabaseConfig] = DatabaseConfig

    def __init__(self, config: dict[str, Any] | DatabaseConfig):
        if isinstance(config, dict):
            self.config = self.config_cls(**config)
        else:
            assert isinstance(config, self.config_cls)
            self.config = config

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
