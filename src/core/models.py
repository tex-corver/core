import dataclasses
import uuid
from datetime import datetime

from . import messages
import utils

@dataclasses.dataclass
class BaseModel:
    id: str = str(uuid.uuid4())
    created_time: datetime = datetime.now()
    updated_time: datetime = datetime.now()
    datetime_format: str = "%Y-%m-%d %H:%M:%S"
    events: list[messages.Event] = None

    def __post_init__(self):
        if self.events is None:
            self.events = []

    @property
    def json(self):
        data = {
            key: val for key, val in self.__dict__.items() if not key.startswith("_")
        }
        for attr, value in data.items():
            if isinstance(value, datetime):
                data[attr] = value.strftime(self.datetime_format)
        return data