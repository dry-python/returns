from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.io import IOLikeN
from returns.primitives.hkt import KindN, kinded

if TYPE_CHECKING:
    from returns.io import IO  # noqa: WPS433§

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IOLikeKind = TypeVar('_IOLikeKind', bound=IOLikeN)


@kinded
def bind_io(
    container: KindN[_IOLikeKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], 'IO[_UpdatedType]'],
) -> KindN[_IOLikeKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a ``IO`` returning function over a container.

    .. code:: python

      >>> from returns.methods import bind_io
      >>> from returns.io import IO

      >>> def example(argument: int) -> IO[int]:
      ...     return IO(argument + 1)

      >>> assert bind_io(IO(1), example) == IO(2)

    Note, that this function works
    for all containers with ``.bind_io`` method.
    See :class:`returns.primitives.interfaces.specific.io.IOLikeN`
    for more info.

    """
    return container.bind_io(function)
