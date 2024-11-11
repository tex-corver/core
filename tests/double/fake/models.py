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
        self.ignore_keys = set(["pin"])
        self.events.append(schemas.CreatedModelEvent(model=self))
