import dataclasses
import uuid
from datetime import datetime
from typing import override

from core import messages


@dataclasses.dataclass
class BaseModel:
    """BaseModel."""

    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    created_time: datetime = dataclasses.field(default_factory=datetime.now)
    updated_time: datetime = dataclasses.field(default_factory=datetime.now)
    events: list[messages.Event] = dataclasses.field(default_factory=list)
    message_id: str | None = None

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
        data = {key: val for key, val in self.__dict__.items() if not key.startswith("_")}
        for attr, value in data.items():
            if isinstance(value, datetime):
                data[attr] = value.strftime(self._datetime_format)
            if isinstance(value, set):
                data[attr] = list(value)
        return data

    @override
    def __repr__(self) -> str:
        dict_str = ", ".join(f"{key}: {value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({dict_str})"

    def load_from_database(self):
        """load_from_database."""
        self.events = []
        self._immutable_atributes = set()
