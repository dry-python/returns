def _map(function):
    """
    Lifts function to be wrapped in a container for better composition.

    In other words, it modifies the function's
    signature from: ``a -> b`` to: ``Container[a] -> Container[b]``

    Works similar to :meth:`returns.primitives.interfaces.Mappable.map`,
    but has inverse semantics.

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import Future
        >>> from returns.io import IO
        >>> from returns.pointfree import map_

        >>> def example(argument: int) -> float:
        ...     return argument / 2  # not Future!

        >>> async def main() -> Future[float]:
        ...     return await map_(example)(Future.from_value(1))

        >>> assert anyio.run(main) == IO(0.5)

    See also:
        - https://wiki.haskell.org/Lifting
        - https://en.wikipedia.org/wiki/Natural_transformation

    """
    return lambda container: container.map(function)
