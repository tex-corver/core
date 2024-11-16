from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime
from typing import Any, override

from core import messages


def is_serializable(field: str):
    if field.startswith("_"):
        return False
    if field == "events":
        return False
    return True


@dataclasses.dataclass
class BaseModel:
    """BaseModel."""

    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    created_time: datetime = dataclasses.field(default_factory=datetime.now)
    updated_time: datetime = dataclasses.field(default_factory=datetime.now)
    events: list[messages.Event] = dataclasses.field(default_factory=list)
    message_id: str | None = None
    ignore_keys: set[str] = dataclasses.field(default_factory=lambda: {"password"})

    _immutable_atributes: set[str] = dataclasses.field(
        default_factory=lambda: {"id", "created_time"}
    )
    _datetime_format: str = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def immutable_atributes(cls):
        """immutable_atributes."""
        return cls._immutable_atributes

    def update(self, **kwargs):
        """update.

        Args:
            kwargs:
        """
        for key, value in kwargs.items():
            if key in self._immutable_atributes:
                continue

            setattr(self, key, value)

    @property
    def json(self):
        """json."""
        data = {
            key: val
            for key, val in self.__dict__.items()
            if key not in self.ignore_keys and is_serializable(key)
        }
        return BaseModel.dict_json(data)

    @override
    def __repr__(self) -> str:
        dict_str = ", ".join(f"{key}: {value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({dict_str})"

    def load_from_database(self):
        """load_from_database."""
        self.events = []
        self._immutable_atributes = set()

    # TODO: Implement a serializer class
    @classmethod
    def list_json(cls, l: list[Any]) -> list[dict[str, Any]]:
        """model_list_json.
        Assume all element has same type."""
        if len(l) == 0:
            return []
        if isinstance(l[0], BaseModel):
            return [item.json for item in l]
        return l

    @classmethod
    def dict_json(cls, d: dict[str, Any]) -> dict[str, Any]:
        for attr, value in d.items():
            if isinstance(value, datetime):
                d[attr] = value.strftime(cls._datetime_format)
            if isinstance(value, set):
                d[attr] = list(value)
            if isinstance(value, list):
                d[attr] = BaseModel.list_json(value)
            if isinstance(value, BaseModel):
                d[attr] = value.json
            if isinstance(value, dict):
                d[attr] = BaseModel.dict_json(value)
        return d
