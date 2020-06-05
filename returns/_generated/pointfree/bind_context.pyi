from typing import Callable, TypeVar, overload

from typing_extensions import Protocol

from returns.context import (
    RequiresContext,
    RequiresContextFutureResult,
    RequiresContextIOResult,
    RequiresContextResult,
)

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType')


class _BindContext(Protocol[_EnvType, _ValueType, _NewValueType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    @overload
    def __call__(
        self,
        container: RequiresContextResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextFutureResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]:
        ...


def _bind_context(
    function: Callable[[_ValueType], RequiresContext[_EnvType, _NewValueType]],
) -> _BindContext[_EnvType, _ValueType, _NewValueType]:
    ...
