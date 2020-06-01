def _bind_context_result(function):
    """
    Lifts function from ``RequiresContextResult`` for better composition.

    In other words, it modifies the function's
    signature from: ``a -> RequiresContextResult[env, b, c]`` to:
    ``Container[env, a, c]`` -> ``Container[env, b, c]``

    .. code:: python

      >>> from returns.context import (
      ...     RequiresContextResult,
      ...     RequiresContextIOResult,
      ... )
      >>> from returns.io import IOSuccess, IOFailure
      >>> from returns.result import Success
      >>> from returns.pointfree import bind_context_result

      >>> def function(arg: int) -> RequiresContextResult[str, int, str]:
      ...     return RequiresContextResult(
      ...         lambda deps: Success(len(deps) + arg),
      ...     )

      >>> assert bind_context_result(function)(
      ...     RequiresContextIOResult.from_value(2),
      ... )('abc') == IOSuccess(5)

      >>> assert bind_context_result(function)(
      ...     RequiresContextIOResult.from_failure(0),
      ... )('abc') == IOFailure(0)

    """
    return lambda container: container.bind_context_result(function)
