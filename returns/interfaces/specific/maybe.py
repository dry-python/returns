from abc import abstractmethod
from typing import Callable, NoReturn, Optional, Type, TypeVar, Union

from returns.interfaces import container, equable, rescuable, unwrappable
from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_MaybeLikeType = TypeVar('_MaybeLikeType', bound='MaybeLikeN')

# New values:
_ValueType = TypeVar('_ValueType')


class MaybeLikeN(
    container.ContainerN[_FirstType, _SecondType, _ThirdType],
    rescuable.RescuableN[_FirstType, _SecondType, _ThirdType],
):
    """
    Type for values that do look like a ``Maybe``.

    For example, ``RequiresContextMaybe`` should be created from this interface.
    Cannot be unwrapped or compared.
    """

    @abstractmethod
    def bind_optional(
        self: _MaybeLikeType,
        function: Callable[[_FirstType], Optional[_UpdatedType]],
    ) -> KindN[_MaybeLikeType, _UpdatedType, _SecondType, _ThirdType]:
        """Binds a function that returns ``Optional`` values."""

    @classmethod
    @abstractmethod
    def from_optional(
        cls: Type[_MaybeLikeType],  # noqa: N805
        inner_value: Optional[_ValueType],
    ) -> KindN[_MaybeLikeType, _ValueType, _SecondType, _ThirdType]:
        """Unit method to create containers from ``Optional`` value."""


#: Type alias for kinds with two type arguments.
MaybeLike2 = MaybeLikeN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
MaybeLike3 = MaybeLikeN[_FirstType, _SecondType, _ThirdType]


class MaybeBasedN(
    MaybeLikeN[_FirstType, _SecondType, _ThirdType],
    unwrappable.Unwrappable[_FirstType, None],
    equable.SupportsEquality,
):
    """
    Concrete interface for ``Maybe`` type.

    Can be unwrapped and compared.
    """

    @abstractmethod
    def or_else_call(
        self,
        function: Callable[[], _ValueType],
    ) -> Union[_FirstType, _ValueType]:
        """Calls a function in case there nothing to unwrap."""


#: Type alias for kinds with two type arguments.
MaybeBased2 = MaybeBasedN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
MaybeBased3 = MaybeBasedN[_FirstType, _SecondType, _ThirdType]
