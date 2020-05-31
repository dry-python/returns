def _fix(function):
    """
    Lifts function to be wrapped in a container for better composition.

    In other words, it modifies the function's
    signature from: ``a -> b`` to: ``Container[a] -> Container[b]``

    Works similar to :meth:`returns.primitives.interfaces.Fixable.fix`,
    but has inverse semantics.

    This is how it should be used:

    .. code:: python

        >>> from returns.result import Result, Success, Failure
        >>> from returns.pointfree import fix

        >>> def example(argument: int) -> float:
        ...     return argument / 2

        >>> first: Result[int, int] = Success(1)
        >>> second: Result[int, int] = Failure(1)

        >>> assert fix(example)(first) == Success(1)
        >>> assert fix(example)(second) == Success(0.5)

    """
    return lambda container: container.fix(function)
