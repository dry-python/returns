def _alt(function):
    """
    Lifts function to be wrapped in a container for better composition.

    In other words, it modifies the function's
    signature from: ``a -> b`` to: ``Container[a] -> Container[b]``

    Works similar to :meth:`returns.primitives.interfaces.Altable.alt`,
    but has inverse semantics.

    This is how it should be used:

    .. code:: python

        >>> from returns.result import Result, Success, Failure
        >>> from returns.pointfree import alt

        >>> def example(argument: int) -> float:
        ...     return argument / 2

        >>> first: Result[str, int] = Success('a')
        >>> second: Result[str, int] = Failure(1)

        >>> assert alt(example)(first) == Success('a')
        >>> assert alt(example)(second) == Failure(0.5)

    """
    return lambda container: container.alt(function)
