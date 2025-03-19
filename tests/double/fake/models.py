__all__ = [
    "Model",
    "IgnoreKeysModel",
]

import core
from tests.double.fake import schemas


class Model(core.BaseModel):
    name: str
    password: str

    def __init__(
        self,
        name: str,
        password: str = "password",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.password = password
        self.events.append(schemas.CreatedModelEvent(model=self))

    def __eq__(self, other):
        return self.name == other.name

class IgnoreKeysModel(core.BaseModel):
    name: str
    pin: str

    def __init__(
        self,
        name: str,
        pin: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.pin = pin
        self.events.append(schemas.CreatedModelEvent(model=self))

