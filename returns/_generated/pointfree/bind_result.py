def _bind_result(function):
    """
    Composes successful container with a function that returns a container.

    In other words, it modifies the function's
    signature from: ``a -> Result[b, c]``
    to: ``Container[a, c] -> Container[b, c]``

    .. code:: python

      >>> from returns.io import IOSuccess
      >>> from returns.context import RequiresContextResult
      >>> from returns.result import Result, Success
      >>> from returns.pointfree import bind_result

      >>> def returns_result(arg: int) -> Result[int, str]:
      ...     return Success(arg + 1)

      >>> bound = bind_result(returns_result)
      >>> assert bound(IOSuccess(1)) == IOSuccess(2)
      >>> assert bound(RequiresContextResult.from_value(1))(...) == Success(2)

    """
    return lambda container: container.bind_result(function)
