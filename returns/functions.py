from functools import wraps
from typing import Any, Callable, NoReturn, TypeVar

from returns.io import IO, IOResult
from returns.primitives.container import BaseContainer

# Aliases:
_FirstType = TypeVar('_FirstType')
_SecondType = TypeVar('_SecondType')
_ThirdType = TypeVar('_ThirdType')


def identity(instance: _FirstType) -> _FirstType:
    """
    Function that returns its argument.

    .. code:: python

      >>> identity(1)
      1
      >>> identity([1, 2, 3])
      [1, 2, 3]

    Why do we even need this?
    Identity functions help us with the composition.

    Imagine, that you want to use :func:`returns.converters.coalesce_result`
    like so:

    .. code:: python

      from returns.result import Result
      from returns.converters import coalesce_result

      numbers: Result[int, float]
      # Now you want to coalesce `number` into `int` type:
      number: int = coalesce_result(identity, int)(numbers)
      # Done!

    See also:
        - https://en.wikipedia.org/wiki/Identity_function
        - https://stackoverflow.com/a/21506571/4842742

    """
    return instance


def compose(
    first: Callable[[_FirstType], _SecondType],
    second: Callable[[_SecondType], _ThirdType],
) -> Callable[[_FirstType], _ThirdType]:
    """
    Allows function composition.

    Works as: ``second . first`` or ``first() |> second()``.
    You can read it as "second after first".

    .. code:: python

      >>> compose(float, int)('123.5')
      123

    We can only compose functions with one argument and one return.
    Type checked.
    """
    return lambda argument: second(first(argument))


def tap(
    function: Callable[[_FirstType], Any],
) -> Callable[[_FirstType], _FirstType]:
    """
    Allows to apply some function and return an argument, instead of a result.

    Is useful for composing functions with
    side-effects like ``print()``, ``logger.log()``, etc.

    .. code:: python

      >>> tap(print)(1)
      1
      1
      >>> tap(lambda _: 1)(2)
      2

    See also:
        - https://github.com/dry-python/returns/issues/145

    """
    def decorator(argument_to_return: _FirstType) -> _FirstType:
        function(argument_to_return)
        return argument_to_return
    return decorator


def untap(
    function: Callable[[_FirstType], Any],
) -> Callable[[_FirstType], None]:
    """
    Allows to apply some function and always return ``None`` as a result.

    Is useful for composing functions that do some side effects
    and return some nosense.

    Is the kind of a reverse of the ``tap`` function.

    .. code:: python

      >>> def strange_log(arg: int) -> int:
      ...     print(arg)
      ...     return arg
      >>> untap(strange_log)(2)
      2
      >>> untap(tap(lambda _: 1))(2)

    See also:
        - https://github.com/dry-python/returns/issues/145

    """
    def decorator(argument_to_return: _FirstType) -> None:
        function(argument_to_return)
    return decorator


def raise_exception(exception: Exception) -> NoReturn:
    """
    Helper function to raise exceptions as a function.

    It might be required as a compatibility tool for existing APIs.
    That's how it can be used:

    .. code:: python

      >>> from returns.result import Failure, Result
      >>> # Some operation result:
      >>> user: Result[int, ValueError] = Failure(ValueError('boom'))
      >>> # Here we unwrap internal exception and raise it:

    .. code::

      >>> user.fix(raise_exception)
      Traceback (most recent call last):
        ...
      ValueError: boom

    See also:
        - https://github.com/dry-python/returns/issues/56

    """
    raise exception


def not_(function: Callable[..., bool]) -> Callable[..., bool]:
    """
    Denies the function returns.

    .. code:: python

      >>> from returns.result import Result, Success, Failure

      >>> def is_successful(result_container: Result[float, int]) -> bool:
      ...     return isinstance(result_container, Result.success_type)
      ...

      >>> assert not_(is_successful)(Success(1.0)) is False
      >>> assert not_(is_successful)(Failure(1)) is True

    """
    @wraps(function)  # noqa: WPS430
    def wrapped_function(*args, **kwargs) -> bool:  # noqa: WPS430
        return not function(*args, **kwargs)
    return wrapped_function


def is_io(container: BaseContainer) -> bool:
    """
    Verifies if a container is ``IO`` type.

    .. code:: python

      >>> from returns.io import IO
      >>> from returns.result import Success

      >>> assert is_io(IO(1.0)) is True
      >>> assert is_io(Success(1.0)) is False

    """
    from returns.context import RequiresContextIOResult  # noqa: WPS433
    return isinstance(container, (IO, IOResult, RequiresContextIOResult))
