from typing import ClassVar

from typing_extensions import Protocol

from returns._generated.pipeline.flow import _flow as flow
from returns._generated.pipeline.managed import _managed as managed
from returns._generated.pipeline.pipe import _pipe as pipe


class _HasSuccessAndFailureTypes(Protocol):
    """This protocol enforces container to have a ``.success_type`` field."""

    success_type: ClassVar[type]


def is_successful(container: _HasSuccessAndFailureTypes) -> bool:
    """
    Determins if a container was successful or not.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> from returns.io import IOSuccess, IOFailure

      >>> assert is_successful(Some(1))
      >>> assert not is_successful(Nothing)

      >>> assert is_successful(Success(1))
      >>> assert not is_successful(Failure(1))

      >>> assert is_successful(IOSuccess(1))
      >>> assert not is_successful(IOFailure(1))

    This function can work with containers
    that have ``.success_type`` class field.

    """
    return isinstance(container, container.success_type)
