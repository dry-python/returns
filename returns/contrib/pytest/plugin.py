import inspect
import sys
from contextlib import contextmanager
from functools import partial, wraps
from types import FrameType
from typing import TYPE_CHECKING, Any, Callable, Iterator, TypeVar

import pytest
from typing_extensions import Final, final

if TYPE_CHECKING:
    from returns.interfaces.specific.result import ResultBasedN

_ERROR_FIELD: Final = '_error_handled'
_ERROR_HANDLERS: Final = (
    'rescue',
)
_ERRORS_COPIERS: Final = (
    'map',
    'alt',
)

_FunctionType = TypeVar('_FunctionType', bound=Callable)
_ResultCallableType = TypeVar(
    '_ResultCallableType', bound=Callable[..., 'ResultBasedN'],
)


class _DesiredFunctionFound(RuntimeError):
    """Exception to raise when expected function is found."""


@final
class _ReturnsAsserts(object):
    """Class with helpers assertions to check containers."""

    __slots__ = ()

    def is_error_handled(self, container) -> bool:
        """Ensures that container has its error handled in the end."""
        return bool(getattr(container, _ERROR_FIELD, False))

    @contextmanager
    def has_trace(
        self,
        trace_type: _ResultCallableType,
        function_to_search: _FunctionType,
    ) -> Iterator[None]:
        old_tracer = sys.gettrace()
        sys.settrace(partial(_trace_function, trace_type, function_to_search))

        try:
            yield
        except _DesiredFunctionFound:
            pass  # noqa: WPS420
        else:
            pytest.fail(
                'No container {0} was created'.format(trace_type.__name__),
            )
        finally:
            sys.settrace(old_tracer)


@pytest.fixture(scope='session')
def _patch_containers() -> None:
    """
    Fixture to add test specifics into our containers.

    Currently we inject:

    - Error handling state, this is required to test that ``Result``-based
      containers do handle errors

    Even more things to come!
    """
    _patch_error_handling(_ERROR_HANDLERS, _PatchedContainer.error_handler)
    _patch_error_handling(_ERRORS_COPIERS, _PatchedContainer.copy_handler)


@pytest.fixture(scope='session')
def returns(_patch_containers) -> _ReturnsAsserts:  # noqa: WPS442
    """Returns our own class with helpers assertions to check containers."""
    return _ReturnsAsserts()


def _patch_error_handling(methods, patch_handler) -> None:
    for container in _PatchedContainer.containers_to_patch():
        for method in methods:
            original = getattr(container, method, None)
            if original:
                setattr(container, method, patch_handler(original))


def _trace_function(
    trace_type: _ResultCallableType,
    function_to_search: _FunctionType,
    frame: FrameType,
    event: str,
    arg: Any,
) -> None:
    is_desired_type_call = (
        event == 'call' and frame.f_code is trace_type.__code__
    )
    if is_desired_type_call:
        current_call_stack = inspect.stack()
        function_to_search_code = getattr(function_to_search, '__code__', None)
        for frame_info in current_call_stack:
            if function_to_search_code is frame_info.frame.f_code:
                raise _DesiredFunctionFound()


@final
class _PatchedContainer(object):
    """Class with helper methods to patched containers."""

    __slots__ = ()

    @classmethod
    def containers_to_patch(cls) -> tuple:
        """We need this method so coverage will work correctly."""
        from returns.context import (
            RequiresContextIOResult,
            RequiresContextResult,
            RequiresContextFutureResult,
        )
        from returns.future import FutureResult
        from returns.io import _IOFailure, _IOSuccess
        from returns.result import _Failure, _Success

        return (
            _Success,
            _Failure,
            _IOSuccess,
            _IOFailure,
            RequiresContextResult,
            RequiresContextIOResult,
            RequiresContextFutureResult,
            FutureResult,
        )

    @classmethod
    def error_handler(cls, original):
        if inspect.iscoroutinefunction(original):
            async def factory(self, *args, **kwargs):
                original_result = await original(self, *args, **kwargs)
                object.__setattr__(
                    original_result, _ERROR_FIELD, True,  # noqa: WPS425
                )
                return original_result
        else:
            def factory(self, *args, **kwargs):
                original_result = original(self, *args, **kwargs)
                object.__setattr__(
                    original_result, _ERROR_FIELD, True,  # noqa: WPS425
                )
                return original_result
        return wraps(original)(factory)

    @classmethod
    def copy_handler(cls, original):
        if inspect.iscoroutinefunction(original):
            async def factory(self, *args, **kwargs):
                original_result = await original(self, *args, **kwargs)
                object.__setattr__(
                    original_result,
                    _ERROR_FIELD,
                    getattr(self, _ERROR_FIELD, False),
                )
                return original_result
        else:
            def factory(self, *args, **kwargs):
                original_result = original(self, *args, **kwargs)
                object.__setattr__(
                    original_result,
                    _ERROR_FIELD,
                    getattr(self, _ERROR_FIELD, False),
                )
                return original_result
        return wraps(original)(factory)
