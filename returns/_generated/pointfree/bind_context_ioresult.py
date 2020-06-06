def _bind_context_ioresult(function):
    """
    Lifts function from ``RequiresContextIOResult`` for better composition.

    In other words, it modifies the function's
    signature from: ``a -> RequiresContextResult[env, b, c]`` to:
    ``Container[env, a, c]`` -> ``Container[env, b, c]``

    .. code:: python

      >>> import anyio
      >>> from returns.context import (
      ...     RequiresContextFutureResult,
      ...     RequiresContextIOResult,
      ... )
      >>> from returns.io import IOSuccess, IOFailure
      >>> from returns.pointfree import bind_context_ioresult

      >>> def function(arg: int) -> RequiresContextIOResult[str, int, str]:
      ...     return RequiresContextIOResult(
      ...         lambda deps: IOSuccess(len(deps) + arg),
      ...     )

      >>> assert anyio.run(bind_context_ioresult(function)(
      ...     RequiresContextFutureResult.from_value(2),
      ... )('abc').awaitable) == IOSuccess(5)

      >>> assert anyio.run(bind_context_ioresult(function)(
      ...     RequiresContextFutureResult.from_failure(0),
      ... )('abc').awaitable) == IOFailure(0)

    """
    return lambda container: container.bind_context_ioresult(function)
