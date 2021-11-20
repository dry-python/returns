from typing import Callable, TypeVar

from returns.interfaces.filterable import FilterableN
from returns.primitives.hkt import Kinded, KindN, kinded

_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')
_FilterableKind = TypeVar('_FilterableKind', bound=FilterableN)


def filter_(
    predicate: Callable[[_FirstType], bool],
) -> Kinded[Callable[
    [KindN[_FilterableKind, _FirstType, _SecondType, _ThirdType]],
    KindN[_FilterableKind, _FirstType, _SecondType, _ThirdType],
]]:
    """
    Applies predicate over container.

    This is how it should be used:

    .. code:: python

        >>> from returns.maybe import Some, Nothing

        >>> def example(value):
        ...     return value % 2 == 0

        >>> assert filter_(example)(Some(5)) == Nothing
        >>> assert filter_(example)(Some(6)) == Some(6)

    """

    @kinded
    def factory(
        container: KindN[_FilterableKind, _FirstType, _SecondType, _ThirdType],
    ) -> KindN[_FilterableKind, _FirstType, _SecondType, _ThirdType]:
        return container.filter(predicate)

    return factory
