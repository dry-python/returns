from functools import partial
from typing import Any, Callable, TypeVar

_ReturnType = TypeVar('_ReturnType')


def curry(
    func: Callable[..., _ReturnType], *args: Any, **kwargs: Any,
) -> Callable[..., _ReturnType]:
    """
    Typed curring helper.

    It just ``functools.partial`` wrapper with better typing support.

    We use custom ``mypy`` plugin to make types correct.
    Otherwise, it is currently impossible.

    .. code:: python

        >>> from returns.curry import curry
        >>> curried_int = curry(int, base=2)
        >>> assert curried_int('10') == 2

    See also:
        https://docs.python.org/3/library/functools.html#functools.partial

    """
    return partial(func, *args, **kwargs)
