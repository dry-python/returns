import types
from contextlib import contextmanager
from inspect import FrameInfo, stack
from typing import List

from returns.result import _Failure


@contextmanager
def collect_traces():
    """
    Context Manager/Decorator to active traces collect to the Failures.

    .. code:: python

        >>> from inspect import FrameInfo

        >>> from returns.io import IOResult
        >>> from returns.result import Result
        >>> from returns.tracing import collect_traces

        >>> with collect_traces():
        ...     traced_failure = Result.from_failure('Traced Failure')
        >>> non_traced_failure = IOResult.from_failure('Non Traced Failure')

        >>> assert non_traced_failure.trace is None
        >>> assert isinstance(traced_failure.trace, list)
        >>> assert isinstance(traced_failure.trace[0], FrameInfo)

    """
    unpatched_get_trace = getattr(_Failure, '_get_trace')  # noqa: B009
    substitute_get_trace = types.MethodType(_get_trace, _Failure)
    setattr(_Failure, '_get_trace', substitute_get_trace)  # noqa: B010
    try:
        yield
    finally:
        setattr(_Failure, '_get_trace', unpatched_get_trace)  # noqa: B010


def _get_trace(_self) -> List[FrameInfo]:
    current_stack = stack()
    return current_stack[2:]
