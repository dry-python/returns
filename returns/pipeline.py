# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, Union

from returns._generated.pipe import _pipe as pipe  # noqa: F401
from returns._generated.pipeline import _pipeline as pipeline
from returns.primitives.exceptions import UnwrapFailedError

if TYPE_CHECKING:  # pragma: no cover
    from returns.maybe import Maybe
    from returns.result import Result
    from returns.io import IOResult

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

    """
    try:
        container.unwrap()
    except UnwrapFailedError:
        return False
    else:
        return True
