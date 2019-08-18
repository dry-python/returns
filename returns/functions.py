# -*- coding: utf-8 -*-

from typing import Callable, NoReturn, TypeVar

from returns.generated.box import _box as box  # noqa: F401, WPS436

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


def compose(
    first: Callable[[_FirstType], _SecondType],
    second: Callable[[_SecondType], _ThirdType],
) -> Callable[[_FirstType], _ThirdType]:
    """
    Allows function composition.

    Works as: ``second . first`` or ``first() |> second()``.
    You can read it as "second after first".

    .. code:: python

      >>> from returns.functions import compose
      >>> compose(float, int)('123.5')
      123

    We can only compose functions with one argument and one return.
    Type checked.
    """
    return lambda argument: second(first(argument))


def raise_exception(exception: Exception) -> NoReturn:
    """
    Helper function to raise exceptions as a function.

    It might be required as a compatibility tool for existing APIs.
    That's how it can be used:

    .. code:: python

      >>> from returns.functions import raise_exception
      >>> from returns.result import Failure, Result
      >>> # Some operation result:
      >>> user: Result[int, ValueError] = Failure(ValueError('boom'))
      >>> # Here we unwrap internal exception and raise it:
      >>> user.fix(raise_exception)
      Traceback (most recent call last):
        ...
      ValueError: boom

    See also:
        - https://github.com/dry-python/returns/issues/56

    """
    raise exception
