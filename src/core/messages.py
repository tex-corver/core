import dataclasses
import re
from datetime import datetime


@dataclasses.dataclass
class Message:
    def __post_init__(self):
        self.name = "_".join(re.split("(?=[A-Z])", self.__class__.__name__))
        self.created_date = datetime.utcnow()


@dataclasses.dataclass
class Command(Message):
    pass


@dataclasses.dataclass
class Event(Message):
    pass
