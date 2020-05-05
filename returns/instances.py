from returns.context import (
    ContextIOResult,
    ContextResult,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import FutureResult
from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer
from returns.result import Result


def is_io(container: BaseContainer) -> bool:
    """
    Verifies if a container is ``IO`` type.

    .. code:: python

      >>> from returns.io import IO
      >>> from returns.result import Success

      >>> assert is_io(IO(1.0)) is True
      >>> assert is_io(Success(1.0)) is False

    """
    return isinstance(container, (IO, IOResult, RequiresContextIOResult))


def is_result(container: BaseContainer) -> bool:
    """
    Verifies if a container is `` Result`` type.

    .. code:: python

      >>> from returns.maybe import Maybe
      >>> from returns.result import Success

      >>> assert is_result(Success(1.0)) is True
      >>> assert is_result(Maybe.from_value(1.0)) is False

    """
    result_containers = (
        Result,
        FutureResult,
        ContextResult,
        ContextIOResult,
        IOResult,
        RequiresContextResult,
        RequiresContextIOResult,
    )
    return isinstance(container, result_containers)
