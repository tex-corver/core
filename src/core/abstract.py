from __future__ import annotations
import abc
from collections.abc import Callable

from . import messages, models


class Engine(abc.ABC):
    pass


class Repository(abc.ABC):
    def __init__(self, *args, **kwargs):
        self.cached: dict[any, models.BaseModel] = {}

    def return_model(query_function: Callable[..., list[models.BaseModel]]):
        def _return_model(*args, **kwargs):
            models: list[models.BaseModel] = query_function(*args, **kwargs)
            for model in models:
                if not hasattr(model, "events"):
                    setattr(model, "events", [])
                many = kwargs.get("many", False)
                if many:
                    return models
                return models[0] if len(models) > 0 else None

        return _return_model

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

    @return_model
    def get(
        self,
        model_class: type[models.BaseModel],
        many: bool = False,
        **identities,
    ) -> list[models.BaseModel] | models.BaseModel | None:
        models = self._get(model_class, **identities)
        self.cache(models)
        return models

    @abc.abstractmethod
    def _get(
        self, model_class: type[models.BaseModel], **identities
    ) -> list[models.BaseModel]:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(
        self, models: list[models.BaseModel], *args, **kwargs
    ) -> list[models.BaseModel]:
        raise NotADirectoryError


class Session(abc.ABC):
    def create_repository(self, *args, **kwargs):
        repo = self._create_repository(*args, **kwargs)
        return repo

    def commit(self):
        self._commit()

    def rollback(self):
        self._rollback()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _rollback(self):
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
