def _bind_awaitable(function):
    """
    Composes a container a regular ``async`` function.

    This function should return plain, non-container value.

    In other words, it modifies the function's
    signature from: ``a -> Awaitable[b]``
    to: ``Container[a] -> Container[b]``

    .. code:: python

        >>> import anyio
        >>> from returns.future import Future
        >>> from returns.io import IO
        >>> from returns.pointfree import bind_awaitable

        >>> async def coroutine(x: int) -> int:
        ...    return x + 1

        >>> assert anyio.run(
        ...     bind_awaitable(coroutine)(Future.from_value(1)).awaitable,
        ... ) == IO(2)

    """
    return lambda container: container.bind_awaitable(function)
