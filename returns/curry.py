from functools import partial as _partial
from inspect import getcallargs
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


class EagerCurry:
    """Currying that calls the wrapped function when enough arguments are passed.

    Currying is a conception from functional languages that does partial
    applying. That means that if we pass one argument in a function that
    get 2 or more arguments, we'll get a new function that remembers all
    previously passed arguments. Then we can pass remaining arguments, and
    the function will be executed.

    ``partial`` sunction does a similar thing but it does partial application
    exactly once. ``eager_curry`` is a bit smarter and will do parial
    application until enough arguments passed.

    The reason why we have 2 implementations of currying is that Python
    is a bit different from classic functional languages. Python has
    unpacking and default arguments, hence sometimes we can't say if
    the user will pass more arguments or the function already must be called.
    ``eager_curry`` calls the function immediately when enough arguments passed
    while ``lazy_curry`` wait until the function is explicitly called
    without arguments.
    """
    def __init__(self, func: Callable):
        self._func = func

    def _enough(self, *args, **kwargs) -> bool:
        """Returns True if passed arguments are enough to call the function.
        """
        try:
            getcallargs(self._func, *args, **kwargs)
        except TypeError:
            return False
        return True

    def __call__(self, *args, **kwargs):
        if not self._enough(*args, **kwargs):
            return partial(self, *args, **kwargs)
        return self._func(*args, **kwargs)


class LazyCurry:
    def __init__(self, func: Callable):
        self._func = func

    def __call__(self, *args, **kwargs):
        if args or kwargs:
            return partial(self, *args, **kwargs)
        return self._func(*args, **kwargs)


eager_curry = EagerCurry
lazy_curry = LazyCurry
