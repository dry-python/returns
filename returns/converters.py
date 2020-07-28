from typing import TypeVar

from returns.functions import identity
from returns.interfaces.bindable import BindableN
from returns.interfaces.specific.result import ResultLikeN
from returns.maybe import Maybe
from returns.pipeline import is_successful
from returns.primitives.hkt import KindN, kinded
from returns.result import Failure, Result, Success

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_BindableKind = TypeVar('_BindableKind', bound=BindableN)
_ResultLikeKind = TypeVar('_ResultLikeKind', bound=ResultLikeN)


@kinded
def swap(
    container: KindN[_ResultLikeKind, _FirstType, _SecondType, _ThirdType],
) -> KindN[_ResultLikeKind, _SecondType, _FirstType, _ThirdType]:
    """
    Swaps value and error types in a container.

    Why? Because we have a lot of ``.bind`` related helpers
    and none ``.rescue`` related helpers.

    So, you can ``swap`` a container to handle errors in a simple way,
    and then swap it back to continue normal execution.

    .. code:: python

      >>> from returns.converters import swap
      >>> from returns.io import IOResult, IOSuccess, IOFailure

      >>> container: IOResult[int, str] = IOSuccess(1)
      >>> swapped: IOResult[str, int] = swap(container)
      >>> assert swapped == IOFailure(1)

      >>> container: IOResult[int, str] = IOFailure('error')
      >>> assert swap(container) == IOSuccess('error')

    And here's how you can handle errors easily:

    .. code:: python

      >>> from returns.converters import swap
      >>> from returns.io import IOResult, IOSuccess
      >>> from returns.result import Result, Success

      >>> def function(error: str) -> Result[str, int]:
      ...     return Success('Very bad error: ' + error)

      >>> container: IOResult[int, str] = IOFailure('boom')
      >>> # You cannot `.rescue_result`, but you can `.bind_result` instead!
      >>> assert swap(
      ...     swap(container).bind_result(function),
      ... ) == IOFailure('Very bad error: boom')

    This converter supports all ``ResultLikeN`` containers.
    """
    return container.swap()


@kinded
def flatten(
    container: KindN[
        _BindableKind,
        KindN[_BindableKind, _FirstType, _SecondType, _ThirdType],
        _SecondType,
        _ThirdType,
    ],
) -> KindN[_BindableKind, _FirstType, _SecondType, _ThirdType]:
    """
    Joins two nested containers together.

    Please, note that it will not join
    two ``Failure`` for ``Result`` case
    or two ``Nothing`` for ``Maybe`` case
    (or basically any two error types) together.

    .. code:: python

      >>> from returns.converters import flatten
      >>> from returns.io import IO
      >>> from returns.result import Failure, Success

      >>> assert flatten(IO(IO(1))) == IO(1)

      >>> assert flatten(Success(Success(1))) == Success(1)
      >>> assert flatten(Failure(Failure(1))) == Failure(Failure(1))

    See also:
        https://bit.ly/2sIviUr

    """
    return container.bind(identity)


def result_to_maybe(
    result_container: Result[_FirstType, _SecondType],
) -> Maybe[_FirstType]:
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
    maybe_container: Maybe[_FirstType],
) -> Result[_FirstType, None]:
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
