__all__ = [
    "ModelSchema",
    "CreateModelCommand",
    "CreatedModelEvent",
    "CreateModelErrorCommand",
    "CreatedModelErrorEvent",
]
import pydantic

import core


class ModelSchema(pydantic.BaseModel):
    model_config: pydantic.ConfigDict = pydantic.ConfigDict(from_attributes=True)


class CreateModelCommand(core.Command):
    name: str


class CreatedModelEvent(core.Event):
    model: ModelSchema


class CreateModelErrorCommand(core.Command):
    name: str


class CreatedModelErrorEvent(core.Event):
    model: ModelSchema
