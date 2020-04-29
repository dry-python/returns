from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

if TYPE_CHECKING:
    from returns.future import Future  # noqa: F401

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')


async def async_map(
    function: Callable[[_ValueType], _NewValueType],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    """Async maps a function over a value."""
    return function(await inner_value)


async def async_bind_awaitable(
    function: Callable[[_ValueType], Awaitable[_NewValueType]],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    """Async binds a coroutine over a value."""
    return await function(await inner_value)


async def async_bind(
    function: Callable[[_ValueType], 'Future[_NewValueType]'],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    """Async binds a container over a value."""
    return (await function(await inner_value))._inner_value  # noqa: WPS437


async def async_bind_async(
    function: Callable[[_ValueType], Awaitable['Future[_NewValueType]']],
    inner_value: Awaitable[_ValueType],
) -> _NewValueType:
    """Async binds a coroutine with container over a value."""
    inner_io = (await function(await inner_value))._inner_value  # noqa: WPS437
    return await inner_io
