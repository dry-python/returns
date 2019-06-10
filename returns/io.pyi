# -*- coding: utf-8 -*-

from typing import Callable, Coroutine, TypeVar, overload

from typing_extensions import final

from returns.primitives.container import GenericContainerOneSlot

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')

# Helpers:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')


@final
class IO(GenericContainerOneSlot[_ValueType]):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        ...

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], _NewValueType],
    ) -> 'IO[_NewValueType]':
        ...

    def bind(
        self, function: Callable[[_ValueType], 'IO[_NewValueType]'],
    ) -> 'IO[_NewValueType]':
        ...


@overload  # noqa: Z320
def impure(  # type: ignore
    function: Callable[..., Coroutine[_FirstType, _SecondType, _NewValueType]],
) -> Callable[
    ...,
    Coroutine[_FirstType, _SecondType, IO[_NewValueType]],
]:
    ...


@overload
def impure(
    function: Callable[..., _NewValueType],
) -> Callable[..., IO[_NewValueType]]:
    ...
