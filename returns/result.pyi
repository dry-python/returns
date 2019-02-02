# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, Generic, NoReturn, TypeVar, Union

from typing_extensions import final

from returns.primitives.monad import Monad

# There's a wierd bug with mypy when we remove this line and use import:
_MonadType = TypeVar('_MonadType', bound='Monad')

# Regular type vars, work correctly:
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')


# That's the ugliest part.
# We need to express `Result` with two type parameters and
# Failure and Success with just one parameter.
# And that's how we do it. Any other and more cleaner ways are appreciated.
class Result(Generic[_ValueType, _ErrorType], Monad, metaclass=ABCMeta):
    _inner_value: Union[_ValueType, _ErrorType]

    def fmap(
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> _MonadType:
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _MonadType],
    ) -> _MonadType:
        ...

    def efmap(
        self,
        function: Callable[[_ErrorType], _NewValueType],
    ) -> 'Success[_NewValueType]':
        ...

    def ebind(
        self,
        function: Callable[[_ErrorType], _MonadType],
    ) -> _MonadType:
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
class Failure(Result[Any, _ErrorType], Monad[_ErrorType]):
    _inner_value: _ErrorType

    def __init__(self, inner_value: _ErrorType) -> None:
        ...

    def fmap(self, function) -> 'Failure[_ErrorType]':  # type: ignore
        ...

    def bind(self, function) -> 'Failure[_ErrorType]':  # type: ignore
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
class Success(Result[_ValueType, Any], Monad[_ValueType]):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        ...

    def fmap(  # type: ignore
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Success[_NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _MonadType],
    ) -> _MonadType:
        ...

    def efmap(self, function) -> 'Success[_ValueType]':  # type: ignore
        ...

    def ebind(self, function) -> 'Success[_ValueType]':  # type: ignore
        ...

    def value_or(self, default_value: _NewValueType) -> _ValueType:
        ...

    def unwrap(self) -> _ValueType:
        ...

    def failure(self) -> NoReturn:
        ...
