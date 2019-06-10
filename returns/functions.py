# -*- coding: utf-8 -*-


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
