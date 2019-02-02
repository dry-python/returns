# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any, Generic, NoReturn, TypeVar

# These type variables are widely used in our source code.
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')


class _BaseMonad(Generic[_ValueType], metaclass=ABCMeta):
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


class Monad(_BaseMonad[_ValueType]):
    @abstractmethod
    def fmap(self, function):
        ...

    @abstractmethod
    def bind(self, function):
        ...

    @abstractmethod
    def efmap(self, function):
        ...

    @abstractmethod
    def ebind(self, function):
        ...

    @abstractmethod
    def value_or(self, default_value):
        ...

    @abstractmethod
    def unwrap(self) -> _ValueType:
        ...

    @abstractmethod
    def failure(self):
        ...
