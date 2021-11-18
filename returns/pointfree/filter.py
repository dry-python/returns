from typing import Callable, TypeVar

from returns.interfaces.filterable import Filterable
from returns.primitives.hkt import Kind1, Kinded, kinded

_InnerType = TypeVar('_InnerType')
_FilterableKind = TypeVar('_FilterableKind', bound=Filterable)


def filter_(
    predicate: Callable[[_InnerType], bool],
) -> Kinded[Callable[
    [Kind1[_FilterableKind, _InnerType]],
    Kind1[_FilterableKind, _InnerType],
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
        container: Kind1[_FilterableKind, _InnerType],
    ) -> Kind1[_FilterableKind, _InnerType]:
        return container.filter(predicate)

    return factory
