# pylint: disable=global-statement
import json
from collections.abc import Callable
from typing import Any

from sqlalchemy import Text, types

MAPPED_ORM: bool = False


def map_once(mapper_function: Callable[..., None]):
    """map_once.

    Args:
        mapper_function (Callable): mapper_function
    """

    def _start_mappers(*args, **kwargs):
        global MAPPED_ORM
        if MAPPED_ORM:
            return None

        MAPPED_ORM = True
        return mapper_function(*args, **kwargs)

    return _start_mappers


class PyDict(types.TypeDecorator):
    impl = Text

    def process_bind_param(self, value: dict[Any, Any], dialect) -> str | None:
        if value is not None:
            value_str: str = json.dumps(value)
            return value_str
        return None

    def process_result_value(self, value: str, dialect) -> dict[Any, Any]:
        if value is not None:
            value = json.loads(value)
        return value


class PyList(types.TypeDecorator):
    impl = Text

    def process_bind_param(self, value: list[Any], dialect) -> str:
        if value is not None:
            value = "| ".join([item.model_dump() for item in value])
        return value

    def process_result_value(self, value: str, dialect) -> list[Any]:
        if value is not None:
            value = value.split("| ")
        return value
