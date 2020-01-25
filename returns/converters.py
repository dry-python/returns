# -*- coding: utf-8 -*-

from typing import TypeVar

from returns._generated import fold
from returns._generated.flatten import _flatten as flatten  # noqa: F401
from returns.maybe import Maybe
from returns.result import Failure, Result, Success

# Contianer internals:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Re-export from generated:
fold_maybe = fold._fold_maybe  # noqa: WPS437
fold_result = fold._fold_result  # noqa: WPS437
fold_ioresult = fold._fold_ioresult  # noqa: WPS437


def result_to_maybe(
    result_container: Result[_ValueType, _ErrorType],
) -> Maybe[_ValueType]:
    """
    Converts ``Result`` container to ``Maybe`` container.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> result_to_maybe(Success(1)) == Some(1)
      True
      >>> result_to_maybe(Failure(1)) == Nothing
      True
      >>> result_to_maybe(Success(None)) == Nothing
      True

    """
    return Maybe.new(result_container.value_or(None))


def maybe_to_result(
    maybe_container: Maybe[_ValueType],
) -> Result[_ValueType, None]:
    """
    Converts ``Maybe`` container to ``Result`` container.

    .. code:: python

      >>> from returns.maybe import Some, Nothing
      >>> from returns.result import Failure, Success
      >>> maybe_to_result(Nothing) == Failure(None)
      True
      >>> maybe_to_result(Some(1)) == Success(1)
      True
      >>> maybe_to_result(Some(None)) == Failure(None)
      True

    """
    inner_value = maybe_container.value_or(None)
    if inner_value is not None:
        return Success(inner_value)
    return Failure(inner_value)
