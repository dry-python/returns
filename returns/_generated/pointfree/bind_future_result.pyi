from typing import Callable, TypeVar

from typing_extensions import Protocol

from returns.context import RequiresContextFutureResult
from returns.future import FutureResult

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType')


class _BindFutureResult(Protocol[_ValueType, _NewValueType, _ErrorType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    def __call__(
        self,
        container: RequiresContextFutureResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> RequiresContextFutureResult[_EnvType, _NewValueType, _ErrorType]:
        ...


def _bind_future_result(
    function: Callable[[_ValueType], FutureResult[_NewValueType, _ErrorType]],
) -> _BindFutureResult[_ValueType, _NewValueType, _ErrorType]:
    ...
