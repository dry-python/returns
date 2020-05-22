def _bind_ioresult(function):
    """
    Lifts function returning ``IOResult`` to be wrapped in another container.

    In other words, it modifies the function's
    signature from: ``a -> IOResult[b, c]``
    to: ``Container[a, c] -> Container[b, c]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import FutureResult
        >>> from returns.io import IOSuccess, IOFailure, IOResult
        >>> from returns.pointfree import bind_ioresult

        >>> def example(argument: int) -> IOResult[float, int]:
        ...     return IOSuccess(argument / 2)

        >>> async def success() -> FutureResult[float, int]:
        ...     container = FutureResult.from_value(1)
        ...     return await bind_ioresult(example)(container)

        >>> async def failure() -> FutureResult[float, int]:
        ...     container = FutureResult.from_failure(1)
        ...     return await bind_ioresult(example)(container)

        >>> assert anyio.run(success) == IOSuccess(0.5)
        >>> assert anyio.run(failure) == IOFailure(1)

    And with sync code:

    .. code:: python

        >>> from returns.context import RequiresContextIOResult

        >>> def function(arg: int) -> IOResult[str, int]:
        ...     if arg > 0:
        ...         return IOSuccess(str(arg) + '!')
        ...     return IOFailure(arg)

        >>> deps = RequiresContextIOResult.empty

        >>> assert bind_ioresult(function)(
        ...     RequiresContextIOResult.from_value(1),
        ... )(deps) == IOSuccess('1!')

        >>> assert bind_ioresult(function)(
        ...     RequiresContextIOResult.from_value(0),
        ... )(deps) == IOFailure(0)

        >>> assert bind_ioresult(function)(
        ...     RequiresContextIOResult.from_failure('nope'),
        ... )(deps) == IOFailure('nope')

    See also:
        - https://wiki.haskell.org/Lifting
        - https://en.wikipedia.org/wiki/Natural_transformation

    """
    return lambda container: container.bind_ioresult(function)
