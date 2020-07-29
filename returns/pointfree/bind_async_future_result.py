from typing import Awaitable, Callable, TypeVar

from returns.future import FutureResult
from returns.interfaces.specific.future_result import FutureResultLikeN
from returns.methods.bind_async_future_result import (
    internal_bind_async_future_result,
)
from returns.primitives.hkt import Kinded, KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_FutureResultKind = TypeVar('_FutureResultKind', bound=FutureResultLikeN)


def bind_async_future_result(
    function: Callable[
        [_FirstType],
        Awaitable[FutureResult[_UpdatedType, _SecondType]],
    ],
) -> Kinded[Callable[
    [KindN[_FutureResultKind, _FirstType, _SecondType, _ThirdType]],
    KindN[_FutureResultKind, _UpdatedType, _SecondType, _ThirdType],
]]:
    """
    Compose a container and async function returning ``FutureResult``.

    In other words, it modifies the function
    signature from: ``a -> Awaitable[FutureResult[b, c]]``
    to: ``Container[a, c] -> Container[b, c]``

    This is how it should be used:

    .. code:: python

      >>> import anyio
      >>> from returns.pointfree import bind_async_future
      >>> from returns.future import Future
      >>> from returns.io import IO

      >>> async def example(argument: int) -> Future[int]:
      ...     return Future.from_value(argument + 1)

      >>> assert anyio.run(
      ...     bind_async_future(example)(Future.from_value(1)).awaitable,
      ... ) == IO(2)

    .. currentmodule: returns.primitives.interfaces.specific.future_result

    Note, that this function works
    for all containers with ``.bind_async_future`` method.
    See :class:`~FutureResultLikeN` for more info.

    """
    @kinded
    def factory(
        container: KindN[
            _FutureResultKind, _FirstType, _SecondType, _ThirdType,
        ],
    ) -> KindN[_FutureResultKind, _UpdatedType, _SecondType, _ThirdType]:
        return internal_bind_async_future_result(container, function)
    return factory
