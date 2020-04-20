from functools import partial as _partial
from typing import Any, Callable, TypeVar

_ReturnType = TypeVar('_ReturnType')


def partial(
    func: Callable[..., _ReturnType], *args: Any, **kwargs: Any,
) -> Callable[..., _ReturnType]:
    """
    Typed partial application helper.

    It just ``functools.partial`` wrapper with better typing support.

    We use custom ``mypy`` plugin to make types correct.
    Otherwise, it is currently impossible.

    .. code:: python

        >>> from returns.curry import partial

        >>> def sum_two_numbers(first: int, second: int) -> int:
        ...     return first + second
        ...
        >>> sum_with_ten = partial(sum_two_numbers, 10)
        >>> assert sum_with_ten(2) == 12
        >>> assert sum_with_ten(-5) == 5

    See also:
        https://docs.python.org/3/library/functools.html#functools.partial

    """
    return _partial(func, *args, **kwargs)
