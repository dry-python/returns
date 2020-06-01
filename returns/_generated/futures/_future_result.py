from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar

from returns.io import IO, IOResult
from returns.result import Failure, Result, Success

if TYPE_CHECKING:
    from returns.future import Future, FutureResult  # noqa: F401


_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_NewErrorType = TypeVar('_NewErrorType')


async def async_map(
    function: Callable[[_ValueType], _NewValueType],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async maps a function over a value."""
    return (await inner_value).map(function)


async def async_apply(
    container:
        'FutureResult[Callable[[_ValueType], _NewValueType], _ErrorType]',
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async maps a function over a value."""
    return (await inner_value).apply((await container)._inner_value)


async def async_bind(
    function: Callable[
        [_ValueType],
        'FutureResult[_NewValueType, _ErrorType]',
    ],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a container over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return (await function(container.unwrap()))._inner_value
    return container  # type: ignore


async def async_bind_awaitable(
    function: Callable[[_ValueType], Awaitable[_NewValueType]],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a coroutine over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return Result.from_value(await function(container.unwrap()))
    return container  # type: ignore


async def async_bind_async(
    function: Callable[
        [_ValueType],
        Awaitable['FutureResult[_NewValueType, _ErrorType]'],
    ],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a coroutine with container over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return await (await function(container.unwrap()))._inner_value
    return container  # type: ignore


async def async_bind_result(
    function: Callable[[_ValueType], Result[_NewValueType, _ErrorType]],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a container returning ``Result`` over a value."""
    return (await inner_value).bind(function)


async def async_bind_ioresult(
    function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a container returning ``IOResult`` over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return function(container.unwrap())._inner_value
    return container  # type: ignore


async def async_bind_io(
    function: Callable[[_ValueType], IO[_NewValueType]],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a container returning ``IO`` over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return Success(function(container.unwrap())._inner_value)
    return container  # type: ignore


async def async_bind_future(
    function: Callable[[_ValueType], 'Future[_NewValueType]'],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a container returning ``IO`` over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return await async_success(function(container.unwrap()))
    return container  # type: ignore


async def async_fix(
    function: Callable[[_ErrorType], _NewValueType],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_NewValueType, _ErrorType]:
    """Async fixes a function over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return container
    return Success(function(container.failure()))


async def async_alt(
    function: Callable[[_ErrorType], _NewErrorType],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_ValueType, _NewErrorType]:
    """Async alts a function over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return container
    return Failure(function(container.failure()))


async def async_rescue(
    function: Callable[[_ErrorType], 'FutureResult[_ValueType, _NewErrorType]'],
    inner_value: Awaitable[Result[_ValueType, _ErrorType]],
) -> Result[_ValueType, _NewErrorType]:
    """Async rescues a function returning a container over a value."""
    container = await inner_value
    if isinstance(container, Result.success_type):
        return container
    return (await function(container.failure()))._inner_value


async def async_success(
    container: 'Future[_NewValueType]',
) -> Result[_NewValueType, Any]:
    """Async success unit factory."""
    return Success((await container)._inner_value)


async def async_failure(
    container: 'Future[_NewErrorType]',
) -> Result[Any, _NewErrorType]:
    """Async failure unit factory."""
    return Failure((await container)._inner_value)
