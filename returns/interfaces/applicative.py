from abc import abstractmethod
from typing import Callable, Generic, NoReturn, Type, TypeVar

from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')
_ApplicativeType = TypeVar('_ApplicativeType', bound='ApplicativeN')


class ApplicativeN(Generic[_FirstType, _SecondType, _ThirdType]):
    """
    Allows to create unit containers from raw values and to apply wrapped funcs.

    See also:
        https://en.wikipedia.org/wiki/Applicative_functor
        http://learnyouahaskell.com/functors-applicative-functors-and-monoids

    """

    @abstractmethod
    def apply(
        self: _ApplicativeType,
        container: KindN[
            _ApplicativeType,
            Callable[[_FirstType], _UpdatedType],
            _SecondType,
            _ThirdType,
        ],
    ) -> KindN[_ApplicativeType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to apply a wrapped function over a container."""

    @classmethod
    @abstractmethod
    def from_value(
        cls: Type[_ApplicativeType],  # noqa: N805
        inner_value: _FirstType,
    ) -> KindN[_ApplicativeType, _FirstType, _SecondType, _ThirdType]:
        """Unit method to create new containers from any raw value."""


#: Type alias for kinds with one type argument.
Applicative1 = ApplicativeN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Applicative2 = ApplicativeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Applicative3 = ApplicativeN[_FirstType, _SecondType, _ThirdType]
