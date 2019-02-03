# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, NoReturn, TypeVar, Union, overload

from typing_extensions import Literal, final

from returns.primitives.container import Container, GenericContainerOneSlot

_ContainerType = TypeVar('_ContainerType', bound=Container)
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')


class Maybe(GenericContainerOneSlot[_ValueType], metaclass=ABCMeta):
    @overload
    @classmethod
    def new(cls, inner_value: Literal[None]) -> 'Nothing':  # type: ignore
        ...

    @overload  # noqa: F811
    @classmethod
    def new(cls, inner_value: _ValueType) -> 'Some[_ValueType]':
        ...

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> Union['Some[_NewValueType]', 'Maybe[_ValueType]']:
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _ContainerType],
    ) -> Union[_ContainerType, 'Maybe[_ValueType]']:
        ...

    def fix(
        self,
        function: Callable[[Literal[None]], '_NewValueType'],
    ) -> Union['Some[_ValueType]', 'Some[_NewValueType]']:
        ...

    def rescue(
        self,
        function: Callable[[Literal[None]], _ContainerType],
    ) -> Union[_ContainerType, 'Maybe[_ValueType]']:
        ...

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        ...

    def unwrap(self) -> Union[NoReturn, _ValueType]:
        ...

    def failure(self) -> Union[NoReturn, Literal[None]]:
        ...


@final
class Nothing(Maybe[Any]):
    _inner_value: Literal[None]

    def __init__(self, inner_value: Literal[None] = ...) -> None:
        ...

    def map(self, function) -> 'Nothing':  # noqa: A003
        ...

    def bind(self, function) -> 'Nothing':
        ...

    def fix(
        self,
        function: Callable[[Literal[None]], '_NewValueType'],
    ) -> 'Some[_NewValueType]':
        ...

    def rescue(
        self,
        function: Callable[[Literal[None]], _ContainerType],
    ) -> _ContainerType:
        ...

    def value_or(self, default_value: _NewValueType) -> _NewValueType:
        ...

    def unwrap(self) -> NoReturn:
        ...

    def failure(self) -> Literal[None]:
        ...


@final
class Some(Maybe[_ValueType]):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        ...

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'Some[_NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[_ValueType], _ContainerType],
    ) -> _ContainerType:
        ...

    def fix(self, function) -> 'Some[_ValueType]':
        ...

    def rescue(self, function) -> 'Some[_ValueType]':
        ...

    def value_or(self, default_value: _NewValueType) -> _ValueType:
        ...

    def unwrap(self) -> _ValueType:
        ...

    def failure(self) -> NoReturn:
        ...
