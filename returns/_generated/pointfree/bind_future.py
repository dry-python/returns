def _bind_future(function):
    """
    Lifts ``Future`` function to be wrapped in other container.

    In other words, it modifies the function's
    signature from: ``a -> Future[b]``
    to: ``Container[a] -> Container[b]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import Future, FutureResult
        >>> from returns.io import IOSuccess, IOFailure
        >>> from returns.pointfree import bind_future

        >>> def example(argument: int) -> Future[float]:
        ...     return Future.from_value(argument / 2)

        >>> async def success() -> FutureResult[float, int]:
        ...     container = FutureResult.from_value(1)
        ...     return await bind_future(example)(container)

        >>> async def failure() -> FutureResult[float, int]:
        ...     container = FutureResult.from_failure(1)
        ...     return await bind_future(example)(container)


        >>> assert anyio.run(success) == IOSuccess(0.5)
        >>> assert anyio.run(failure) == IOFailure(1)

    See also:
        - https://wiki.haskell.org/Lifting
        - https://en.wikipedia.org/wiki/Natural_transformation

    """
    return lambda container: container.bind_future(function)
