import types
from contextlib import contextmanager
from inspect import FrameInfo, stack
from typing import Iterator, List, Optional

from returns.result import _Failure


def collect_traces() -> Iterator[None]:
    """
    Context Manager/Decorator to active traces collect to the Failures.

    .. code:: python

        >>> from inspect import FrameInfo

        >>> from returns.io import IOResult
        >>> from returns.result import Result
        >>> from returns.primitives.tracing import collect_traces

        >>> with collect_traces():
        ...     traced_failure = Result.from_failure('Traced Failure')
        >>> non_traced_failure = IOResult.from_failure('Non Traced Failure')

        >>> assert non_traced_failure.trace is None
        >>> assert isinstance(traced_failure.trace, list)
        >>> assert all(isinstance(trace_line, FrameInfo) for trace_line in traced_failure.trace)

        >>> for trace_line in traced_failure.trace:
        ...     print(f'{trace_line.filename}:{trace_line.lineno} in `{trace_line.function}`') # doctest: +SKIP
        ...
        /returns/returns/result.py:525 in `Failure`
        /returns/returns/result.py:322 in `from_failure`
        /example_folder/example.py:1 in `<module>`
        # doctest: # noqa: DAR301, E501

    """
    unpatched_get_trace = getattr(_Failure, '_get_trace')  # noqa: B009
    substitute_get_trace = types.MethodType(_get_trace, _Failure)
    setattr(_Failure, '_get_trace', substitute_get_trace)  # noqa: B010
    try:
        yield
    finally:
        setattr(_Failure, '_get_trace', unpatched_get_trace)  # noqa: B010


def _get_trace(_self: _Failure) -> Optional[List[FrameInfo]]:
    """
    Function to be used on Monkey Patching.

    This function is the substitute for '_get_trace' method from ``_Failure``
    class on Monkey Patching promoted by
    :func:`returns.primitives.tracing.collect_traces` function.

    We get all the call stack from the current call and return it from the
    third position, to avoid two non-useful calls on the call stack.
    Those non-useful calls are a call to this function and a call to `__init__`
    method from ``_Failure`` class. We're just interested in the call stack
    ending on ``Failure`` function call!

    See also:
        https://github.com/dry-python/returns/issues/409

    """
    current_stack = stack()
    return current_stack[2:]


collect_traces = contextmanager(collect_traces)  # type: ignore
