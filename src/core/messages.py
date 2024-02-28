import uuid
from datetime import UTC, datetime

import pydantic


class Message(pydantic.BaseModel):
    _id: str = pydantic.PrivateAttr(default_factory=lambda: str(uuid.uuid4()))
    _created_time: datetime = pydantic.PrivateAttr(
        default_factory=lambda: datetime.now(UTC)
    )


class Command(Message):
    pass


class Event(Message):
    pass
