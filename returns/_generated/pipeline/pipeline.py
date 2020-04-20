from functools import wraps
from inspect import iscoroutinefunction

from returns.primitives.exceptions import UnwrapFailedError


def _pipeline(container_type):  # noqa: C901, WPS212
    """
    Decorator to enable ``do-notation`` context.

    Should be used for series of computations that rely on ``.unwrap`` method.
    Supports both async and regular functions.

    Works with both ``Maybe`` and ``Result`` containers.

    Example:
    .. code:: python

        >>> from typing import Optional
        >>> from returns.pipeline import pipeline
        >>> from returns.maybe import Maybe

        >>> @pipeline(Maybe)
        ... def test(one: Optional[int], two: Optional[int]) -> Maybe[int]:
        ...      first = Maybe.from_value(one).unwrap()
        ...      second = Maybe.from_value(two).unwrap()
        ...      return Maybe.from_value(first + second)
        ...
        >>> str(test(1, 2))
        '<Some: 3>'
        >>> str(test(2, None))
        '<Nothing>'

    Make sure to supply the correct container type when creating a pipeline.

    """
    def factory(function):
        if iscoroutinefunction(function):
            async def decorator(*args, **kwargs):  # noqa: WPS430
                try:
                    return await function(*args, **kwargs)
                except UnwrapFailedError as exc:
                    return exc.halted_container
        else:
            def decorator(*args, **kwargs):  # noqa: WPS430
                try:
                    return function(*args, **kwargs)
                except UnwrapFailedError as exc:
                    return exc.halted_container
        return wraps(function)(decorator)
    return factory
