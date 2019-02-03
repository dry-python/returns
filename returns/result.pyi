# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, NoReturn, TypeVar, Union

from typing_extensions import final

from returns.primitives.monad import GenericMonadTwoSlots, Monad

_MonadType = TypeVar('_MonadType', bound=Monad)
_ResultType = TypeVar('_ResultType', bound='Result')

# Regular type vars, work correctly:
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')


class Result(GenericMonadTwoSlots[_ValueType, _ErrorType], metaclass=ABCMeta):
    _inner_value: Union[_ValueType, _ErrorType]

    def fmap(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Union['Success[_NewValueType]', 'Result[_ValueType, _ErrorType]']:
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _MonadType],
    ) -> Union[_MonadType, 'Result[_ValueType, _ErrorType]']:
        ...

    def efmap(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> Union['Success[_ValueType]', 'Success[_NewValueType]']:
        ...

    def ebind(
        self,
        function: Callable[[_ErrorType], _MonadType],
    ) -> Union[_MonadType, 'Result[_ValueType, _ErrorType]']:
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

    def fmap(self, function) -> 'Failure[_ErrorType]':
        ...

    def bind(self, function) -> 'Failure[_ErrorType]':
        ...

    def efmap(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Success[_NewValueType]':
        ...

    def ebind(
        self, function: Callable[[_ErrorType], _MonadType],
    ) -> _MonadType:
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

    def fmap(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Success[_NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _MonadType],
    ) -> _MonadType:
        ...

    def efmap(self, function) -> 'Success[_ValueType]':
        ...

    def ebind(self, function) -> 'Success[_ValueType]':
        ...

    def value_or(self, default_value: _NewValueType) -> _ValueType:
        ...

    def unwrap(self) -> _ValueType:
        ...

    def failure(self) -> NoReturn:
        ...
