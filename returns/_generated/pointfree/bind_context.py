def _bind_context(function):
    """
    Lifts function from ``RequiresContext`` for better composition.

    In other words, it modifies the function's
    signature from: ``a -> RequiresContext[env, b]`` to:
    ``Container[env, a, c]`` -> ``Container[env, b, c]``

    .. code:: python

        >>> from returns.context import RequiresContext, RequiresContextResult
        >>> from returns.result import Success, Failure
        >>> from returns.pointfree import bind_context

        >>> def function(arg: int) -> RequiresContext[str, int]:
        ...     return RequiresContext(lambda deps: len(deps) + arg)

        >>> assert bind_context(function)(
        ...     RequiresContextResult.from_value(2),
        ... )('abc') == Success(5)

        >>> assert bind_context(function)(
        ...     RequiresContextResult.from_failure(0),
        ... )('abc') == Failure(0)

    """
    return lambda container: container.bind_context(function)
