import inspect
import sys
from collections.abc import Callable, Generator, Iterator, Mapping
from contextlib import ExitStack, contextmanager
from functools import partial, wraps
from types import FrameType
from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, Union, final
from unittest import mock

import pytest

if TYPE_CHECKING:
    from returns.interfaces.specific.result import ResultLikeN

# We keep track of errors handled by keeping a mapping of <object id>: object.
# If an error is handled, it is in the mapping.
# If it isn't in the mapping, the error is not handled.
#
# Note only storing object IDs would not work, as objects may be GC'ed
# and their object id assigned to another object.
# Also, the object itself cannot be (in) the key because
# (1) we cannot always assume hashability and
# (2) we need to track the object identity, not its value
_ErrorsHandled: TypeAlias = dict[int, Any]

_FunctionType = TypeVar('_FunctionType', bound=Callable)
_ReturnsResultType = TypeVar(
    '_ReturnsResultType',
    bound=Union['ResultLikeN', Callable[..., 'ResultLikeN']],
)


@final
class ReturnsAsserts:
    """Class with helpers assertions to check containers."""

    __slots__ = ('_errors_handled',)

    def __init__(self, errors_handled: _ErrorsHandled) -> None:
        """Constructor for this type."""
        self._errors_handled = errors_handled

    @staticmethod  # noqa: WPS602
    def assert_equal(  # noqa: WPS602
        first,
        second,
        *,
        deps=None,
        backend: str = 'asyncio',
    ) -> None:
        """Can compare two containers even with extra calling and awaiting."""
        from returns.primitives.asserts import assert_equal  # noqa: PLC0415

        assert_equal(first, second, deps=deps, backend=backend)

    def is_error_handled(self, container) -> bool:
        """Ensures that container has its error handled in the end."""
        return id(container) in self._errors_handled

    @staticmethod  # noqa: WPS602
    @contextmanager
    def assert_trace(  # noqa: WPS602
        trace_type: _ReturnsResultType,
        function_to_search: _FunctionType,
    ) -> Generator[None]:
        """
        Ensures that a given function was called during execution.

        Use it to determine where the failure happened.
        """
        old_tracer = sys.gettrace()
        sys.settrace(partial(_trace_function, trace_type, function_to_search))

        try:
            yield
        except _DesiredFunctionFound:
            pass  # noqa: WPS420
        else:
            pytest.fail(
                f'No container {type(trace_type).__name__} was created',
            )
        finally:
            sys.settrace(old_tracer)


def _trace_function(
    trace_type: _ReturnsResultType,
    function_to_search: _FunctionType,
    frame: FrameType,
    event: str,
    arg: Any,
) -> None:
    is_desired_type_call = event == 'call' and (
        # Some containers is created through functions and others
        # is created directly using class constructors!
        # The first line covers when it's created through a function
        # The second line covers when it's created through a
        # class constructor
        frame.f_code is getattr(trace_type, '__code__', None)
        or frame.f_code is getattr(trace_type.__init__, '__code__', None)  # type: ignore[misc]
    )
    if is_desired_type_call:
        current_call_stack = inspect.stack()
        for frame_info in current_call_stack:
            if _is_function_frame(function_to_search, frame_info.frame):
                raise _DesiredFunctionFound


def _is_function_frame(function: _FunctionType, frame: FrameType) -> bool:
    function_code = getattr(function, '__code__', None)
    if frame.f_code is not function_code:
        return False

    closure = getattr(function, '__closure__', None)
    if not closure:
        # Fast path: without a closure the code object is enough,
        # so we don't touch the frame's locals at all:
        return True

    # Functions created by the same decorator share the same code object,
    # so we also compare their closure variables to tell them apart:
    frame_locals = frame.f_locals
    return all(
        frame_locals[name] is cell.cell_contents
        for name, cell in zip(function_code.co_freevars, closure, strict=True)
        if name in frame_locals
    )


class _DesiredFunctionFound(BaseException):  # noqa: WPS418
    """Exception to raise when expected function is found."""


def pytest_configure(config) -> None:
    """
    Hook to be executed on import.

    We use it define custom markers.
    """
    config.addinivalue_line(
        'markers',
        (
            'returns_lawful: all tests under `check_all_laws` '
            + 'is marked this way, '
            + 'use `-m "not returns_lawful"` to skip them.'
        ),
    )


@pytest.fixture
def returns() -> Iterator[ReturnsAsserts]:
    """Returns class with helpers assertions to check containers."""
    with _spy_error_handling() as errors_handled:
        yield ReturnsAsserts(errors_handled)


@contextmanager
def _spy_error_handling() -> Generator[_ErrorsHandled]:
    """Track error handling of containers."""
    errs: _ErrorsHandled = {}
    with ExitStack() as cleanup:
        for container in _containers_to_patch():
            for method, patch in _error_handling_patchers().items():
                cleanup.enter_context(
                    mock.patch.object(
                        container,
                        method,
                        patch(getattr(container, method), errs=errs),
                    )
                )
        yield errs


# delayed imports are needed to prevent messing up coverage
def _containers_to_patch() -> list:
    from returns.context import (  # noqa: PLC0415
        RequiresContextFutureResult,
        RequiresContextIOResult,
        RequiresContextResult,
    )
    from returns.future import FutureResult  # noqa: PLC0415
    from returns.io import IOFailure, IOSuccess  # noqa: PLC0415
    from returns.result import Failure, Success  # noqa: PLC0415

    return [
        Success,
        Failure,
        IOSuccess,
        IOFailure,
        RequiresContextResult,
        RequiresContextIOResult,
        RequiresContextFutureResult,
        FutureResult,
    ]


def _error_handling_patchers() -> Mapping[str, Callable]:
    from returns.primitives.compat import make_immutable  # noqa: PLC0415

    return make_immutable({
        'lash': _patched_error_handler,
        'map': _patched_error_copier,
        'alt': _patched_error_copier,
    })


def _patched_error_handler(
    original: _FunctionType,
    errs: _ErrorsHandled,
) -> _FunctionType:
    if inspect.iscoroutinefunction(original):

        async def async_wrapper(self, *args, **kwargs):
            original_result = await original(self, *args, **kwargs)
            errs[id(original_result)] = original_result
            return original_result

        return wraps(original)(async_wrapper)  # type: ignore

    def sync_wrapper(self, *args, **kwargs):
        original_result = original(self, *args, **kwargs)
        errs[id(original_result)] = original_result
        return original_result

    return wraps(original)(sync_wrapper)  # type: ignore


def _patched_error_copier(
    original: _FunctionType,
    errs: _ErrorsHandled,
) -> _FunctionType:
    if inspect.iscoroutinefunction(original):

        async def async_wrapper(self, *args, **kwargs):
            original_result = await original(self, *args, **kwargs)
            if id(self) in errs:
                errs[id(original_result)] = original_result
            return original_result

        return wraps(original)(async_wrapper)  # type: ignore

    def sync_wrapper(self, *args, **kwargs):
        original_result = original(self, *args, **kwargs)
        if id(self) in errs:
            errs[id(original_result)] = original_result
        return original_result

    return wraps(original)(sync_wrapper)  # type: ignore
