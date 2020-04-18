from typing import Union

from returns._generated.pipeline.flow import _flow as flow  # noqa: F401
from returns._generated.pipeline.pipe import _pipe as pipe  # noqa: F401
from returns.io import IOResult
from returns.maybe import Maybe
from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Result

from returns._generated.pipeline.pipeline import (  # isort:skip  # noqa: F401
    _pipeline as pipeline,
)

# Logical aliases:
_Unwrapable = Union[Result, Maybe, IOResult]


def is_successful(container: '_Unwrapable') -> bool:
    """
    Determins if a container was successful or not.

    We treat container that raise ``UnwrapFailedError`` on ``.unwrap()``
    not successful.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> is_successful(Some(1))
      True
      >>> is_successful(Nothing)
      False
      >>> is_successful(Success(1))
      True
      >>> is_successful(Failure(1))
      False

    This function can work with containers that support
    :class:`returns.primitives.interfaces.Unwrapable` protocol.
    But only non-lazy containers are supported.

    """
    try:
        container.unwrap()
    except UnwrapFailedError:
        return False
    else:
        return True
