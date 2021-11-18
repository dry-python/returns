from abc import abstractmethod
from typing import Callable, Generic, TypeVar

from returns.primitives.hkt import Kind1

_InnerType = TypeVar('_InnerType')

_FilterableType = TypeVar('_FilterableType', bound='Filterable')


class Filterable(Generic[_InnerType]):
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

        >>> def example(argument: int) -> bool:
        ...     return argument % 2 == 0

        >>> assert filter_(example)(Some(5)) == Nothing
        >>> assert filter_(example)(Some(6)) == Some(6)
        >>> assert filter_(example)(Nothing) == Nothing

    """

    @abstractmethod
    def filter(
        self: _FilterableType,
        predicate: Callable[[_InnerType], bool],
    ) -> Kind1[_FilterableType, _InnerType]:
        """Applies 'predicate' to the result fo a previous computation."""
