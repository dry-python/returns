from functools import wraps
from inspect import iscoroutinefunction

import pytest
from typing_extensions import Final, final

_ERROR_FIELD: Final = '_error_handled'
_ERROR_HANDLERS: Final = (
    'rescue',
    'fix',
)
_ERRORS_COPIERS: Final = (
    'map',
    'alt',
)


@final
class _ReturnsAsserts(object):
    def is_error_handled(self, container) -> bool:
        """Ensures that container has its error handled in the end."""
        return getattr(container, _ERROR_FIELD, False)


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


class _PatchedContainer(object):
    @classmethod
    def containers_to_patch(cls) -> tuple:
        """We need this method so coverage will work correctly."""
        from returns.context import (
            RequiresContextIOResult,
            RequiresContextResult,
        )
        from returns.io import _IOFailure, _IOSuccess
        from returns.result import _Failure, _Success
        from returns.future import FutureResult

        return (
            _Success,
            _Failure,
            _IOSuccess,
            _IOFailure,
            RequiresContextResult,
            RequiresContextIOResult,
            FutureResult,
        )

    @classmethod
    def error_handler(cls, original):
        if iscoroutinefunction(original):
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
        if iscoroutinefunction(original):
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
