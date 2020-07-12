from abc import abstractmethod
from typing import Callable, Generic, NoReturn, TypeVar

from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')
_MappableType = TypeVar('_MappableType', bound='MappableN')


class MappableN(Generic[_FirstType, _SecondType, _ThirdType]):
    """
    Allows to chain wrapped values in containers with regular functions.

    Behaves like a functor.

    See also:
        https://en.wikipedia.org/wiki/Functor
    """

    @abstractmethod  # noqa: WPS125
    def map(  # noqa: WPS125
        self: _MappableType,
        function: Callable[[_FirstType], _UpdatedType],
    ) -> KindN[_MappableType, _UpdatedType, _SecondType, _ThirdType]:
        """Allows to run a pure function over a container."""


#: Type alias for kinds with one type argument.
Mappable1 = MappableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Mappable2 = MappableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Mappable3 = MappableN[_FirstType, _SecondType, _ThirdType]
