from typing import TYPE_CHECKING, Callable, TypeVar

from returns.interfaces.specific.ioresult import IOResultBasedN
from returns.primitives.hkt import KindN, kinded

if TYPE_CHECKING:
    from returns.io import IOResult  # noqa: WPS433

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_IOResultBasedKind = TypeVar('_IOResultBasedKind', bound=IOResultBasedN)


def internal_bind_ioresult(
    container: KindN[_IOResultBasedKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[[_FirstType], 'IOResult[_UpdatedType, _SecondType]'],
) -> KindN[_IOResultBasedKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind a ``IOResult`` returning function over a container.

    .. code:: python

      >>> import anyio
      >>> from returns.methods import bind_ioresult
      >>> from returns.io import IOResult, IOSuccess, IOFailure
      >>> from returns.future import FutureResult

      >>> def example(argument: int) -> IOResult[int, str]:
      ...     return IOSuccess(argument + 1)

      >>> assert bind_ioresult(IOSuccess(1), example) == IOSuccess(2)
      >>> assert bind_ioresult(IOFailure('a'), example) == IOFailure('a')

      >>> assert anyio.run(
      ...     bind_ioresult(FutureResult.from_value(1), example).awaitable,
      ... ) == IOSuccess(2)
      >>> assert anyio.run(
      ...     bind_ioresult(FutureResult.from_failure(1), example).awaitable,
      ... ) == IOFailure(1)

    Note, that this function works
    for all containers with ``.bind_ioresult`` method.
    See :class:`returns.primitives.interfaces.specific.ioresult.IOResultBasedN`
    for more info.

    """
    return container.bind_ioresult(function)


#: Kinded version of :func:`~internal_bind_ioresult`,
#: use it to infer real return type.
bind_ioresult = kinded(internal_bind_ioresult)
