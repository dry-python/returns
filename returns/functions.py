# -*- coding: utf-8 -*-

from functools import wraps
from inspect import iscoroutinefunction

from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Success


def is_successful(container):
    """
    Determins if a container was successful or not.

    We treat container that raise ``UnwrapFailedError`` on ``.unwrap()``
    not successful.
    """
    try:
        container.unwrap()
    except UnwrapFailedError:
        return False
    else:
        return True


def safe(function):  # noqa: C901
    """
    Decorator to covert exception throwing function to 'Result' monad.

    Show be used with care, since it only catches 'Exception' subclasses.
    It does not catch 'BaseException' subclasses.

    Supports both async and regular functions.
    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):
            try:
                return Success(await function(*args, **kwargs))
            except Exception as exc:
                return Failure(exc)
    else:
        def decorator(*args, **kwargs):
            try:
                return Success(function(*args, **kwargs))
            except Exception as exc:
                return Failure(exc)
    return wraps(function)(decorator)


def pipeline(function):  # noqa: C901
    """
    Decorator to enable 'do-notation' context.

    Should be used for series of computations that rely on ``.unwrap`` method.

    Supports both async and regular functions.
    """
    if iscoroutinefunction(function):
        async def decorator(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except UnwrapFailedError as exc:
                return exc.halted_container
    else:
        def decorator(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except UnwrapFailedError as exc:
                return exc.halted_container
    return wraps(function)(decorator)


def compose(first, second):
    """
    Allows function composition.

    Works as: ``second . first``
    You can read it as "second after first".

    We can only compose functions with one argument and one return.
    """
    return lambda argument: second(first(argument))


def raise_exception(exception):
    """
    Helper function to raise exceptions as a function.

    That's how it can be used:

    .. code:: python

      from returns.functions import raise_exception

      # Some operation result:
      user: Failure[UserDoesNotExistError]
      # Here we unwrap internal exception and raise it:
      user.fix(raise_exception)

    See: https://github.com/dry-python/returns/issues/56
    """
    raise exception
