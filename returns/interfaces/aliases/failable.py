"""
An interface that represents a computation that can fail.

This type is a base type for
:class:`returns.interfaces.specific.result.ResultLikeN`
and
:class:`returns.interfaces.specific.maybe.MaybeLikeN`.
"""

from abc import abstractmethod
from typing import Callable, Generic, NoReturn, Type, TypeVar

from returns.interfaces.aliases import container
from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_ErrorType = TypeVar('_ErrorType')

_FailableType = TypeVar('_FailableType', bound='FailableN')


class FailableN(container.ContainerN[_FirstType, _SecondType, _ThirdType]):
    """Base types for types that looks can fail."""

    @classmethod
    @abstractmethod
    def from_failure(
        cls: Type[_FailableType],  # noqa: N805
        inner_value: _ErrorType,
    ) -> KindN[_FailableType, _FirstType, _ErrorType, _ThirdType]:
        """Unit method to create new containers from any raw value."""


#: Type alias for kinds with one type argument.
Failable1 = FailableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Failable2 = FailableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Failable3 = FailableN[_FirstType, _SecondType, _ThirdType]
