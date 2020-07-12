from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.io import IOBasedN
from returns.primitives.hkt import KindN, debound, kinded

if TYPE_CHECKING:
    from returns.io import IO  # noqa: WPS433§

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IOBasedKind = TypeVar('_IOBasedKind', bound=IOBasedN)


def internal_bind_io(
    container: KindN[_IOBasedKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], 'IO[_UpdatedType]'],
) -> KindN[_IOBasedKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a ``IO`` returning function over a container.

    It is not marked as ``@kinded``, because this function is intended
    to be used inside a kinded context:
    like in :func:`returns.pointfree.bind.bind`.
    It returns ``KindN[]`` instance, not a real type.

    If you wish to use the user-facing ``bind_io``
    that infers the return type correctly,
    use :func:`~bind_io` function instead.

    .. code:: python

      >>> from returns.methods.bind_io import bind_io
      >>> from returns.io import IO

      >>> def example(argument: int) -> IO[int]:
      ...     return IO(argument + 1)

      >>> assert bind_io(IO(1), example) == IO(2)

    Note, that this function works
    for all containers with ``.bind_io`` method.
    See :class:`returns.primitives.interfaces.specific.io.IOBasedN`
    for more info.

    """
    new_instance, rebound = debound(container)
    return rebound(new_instance.bind_io(function))


#: Kinded version of :func:`~internal_bind_io`,
#: use it to infer real return type.
bind_io = kinded(internal_bind_io)
