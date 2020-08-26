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


def assert_equal(
    first,
    second,
    *,
    deps=None,
    backend: str = 'asyncio',
) -> None:
    assert _convert(
        first, deps=deps, backend=backend,
    ) == _convert(
        second, deps=deps, backend=backend,
    ), '{0} == {1}'.format(first, second)
