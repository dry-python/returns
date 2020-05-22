from typing import Callable, TypeVar, overload

from typing_extensions import Protocol

from returns.context import RequiresContextIOResult
from returns.future import FutureResult
from returns.io import IOResult

_ValueType = TypeVar('_ValueType', contravariant=True)
_ErrorType = TypeVar('_ErrorType')
_NewValueType = TypeVar('_NewValueType', covariant=True)
_EnvType = TypeVar('_EnvType', contravariant=True)


class _BindIOResult(Protocol[_ValueType, _NewValueType, _ErrorType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    @overload
    def __call__(
        self,
        container: RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
    ) -> RequiresContextIOResult[_EnvType, _NewValueType, _ErrorType]:
        ...

    @overload
    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> FutureResult[_NewValueType, _ErrorType]:
        ...


def _bind_ioresult(
    function: Callable[[_ValueType], IOResult[_NewValueType, _ErrorType]],
) -> _BindIOResult[_ValueType, _NewValueType, _ErrorType]:
    ...
