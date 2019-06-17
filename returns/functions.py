# -*- coding: utf-8 -*-

from typing import Callable, NoReturn, TypeVar

# Just aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


def compose(
    first: Callable[[_FirstType], _SecondType],
    second: Callable[[_SecondType], _ThirdType],
) -> Callable[[_FirstType], _ThirdType]:
    """
    Allows function composition.

    Works as: ``second . first``
    You can read it as "second after first".

    .. code:: python

      from returns.functions import compose

      logged_int = compose(int, print)('123')
      # => returns: 123
      # => prints: 123

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

      from returns.functions import raise_exception

      # Some operation result:
      user: Failure[UserDoesNotExistError]

      # Here we unwrap internal exception and raise it:
      user.fix(raise_exception)

    See: https://github.com/dry-python/returns/issues/56
    """
    raise exception
