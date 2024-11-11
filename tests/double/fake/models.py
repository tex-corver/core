__all__ = [
    "Model",
]

import core
from tests.double.fake import schemas


class Model(core.BaseModel):
    name: str
    password: str

    def __init__(
        self,
        name: str,
        password: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.password = password
        self.events.append(schemas.CreatedModelEvent(model=self))
