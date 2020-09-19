from __future__ import annotations

from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.io import IOLikeN
from returns.primitives.hkt import Kinded, KindN, kinded

if TYPE_CHECKING:
    from returns.io import IO  # noqa: WPS433

_FirstType = TypeVar('_FirstType', contravariant=True)
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType', contravariant=True)
_UpdatedType = TypeVar('_UpdatedType', covariant=True)

_IOLikeKind = TypeVar('_IOLikeKind', bound=IOLikeN)


def bind_io(
    function: Callable[[_FirstType], 'IO[_UpdatedType]'],
) -> Kinded[Callable[
    [KindN[_IOLikeKind, _FirstType, _SecondType, _ThirdType]],
    KindN[_IOLikeKind, _UpdatedType, _SecondType, _ThirdType],
]]:
    """
    Composes successful container with a function that returns a container.

    In other words, it modifies the function's
    signature from:
    ``a -> IO[b]``
    to:
    ``Container[a, c] -> Container[b, c]``

    .. code:: python

      >>> from returns.io import IOSuccess, IOFailure
      >>> from returns.io import IO
      >>> from returns.pointfree import bind_io

      >>> def returns_io(arg: int) -> IO[int]:
      ...     return IO(arg + 1)

      >>> bound = bind_io(returns_io)
      >>> assert bound(IO(1)) == IO(2)
      >>> assert bound(IOSuccess(1)) == IOSuccess(2)
      >>> assert bound(IOFailure(1)) == IOFailure(1)

    """
    @kinded
    def factory(
        container: KindN[_IOLikeKind, _FirstType, _SecondType, _ThirdType],
    ) -> KindN[_IOLikeKind, _UpdatedType, _SecondType, _ThirdType]:
        return container.bind_io(function)
    return factory
