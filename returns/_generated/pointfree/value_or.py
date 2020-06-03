def _value_or(default_value):
    """
    Get value from successful container or default value from failed one.

    .. code:: python

        >>> import anyio
        >>> from returns.pointfree import value_or
        >>> from returns.io import IO, IOFailure, IOSuccess
        >>> from returns.maybe import Some, Nothing
        >>> from returns.context import ReaderFutureResult

        >>> assert value_or(2)(IOSuccess(1)) == IO(1)
        >>> assert value_or(2)(IOFailure(1)) == IO(2)

        >>> assert value_or(2)(Some(1)) == 1
        >>> assert value_or(2)(Nothing) == 2

        >>> assert anyio.run(
        ...      value_or(2)(ReaderFutureResult.from_value(1)),
        ...      ReaderFutureResult.empty,
        ... ) == IO(1)
        >>> assert anyio.run(
        ...      value_or(2)(ReaderFutureResult.from_failure(1)),
        ...      ReaderFutureResult.empty,
        ... ) == IO(2)

    """
    return lambda container: container.value_or(default_value)
