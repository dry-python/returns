def _bind_async(function):
    """
    Compose a container and ``async`` function returning a container.

    In other words, it modifies the function's
    signature from: ``a -> Awaitable[Container[b]]``
    to: ``Container[a] -> Container[b]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import Future
        >>> from returns.io import IO
        >>> from returns.pointfree import bind_async

        >>> async def coroutine(x: int) -> Future[str]:
        ...    return Future.from_value(str(x + 1))

        >>> bound = bind_async(coroutine)(Future.from_value(1))
        >>> assert anyio.run(bound.awaitable) == IO('2')

    """
    return lambda container: container.bind_async(function)
