from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from returns.result import Result

if TYPE_CHECKING:
    from returns.context import RequiresContextFutureResult  # noqa: F401

_ValueType = TypeVar('_ValueType', covariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType', covariant=True)
_EnvType = TypeVar('_EnvType')


async def async_bind_async(
    function: Callable[
        [_ValueType],
        Awaitable[
            'RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]',
        ],
    ],
    container: 'RequiresContextFutureResult[_EnvType, _ValueType, _ErrorType]',
    deps: _EnvType,
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a coroutine with container over a value."""
    inner_value = await container(deps)._inner_value
    if isinstance(inner_value, Result.success_type):
        return await (await function(inner_value.unwrap()))(deps)._inner_value
    return inner_value  # type: ignore[return-value]
