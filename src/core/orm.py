import logging
from collections.abc import Callable

import utils

logger = logging.getLogger(__file__)
config = utils.get_config()
mapped_orm: bool = False


def map_once(mapper_function: Callable):
    def _start_mappers(*args, **kwargs):
        global mapped_orm
        if mapped_orm:
            logger.warning("ORM already mapped, skipping")
            return

        mapped_orm = True
        return mapper_function(*args, **kwargs)

    return _start_mappers
