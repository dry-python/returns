# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Callable, NoReturn, overload

from typing_extensions import Literal, final

from returns.primitives.monad import Monad, NewValueType, ValueType
from returns.primitives.types import MonadType


class Maybe(Monad[ValueType], metaclass=ABCMeta):
    @overload
    @classmethod
    def new(cls, inner_value: Literal[None]) -> 'Nothing':  # type: ignore
        ...

    @overload  # noqa: F811
    @classmethod
    def new(cls, inner_value: ValueType) -> 'Some[ValueType]':
        ...


@final
class Nothing(Maybe[Literal[None]]):
    _inner_value: Literal[None]

    def __init__(self, inner_value: Literal[None] = ...) -> None:
        ...

    def fmap(self, function) -> 'Nothing':
        ...

    def bind(self, function) -> 'Nothing':
        ...

    def efmap(
        self,
        function: Callable[[Literal[None]], 'NewValueType'],
    ) -> 'Some[NewValueType]':
        ...

    def ebind(
        self,
        function: Callable[[Literal[None]], MonadType],
    ) -> MonadType:
        ...

    def value_or(self, default_value: NewValueType) -> NewValueType:
        ...

    def unwrap(self) -> NoReturn:
        ...

    def failure(self) -> None:
        ...


@final
class Some(Maybe[ValueType]):
    _inner_value: ValueType

    def __init__(self, inner_value: ValueType) -> None:
        ...

    def fmap(
        self,
        function: Callable[[ValueType], NewValueType],
    ) -> 'Some[NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[ValueType], MonadType],
    ) -> MonadType:
        ...

    def efmap(self, function) -> 'Some[ValueType]':
        ...

    def ebind(self, function) -> 'Some[ValueType]':
        ...

    def value_or(self, default_value: NewValueType) -> ValueType:
        ...

    def unwrap(self) -> ValueType:
        ...

    def failure(self) -> NoReturn:
        ...
