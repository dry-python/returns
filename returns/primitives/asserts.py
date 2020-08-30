def assert_equal(
    first,
    second,
    *,
    deps=None,
    backend: str = 'asyncio',
) -> None:
    """
    Custom ``assert`` function to compare two any containers.

    The important note here is that
    this ``assert`` should probably used in tests.
    Not real application code.

    It will call all ``Reader`` based containers and ``await``
    all ``Future`` based ones.

    It also works recursively.
    For example, ``ReaderFutureResult`` will be called and then awaited.

    You can specify different dependencies to call your containers.
    And different backends to ``await`` then using ``anyio``.

    By the way, ``anyio`` should be installed separately.
    """
    assert _convert(
        first, deps=deps, backend=backend,
    ) == _convert(
        second, deps=deps, backend=backend,
    ), '{0} == {1}'.format(first, second)


def _convert(container, *, deps, backend: str):
    import anyio
    from returns.interfaces.specific.future import AsyncFutureN

    if isinstance(container, AsyncFutureN):
        return _convert(
            anyio.run(container.awaitable, backend=backend),
            deps=deps,
            backend=backend,
        )
    if callable(container):
        # TODO: replace with isinstance(RequiresContextLike)
        return _convert(
            container(deps),
            deps=deps,
            backend=backend,
        )
    return container
