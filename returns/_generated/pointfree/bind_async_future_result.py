def _bind_async_future_result(function):
    """
    Compose a container and ``async`` function returning a ``FutureResult``.

    In other words, it modifies the function's
    signature from: ``a -> Awaitable[FutureResult[b, c]]``
    to: ``Container[a, c] -> Container[b, c]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import FutureResult
        >>> from returns.context import ReaderFutureResult
        >>> from returns.io import IOSuccess, IOFailure
        >>> from returns.pointfree import bind_async_future_result

        >>> async def coroutine(x: int) -> FutureResult[str, int]:
        ...    return FutureResult.from_value(str(x + 1))

        >>> bound = bind_async_future_result(coroutine)(
        ...     ReaderFutureResult.from_value(1),
        ... )
        >>> assert anyio.run(bound, ReaderFutureResult.empty) == IOSuccess('2')

        >>> bound = bind_async_future_result(coroutine)(
        ...     ReaderFutureResult.from_failure(1),
        ... )
        >>> assert anyio.run(bound, ReaderFutureResult.empty) == IOFailure(1)

    """
    return lambda container: container.bind_async_future_result(function)
