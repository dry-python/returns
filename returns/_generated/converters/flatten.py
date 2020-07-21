from typing import TypeVar

from returns.functions import identity
from returns.interfaces.bindable import BindableN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_BindableKind = TypeVar('_BindableKind', bound=BindableN)


@kinded
def _flatten(container: KindN[
    _BindableKind,
    KindN[_BindableKind, _FirstType, _SecondType, _ThirdType],
    _SecondType,
    _ThirdType,
]) -> KindN[_BindableKind, _FirstType, _SecondType, _ThirdType]:
    """
    Joins two nested containers together.

    Please, note that it will not join
    two ``Failure`` for ``Result`` case
    or two ``Nothing`` for ``Maybe`` case together.

    .. code:: python

      >>> from returns.converters import flatten
      >>> from returns.maybe import Some
      >>> from returns.result import Failure, Success
      >>> from returns.io import IO, IOSuccess, IOFailure
      >>> from returns.context import RequiresContext, RequiresContextResult

      >>> assert flatten(IO(IO(1))) == IO(1)

      >>> assert flatten(Some(Some(1))) == Some(1)

      >>> assert flatten(Success(Success(1))) == Success(1)
      >>> assert flatten(Failure(Failure(1))) == Failure(Failure(1))

      >>> assert flatten(IOSuccess(IOSuccess(1))) == IOSuccess(1)
      >>> assert flatten(IOFailure(IOFailure(1))) == IOFailure(IOFailure(1))

      >>> assert flatten(
      ...     RequiresContext.from_value(RequiresContext.from_value(1)),
      ... )(RequiresContext.empty) == 1

      >>> assert flatten(
      ...     RequiresContextResult.from_value(
      ...         RequiresContextResult.from_value(1),
      ...     ),
      ... )(RequiresContext.empty) == Success(1)

    See also:
        https://bit.ly/2sIviUr

    """
    return container.bind(identity)
