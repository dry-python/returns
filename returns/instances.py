from returns.context import RequiresContextIOResult
from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer


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
