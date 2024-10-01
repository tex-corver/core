from typing import Any, Generator

import pytest

import core


@pytest.fixture
def uow(config: dict[str, Any]) -> Generator[core.UnitOfWork, Any, None]:
    uow = core.UnitOfWork(config["database"])
    yield uow
