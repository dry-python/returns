from typing import Awaitable, Callable, TypeVar, Union, overload

from typing_extensions import Protocol

from returns.context import (
    RequiresContextFutureResult,
    RequiresContextIOResult,
    RequiresContextResult,
)
from returns.future import FutureResult
from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.result import Result

_ValueType = TypeVar('_ValueType', contravariant=True)
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')
_EnvType = TypeVar('_EnvType', contravariant=True)


_FirstType = TypeVar('_FirstType', covariant=True)


class _ValueOr(Protocol[_FirstType]):
    """
    Helper class to represent type overloads for ret_type based on a value type.

    Contains all containers we have.

    It does not exist in runtime.
    It is also completely removed from typing with the help of the mypy plugin.
    """

    @overload
    def __call__(
        self,
        container: Maybe[_ValueType],
    ) -> Union[_ValueType, _FirstType]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextResult[_EnvType, _ValueType, _ErrorType],
    ) -> Callable[[_EnvType], Union[_ValueType, _FirstType]]:
        ...

    @overload
    def __call__(
        self,
        container: RequiresContextIOResult[_EnvType, _ValueType, _ErrorType],
    ) -> Callable[[_EnvType], IO[Union[_ValueType, _FirstType]]]:
        ...

    @overload  # noqa: WPS234
    def __call__(  # noqa: WPS234
        self,
        container: RequiresContextFutureResult[
            _EnvType, _ValueType, _ErrorType,
        ],
    ) -> Callable[[_EnvType], Awaitable[IO[Union[_ValueType, _FirstType]]]]:
        ...

    @overload
    def __call__(
        self,
        container: Result[_ValueType, _ErrorType],
    ) -> Union[_ValueType, _FirstType]:
        ...

    @overload
    def __call__(
        self,
        container: IOResult[_ValueType, _ErrorType],
    ) -> IO[Union[_ValueType, _FirstType]]:
        ...

    @overload
    def __call__(
        self,
        container: FutureResult[_ValueType, _ErrorType],
    ) -> Awaitable[IO[Union[_ValueType, _FirstType]]]:
        ...


def _value_or(
    default_value: _NewValueType,
) -> _ValueOr[_NewValueType]:
    ...
