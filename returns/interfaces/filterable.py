from abc import abstractmethod
from typing import Callable, NoReturn, TypeVar

from returns.interfaces.specific.maybe import MaybeLikeN
from returns.primitives.hkt import Kind1

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')

_FilterableType = TypeVar('_FilterableType', bound='FilterableN')


class FilterableN(MaybeLikeN[_FirstType, _SecondType, _ThirdType]):
    """
    Represents container that can apply filter over inner value.

    There are no aliases or ``FilterableN` for ``Filterable`` interface.
    Because it always uses one type.

    Not all types can be ``Filterable`` because we require
    a possibility to access internal value and to model a case,
    where the predicate is false

    .. code:: python

        >>> from returns.maybe import Nothing, Some
        >>> from returns.pointfree import filter_

        >>> def is_even(argument: int) -> bool:
        ...     return argument % 2 == 0

        >>> assert filter_(is_even)(Some(5)) == Nothing
        >>> assert filter_(is_even)(Some(6)) == Some(6)
        >>> assert filter_(is_even)(Nothing) == Nothing

    """

    @abstractmethod
    def filter(
        self: _FilterableType,
        predicate: Callable[[_FirstType], bool],
    ) -> Kind1[_FilterableType, _FirstType]:
        """Applies 'predicate' to the result of a previous computation."""


#: Type alias for kinds with one type argument.
Filterable1 = FilterableN[_FirstType, NoReturn, NoReturn]

#: Type alias for kinds with two type arguments.
Filterable2 = FilterableN[_FirstType, _SecondType, NoReturn]

#: Type alias for kinds with three type arguments.
Filterable3 = FilterableN[_FirstType, _SecondType, _ThirdType]
