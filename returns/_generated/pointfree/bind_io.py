def _bind_io(function):
    """
    Lifts ``IO`` function to be wrapped in other container.

    In other words, it modifies the function's
    signature from: ``a -> IO[b]`` to: ``Container[a] -> Container[b]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import Future
        >>> from returns.io import IO
        >>> from returns.pointfree import bind_io

        >>> def example(argument: int) -> IO[float]:
        ...     return IO(argument / 2)

        >>> async def main() -> Future[float]:
        ...     container = Future.from_value(1)
        ...     return await bind_io(example)(container)

        >>> assert anyio.run(main) == IO(0.5)

    Or with sync code:

    .. code:: python

          >>> from returns.io import IO, IOSuccess, IOFailure

          >>> def returns_io(arg: int) -> IO[float]:
          ...     return IO(arg + 0.5)

          >>> bound = bind_io(returns_io)
          >>> assert bound(IOSuccess(1)) == IOSuccess(1.5)
          >>> assert bound(IOFailure(1)) == IOFailure(1)

    See also:
        - https://wiki.haskell.org/Lifting
        - https://en.wikipedia.org/wiki/Natural_transformation

    """
    return lambda container: container.bind_io(function)
