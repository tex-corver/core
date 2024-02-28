import inspect
from typing import Any, Callable


def inject_dependencies(
    handler: Callable[..., None],
    dependencies: dict[str, Any],
):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }

    return lambda message: handler(message, **deps)
