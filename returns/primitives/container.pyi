# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Generic, NoReturn, TypeVar

_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')


class _BaseContainer(object, metaclass=ABCMeta):
    __slots__ = ('_inner_value',)
    _inner_value: Any

    def __setattr__(self, attr_name: str, attr_value) -> NoReturn:
        ...

    def __delattr__(self, attr_name: str) -> NoReturn:  # noqa: Z434
        ...

    def __str__(self) -> str:
        ...

    def __eq__(self, other) -> bool:
        ...


class Container(_BaseContainer, metaclass=ABCMeta):
    @abstractmethod  # noqa: A003
    def map(self, function):
        ...

    @abstractmethod
    def bind(self, function):
        ...


class GenericContainerOneSlot(
    Generic[_ValueType],
    Container,
    metaclass=ABCMeta,
):
    ...


class GenericContainerTwoSlots(
    Generic[_ValueType, _ErrorType],
    Container,
    metaclass=ABCMeta,
):
    ...
