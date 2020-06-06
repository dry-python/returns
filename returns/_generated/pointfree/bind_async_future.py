def _bind_async_future(function):
    """
    Compose a container and ``async`` function returning a `container`.

    In other words, it modifies the function's
    signature from: ``a -> Awaitable[Container[b]]``
    to: ``Container[a] -> Container[b]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import Future, FutureResult
        >>> from returns.io import IOSuccess, IOFailure
        >>> from returns.pointfree import bind_async_future

        >>> async def coroutine(x: int) -> Future[str]:
        ...    return Future.from_value(str(x + 1))

        >>> bound = bind_async_future(coroutine)(FutureResult.from_value(1))
        >>> assert anyio.run(bound.awaitable) == IOSuccess('2')

        >>> bound = bind_async_future(coroutine)(FutureResult.from_failure(1))
        >>> assert anyio.run(bound.awaitable) == IOFailure(1)

    """
    return lambda container: container.bind_async_future(function)
