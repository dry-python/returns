"""
Accepts two functions that handle different cases of containers.

First one handles successful containers like ``Some`` and ``Success``,
and second one for failed containers like ``Nothing`` and ``Failure``.

This function is useful when you need
to coalesce two possible container states into one type.

Note::
    ``IOResult`` only coalesce to ``IO`` values.
    It is impossible to unwrap ``IO`` here.

.. code:: python

    >>> from returns.converters import coalesce_result
    >>> from returns.result import Success, Failure
    >>> f1 = lambda x: x + 1
    >>> f2 = lambda y: y + 'b'
    >>> assert coalesce_result(f1, f2)(Success(1)) == 2
    >>> assert coalesce_result(f1, f2)(Failure('a')) == 'ab'

    >>> from returns.converters import coalesce_ioresult
    >>> from returns.io import IO, IOSuccess, IOFailure
    >>> f1 = lambda x: x.map(lambda state: state + 1)
    >>> f2 = lambda y: y.map(lambda state: state + 'b')
    >>> assert coalesce_result(f1, f2)(IOSuccess(1)) == IO(2)
    >>> assert coalesce_result(f1, f2)(IOFailure('a')) == IO('ab')

    >>> from returns.converters import coalesce_maybe
    >>> from returns.maybe import Some, Nothing
    >>> f1 = lambda x: x + 1
    >>> f2 = lambda _: 'a'
    >>> assert coalesce_maybe(f1, f2)(Some(1)) == 2
    >>> assert coalesce_maybe(f1, f2)(Nothing) == 'a'

"""

from typing import Callable, TypeVar

from returns.io import IO, IOResult
from returns.maybe import Maybe
from returns.pipeline import is_successful
from returns.result import Result

# Contianer internals:
_ValueType = TypeVar('_ValueType')
_ErrorType = TypeVar('_ErrorType')

# Aliases:
_FirstType = TypeVar('_FirstType')


def _coalesce(success_handler, failure_handler):
    """
    We need this function, because we cannot use a single typed function.

    Shared implementation for all types.
    """
    def decorator(container):
        if is_successful(container):
            return success_handler(container.unwrap())
        return failure_handler(container.failure())
    return decorator


_coalesce_result: Callable[
    [
        Callable[[_ValueType], _FirstType],
        Callable[[_ErrorType], _FirstType],
    ],
    Callable[[Result[_ValueType, _ErrorType]], _FirstType],
] = _coalesce
_coalesce_result.__doc__ = __doc__  # noqa: WPS125

_coalesce_ioresult: Callable[
    [
        Callable[[IO[_ValueType]], IO[_FirstType]],
        Callable[[IO[_ErrorType]], IO[_FirstType]],
    ],
    Callable[[IOResult[_ValueType, _ErrorType]], IO[_FirstType]],
] = _coalesce
_coalesce_ioresult.__doc__ = __doc__  # noqa: WPS125

_coalesce_maybe: Callable[
    [
        Callable[[_ValueType], _FirstType],
        Callable[[None], _FirstType],
    ],
    Callable[[Maybe[_ValueType]], _FirstType],
] = _coalesce
_coalesce_maybe.__doc__ = __doc__  # noqa: WPS125
