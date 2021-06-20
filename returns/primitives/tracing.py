import types
from contextlib import contextmanager
from inspect import FrameInfo, stack
from typing import (
    Callable,
    ContextManager,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
    overload,
)

from returns.result import Failure

_FunctionType = TypeVar('_FunctionType', bound=Callable)


@overload
def collect_traces() -> ContextManager[None]:
    """Context Manager to active traces collect to the Failures."""


@overload
def collect_traces(function: _FunctionType) -> _FunctionType:
    """Decorator to active traces collect to the Failures."""


def collect_traces(
    function: Optional[_FunctionType] = None,
) -> Union[_FunctionType, ContextManager[None]]:  # noqa: DAR101, DAR201, DAR301
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
    @contextmanager
    def factory() -> Iterator[None]:
        unpatched_get_trace = getattr(Failure, '_get_trace')  # noqa: B009
        substitute_get_trace = types.MethodType(_get_trace, Failure)
        setattr(Failure, '_get_trace', substitute_get_trace)  # noqa: B010
        try:  # noqa: WPS501
            yield
        finally:
            setattr(Failure, '_get_trace', unpatched_get_trace)  # noqa: B010
    return factory()(function) if function else factory()


def _get_trace(_self: Failure) -> Optional[List[FrameInfo]]:
    """
    Function to be used on Monkey Patching.

    This function is the substitute for '_get_trace' method from ``Failure``
    class on Monkey Patching promoted by
    :func:`returns.primitives.tracing.collect_traces` function.

    We get all the call stack from the current call and return it from the
    third position, to avoid two useless calls on the call stack.
    Those useless calls are a call to this function and a call to `__init__`
    method from ``Failure`` class. We're just interested in the call stack
    ending on ``Failure`` function call!

    See also:
        - https://github.com/dry-python/returns/issues/409

    """
    current_stack = stack()
    return current_stack[2:]
