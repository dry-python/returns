# -*- coding: utf-8 -*-

from abc import ABCMeta
from typing import Any, Callable, Coroutine, Optional, TypeVar, Union, overload

from typing_extensions import final

from returns.primitives.container import (
    FixableContainer,
    GenericContainerOneSlot,
    ValueUnwrapContainer,
)

_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_ErrorType = TypeVar('_ErrorType')


class Maybe(
    GenericContainerOneSlot[_ValueType],
    FixableContainer,
    ValueUnwrapContainer,
    metaclass=ABCMeta,
):
    @classmethod
    def new(cls, inner_value: Optional[_ValueType]) -> 'Maybe[_ValueType]':
        ...

    def map(  # noqa: A003
        self,
        function: Callable[[_ValueType], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        ...

    def bind(
        self,
        function: Callable[[_ValueType], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':
        ...

    def fix(
        self,
        function: Callable[[], Optional[_NewValueType]],
    ) -> 'Maybe[_NewValueType]':
        ...

    def rescue(
        self,
        function: Callable[[], 'Maybe[_NewValueType]'],
    ) -> 'Maybe[_NewValueType]':
        ...

    def value_or(
        self,
        default_value: _NewValueType,
    ) -> Union[_ValueType, _NewValueType]:
        ...

    def unwrap(self) -> _ValueType:
        ...

    def failure(self) -> None:
        ...


@final
class _Nothing(Maybe[Any]):
    _inner_value: None

    def __init__(self, inner_value: None = ...) -> None:  # noqa: Z459
        ...


@final
class _Some(Maybe[_ValueType]):
    _inner_value: _ValueType

    def __init__(self, inner_value: _ValueType) -> None:
        ...


def Some(inner_value: Optional[_ValueType]) -> Maybe[_ValueType]:  # noqa: N802
    ...


Nothing: Maybe[Any]


@overload  # noqa: Z320
def maybe(  # type: ignore
    function: Callable[
        ...,
        Coroutine[_ValueType, _ErrorType, Optional[_NewValueType]],
    ],
) -> Callable[
    ...,
    Coroutine[_ValueType, _ErrorType, Maybe[_NewValueType]],
]:
    ...


@overload
def maybe(
    function: Callable[..., Optional[_NewValueType]],
) -> Callable[..., Maybe[_NewValueType]]:
    ...
