# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Generic, NoReturn, TypeVar, Union

from typing_extensions import final

from returns.primitives.monad import Monad, NewValueType, ValueType
from returns.primitives.types import MonadType

_ErrorType = TypeVar('_ErrorType')


class Either(Generic[ValueType, _ErrorType], metaclass=ABCMeta):
    _inner_value: Union[ValueType, _ErrorType]

    @abstractmethod
    def unwrap(self) -> ValueType:  # pragma: no cover
        ...


@final
class Left(Either[Any, _ErrorType], Monad[_ErrorType]):
    _inner_value: _ErrorType

    def __init__(self, inner_value: _ErrorType) -> None:
        ...

    def fmap(self, function) -> 'Left[_ErrorType]':
        ...

    def bind(self, function) -> 'Left[_ErrorType]':
        ...

    def efmap(
        self,
        function: Callable[[_ErrorType], NewValueType],
    ) -> 'Right[NewValueType]':
        ...

    def ebind(self, function: Callable[[_ErrorType], MonadType]) -> MonadType:
        ...

    def value_or(self, default_value: NewValueType) -> NewValueType:
        ...

    def unwrap(self) -> NoReturn:
        ...

    def failure(self) -> _ErrorType:
        ...


@final
class Right(Either[ValueType, Any], Monad[ValueType]):
    _inner_value: ValueType

    def __init__(self, inner_value: ValueType) -> None:
        ...

    def fmap(
        self,
        function: Callable[[ValueType], NewValueType],
    ) -> 'Right[NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[ValueType], MonadType],
    ) -> MonadType:
        ...

    def efmap(self, function) -> 'Right[ValueType]':
        ...

    def ebind(self, function) -> 'Right[ValueType]':
        ...

    def value_or(self, default_value: NewValueType) -> ValueType:
        ...

    def unwrap(self) -> ValueType:
        ...

    def failure(self) -> NoReturn:
        ...


# Useful aliases for end users:

Result = Either
Success = Right
Failure = Left
