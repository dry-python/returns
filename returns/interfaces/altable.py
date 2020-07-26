from abc import abstractmethod
from typing import Callable, Generic, NoReturn, TypeVar

from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_AltableType = TypeVar('_AltableType', bound='AltableN')


class AltableN(Generic[_FirstType, _SecondType, _ThirdType]):
    """Modifies the second type argument with a pure function."""

    @abstractmethod
    def alt(
        self: _AltableType,
        function: Callable[[_SecondType], _UpdatedType],
    ) -> KindN[_AltableType, _FirstType, _UpdatedType, _ThirdType]:
        """Allows to run a pure function over a container."""


#: Type alias for kinds with two type arguments.
Altable2 = AltableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Altable3 = AltableN[_FirstType, _SecondType, _ThirdType]
