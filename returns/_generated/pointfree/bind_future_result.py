def _bind_future_result(function):
    """
    Lifts ``FutureResult`` function to be wrapped in other container.

    In other words, it modifies the function's
    signature from: ``a -> FutureResult[b, c]``
    to: ``Container[a, c] -> Container[b, c]``

    This is how it should be used:

    .. code:: python

        >>> import anyio
        >>> from returns.future import FutureResultE
        >>> from returns.context import ReaderFutureResultE
        >>> from returns.io import IOSuccess, IOFailure
        >>> from returns.pointfree import bind_future_result

        >>> def example(argument: int) -> FutureResultE[float]:
        ...     return FutureResultE.from_value(argument / 2)

        >>> assert anyio.run(bind_future_result(example)(
        ...     ReaderFutureResultE.from_value(1),
        ... ), ReaderFutureResultE.empty) == IOSuccess(0.5)

        >>> assert anyio.run(bind_future_result(example)(
        ...     ReaderFutureResultE.from_failure(':('),
        ... ), ReaderFutureResultE.empty) == IOFailure(':(')

    """
    return lambda container: container.bind_future_result(function)
