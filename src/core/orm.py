# pylint: disable=global-statement
from collections.abc import Callable

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
