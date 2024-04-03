import inspect
from typing import Any, Callable


def inject_dependencies(
    handler: Callable[..., None],
    dependencies: dict[str, Any],
):
    """inject_dependencies.

    Args:
        handler (Callable[..., None]): handler
        dependencies (dict[str, Any]): dependencies
    """
    params = inspect.signature(handler).parameters
    deps = {name: dependency for name, dependency in dependencies.items() if name in params}

    return lambda message: handler(message, **deps)
