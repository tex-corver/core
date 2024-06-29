# pylint: disable=global-statement
from collections.abc import Callable

mapped_orm: bool = False


def map_once(mapper_function: Callable[..., None]):
    """map_once.

    Args:
        mapper_function (Callable): mapper_function
    """

    def _start_mappers(*args, **kwargs):
        global mapped_orm
        if mapped_orm:
            return None

        mapped_orm = True
        return mapper_function(*args, **kwargs)

    return _start_mappers
