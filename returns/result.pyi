# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, NoReturn, TypeVar, Union

from typing_extensions import final

from returns.primitives.container import Container, GenericContainerTwoSlots

_ContainerType = TypeVar('_ContainerType', bound=Container)
_ResultType = TypeVar('_ResultType', bound='Result')

# Regular type vars, work correctly:
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')


class Result(
    GenericContainerTwoSlots[_ValueType, _ErrorType],
    metaclass=ABCMeta,
):
    _inner_value: Union[_ValueType, _ErrorType]

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Union['Success[_NewValueType]', 'Result[_ValueType, _ErrorType]']:
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _ContainerType],
    ) -> Union[_ContainerType, 'Result[_ValueType, _ErrorType]']:
        ...

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> Union['Success[_ValueType]', 'Success[_NewValueType]']:
        ...

    def rescue(
        self,
        function: Callable[[_ErrorType], _ContainerType],
    ) -> Union[_ContainerType, 'Result[_ValueType, _ErrorType]']:
        ...

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_NewValueType, _ValueType]:
        ...

    def unwrap(self) -> Union[NoReturn, _ValueType]:
        ...

    def failure(self) -> Union[NoReturn, _ErrorType]:
        ...


@final
class Failure(Result[Any, _ErrorType]):
    _inner_value: _ErrorType

    def __init__(self, inner_value: _ErrorType) -> None:
        ...

    def map(self, function) -> 'Failure[_ErrorType]':  # noqa: A003
        ...

    def bind(self, function) -> 'Failure[_ErrorType]':
        ...

    def fix(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Success[_NewValueType]':
        ...

    def rescue(
        self, function: Callable[[_ErrorType], _ContainerType],
    ) -> _ContainerType:
        ...

    def value_or(self, default_value: _NewValueType) -> _NewValueType:
        ...

    def unwrap(self) -> NoReturn:
        ...

    def failure(self) -> _ErrorType:
        ...


@final
class Success(Result[_ValueType, Any]):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        ...

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Success[_NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _ContainerType],
    ) -> _ContainerType:
        ...

    def fix(self, function) -> 'Success[_ValueType]':
        ...

    def rescue(self, function) -> 'Success[_ValueType]':
        ...

    def value_or(self, default_value: _NewValueType) -> _ValueType:
        ...

    def unwrap(self) -> _ValueType:
        ...

    def failure(self) -> NoReturn:
        ...
