import re

from functools import partial as _partial, update_wrapper
from inspect import getcallargs
from typing import Any, Dict, Callable, TypeVar

_ReturnType = TypeVar('_ReturnType')
rex_missing = re.compile(r'.+ missing \d+ required \w+ arguments?\: .+')


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

    If wrong arguments passed, ``TypeError`` will be raised immediately.

    .. code:: python

        >>> @eager_curry
        ... def divide(left: int, right: int) -> float:
        ...   return left / right
        ...
        >>> divide(10)  # doesn't call the func and remembers arguments
        functools.partial(<returns.curry.EagerCurry object at ...>, 10)
        >>> divide(10, 5)  # you can call the func like always
        2.0
        >>> divide(10)(5)  # the same as above
        2.0
        >>> divide(right=10)(5)
        0.5
        >>> divide(right=10)(left=5)
        0.5

    """
    def __init__(self, func: Callable):
        self._func = func

    def _enough(self, *args, **kwargs) -> bool:
        """Returns True if passed arguments are enough to call the function.
        """
        try:
            getcallargs(self._func, *args, **kwargs)
        except TypeError as err:
            # another option is to copy-paste and patch `getcallargs` func
            # but in this case we get responsibility to maintain it over
            # python releases.
            if rex_missing.fullmatch(err.args[0]):
                return False
            raise
        return True

    def __call__(self, *args, **kwargs):
        if not self._enough(*args, **kwargs):
            return partial(self, *args, **kwargs)
        return self._func(*args, **kwargs)


def eager_curry(func: Callable) -> EagerCurry:
    wrapper = EagerCurry(func)
    return update_wrapper(wrapper=wrapper, wrapped=func)


def _lazy_curry(
    func: Callable,
    old_args: tuple, old_kwargs: Dict[str, Any],
    new_args: tuple, new_kwargs: Dict[str, Any],
):
    #  if no new arguments are passed, call the function
    if not new_args and not new_kwargs:
        return func(*old_args, **old_kwargs)

    # if new arguments are passed, remember them for future calls.
    old_args += new_args
    old_kwargs = old_kwargs.copy()
    old_kwargs.update(new_kwargs)

    def wrapper(*args, **kwargs):
        return _lazy_curry(func, old_args, old_kwargs, args, kwargs)

    # EagerCurry returns either partial or the function result.
    # Let's not break expectations here and return partial as well.
    return partial(wrapper)


def lazy_curry(func: Callable) -> Callable:
    """Currying that calls the wrapped function when called without arguments.

    See documentation for ``eager_curry`` to learn about currying.

    If wrong arguments passed, ``TypeError`` will be raised only
    wnen called without arguments after that.
    """
    def wrapper(*args, **kwargs):
        return _lazy_curry(func, (), {}, args, kwargs)

    return update_wrapper(wrapper=wrapper, wrapped=func)
