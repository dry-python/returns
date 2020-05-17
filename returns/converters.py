from typing import TypeVar

from returns._generated.converters import coalesce
from returns._generated.converters.swap import _swap as swap  # noqa: F401
from returns.maybe import Maybe
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from returns._generated.converters.flatten import (  # isort:skip # noqa: F401
    _flatten as flatten,
)

# Contianer internals:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Re-export from generated:
coalesce_maybe = coalesce._coalesce_maybe  # noqa: WPS437
coalesce_result = coalesce._coalesce_result  # noqa: WPS437
coalesce_ioresult = coalesce._coalesce_ioresult  # noqa: WPS437


def result_to_maybe(
    result_container: Result[_ValueType, _ErrorType],
) -> Maybe[_ValueType]:
    """
    Converts ``Result`` container to ``Maybe`` container.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success

      >>> assert result_to_maybe(Success(1)) == Some(1)
      >>> assert result_to_maybe(Failure(1)) == Nothing
      >>> assert result_to_maybe(Success(None)) == Nothing
      >>> assert result_to_maybe(Failure(None)) == Nothing

    """
    return Maybe.from_value(result_container.value_or(None))


def maybe_to_result(
    maybe_container: Maybe[_ValueType],
) -> Result[_ValueType, None]:
    """
    Converts ``Maybe`` container to ``Result`` container.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success

      >>> assert maybe_to_result(Some(1)) == Success(1)
      >>> assert maybe_to_result(Nothing) == Failure(None)
      >>> assert maybe_to_result(Some(None)) == Failure(None)

    """
    if is_successful(maybe_container):
        return Success(maybe_container.unwrap())
    return Failure(None)
