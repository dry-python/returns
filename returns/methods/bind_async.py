from typing import Awaitable, Callable, TypeVar

from returns.interfaces.specific.future import FutureLikeN
from returns.primitives.hkt import KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_FutureKind = TypeVar('_FutureKind', bound=FutureLikeN)


def internal_bind_async(
    container: KindN[_FutureKind, _FirstType, _SecondType, _ThirdType],
    function: Callable[
        [_FirstType],
        Awaitable[KindN[_FutureKind, _UpdatedType, _SecondType, _ThirdType]],
    ],
) -> KindN[_FutureKind, _UpdatedType, _SecondType, _ThirdType]:
    """
    Bind an async function over a container.

    .. code:: python

      >>> import anyio
      >>> from returns.methods import bind_async
      >>> from returns.future import Future
      >>> from returns.io import IO

      >>> async def example(argument: int) -> Future[int]:
      ...     return Future.from_value(argument + 1)

      >>> assert anyio.run(
      ...     bind_async(Future.from_value(1), example).awaitable,
      ... ) == IO(2)

    Note, that this function works
    for all containers with ``.bind_async`` method.
    See :class:`returns.primitives.interfaces.specific.future.FutureLikeN`
    for more info.

    """
    return container.bind_async(function)


#: Kinded version of :func:`~internal_bind_async`,
#: use it to infer real return type.
bind_async = kinded(internal_bind_async)
