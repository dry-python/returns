from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar

from returns.primitives.hkt import Kind3, dekind
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
            Kind3[
                'RequiresContextFutureResult',
                _NewValueType,
                _ErrorType,
                _EnvType,
            ],
        ],
    ],
    container: 'RequiresContextFutureResult[_ValueType, _ErrorType, _EnvType]',
    deps: _EnvType,
) -> Result[_NewValueType, _ErrorType]:
    """Async binds a coroutine with container over a value."""
    inner_value = await container(deps)._inner_value
    if isinstance(inner_value, Result.success_type):
        return await dekind(
            await function(inner_value.unwrap()),
        )(deps)._inner_value
    return inner_value  # type: ignore[return-value]


async def async_compose_result(
    function: Callable[
        [Result[_ValueType, _ErrorType]],
        Kind3[
            'RequiresContextFutureResult',
            _NewValueType,
            _ErrorType,
            _EnvType,
        ],
    ],
    container: 'RequiresContextFutureResult[_ValueType, _ErrorType, _EnvType]',
    deps: _EnvType,
) -> Result[_NewValueType, _ErrorType]:
    """Async composes ``Result`` based function."""
    new_container = dekind(function((await container(deps))._inner_value))
    return (await new_container(deps))._inner_value
