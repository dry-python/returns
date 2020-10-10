from abc import abstractmethod
from typing import Callable, Generic, NoReturn, TypeVar

from returns.primitives.hkt import KindN

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_UpdatedType = TypeVar('_UpdatedType')

_BindableType = TypeVar('_BindableType', bound='BindableN')


class BindableN(Generic[_FirstType, _SecondType, _ThirdType]):
    """
    Represents a "context" in which calculations can be executed.

    ``Bindable`` allows you to bind together
    a series of calculations while maintaining
    the context of that specific container.

    In contrast to :class:`returns.interfaces.lashable.LashableN`,
    works with the first type argument.
    """

    @abstractmethod
    def bind(
        self: _BindableType,
        function: Callable[
            [_FirstType],
            KindN[_BindableType, _UpdatedType, _SecondType, _ThirdType],
        ],
    ) -> KindN[_BindableType, _UpdatedType, _SecondType, _ThirdType]:
        """
        Applies 'function' to the result of a previous calculation.

        And returns a new container.
        """


#: Type alias for kinds with one type argument.
Bindable1 = BindableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Bindable2 = BindableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Bindable3 = BindableN[_FirstType, _SecondType, _ThirdType]
