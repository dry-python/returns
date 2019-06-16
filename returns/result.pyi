# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, Coroutine, TypeVar, Union, overload

from typing_extensions import final

from returns.primitives.container import (
    FixableContainer,
    GenericContainerTwoSlots,
    ValueUnwrapContainer,
)

_ResultType = TypeVar('_ResultType', bound='Result')

# Regular type vars, work correctly:
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')
_NewErrorType = TypeVar('_NewErrorType')


class Result(
    GenericContainerTwoSlots[_ValueType, _ErrorType],
    FixableContainer,
    ValueUnwrapContainer,
    metaclass=ABCMeta,
):
    _inner_value: Union[_ValueType, _ErrorType]

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':
        ...

    def bind(
        self,
        function: Callable[
            [_ValueType], 'Result[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Result[_NewValueType, _NewErrorType]':
        ...

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Result[_NewValueType, _ErrorType]':
        ...

    def rescue(
        self,
        function: Callable[
            [_ErrorType], 'Result[_NewValueType, _NewErrorType]',
        ],
    ) -> 'Result[_NewValueType, _NewErrorType]':
        ...

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        ...

    def unwrap(self) -> _ValueType:
        ...

    def failure(self) -> _ErrorType:
        ...


@final
class _Failure(Result[Any, _ErrorType]):
    _inner_value: _ErrorType

    def __init__(self, inner_value: _ErrorType) -> None:
        ...


@final
class _Success(Result[_ValueType, Any]):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        ...


def Success(inner_value: _ValueType) -> Result[_ValueType, Any]:  # noqa: N802
    ...


def Failure(inner_value: _ErrorType) -> Result[Any, _ErrorType]:  # noqa: N802
    ...


@overload  # noqa: Z320
def safe(  # type: ignore
    function: Callable[..., Coroutine[_ValueType, _ErrorType, _NewValueType]],
) -> Callable[
    ...,
    Coroutine[_ValueType, _ErrorType, Result[_NewValueType, Exception]],
]:
    ...


@overload
def safe(
    function: Callable[..., _NewValueType],
) -> Callable[..., Result[_NewValueType, Exception]]:
    ...
