from copy import copy, deepcopy

import pytest

from returns.context import ContextIOResult, RequiresContextIOResult
from returns.primitives.exceptions import ImmutableStateError


def test_context_ioresult_immutable():
    """Ensures that helper is immutable."""
    with pytest.raises(ImmutableStateError):
        ContextIOResult().abc = 1


def test_requires_context_result_immutable():
    """Ensures that container is immutable."""
    with pytest.raises(ImmutableStateError):
        RequiresContextIOResult.from_value(1).abc = 1


def test_requires_context_result_immutable_copy():
    """Ensures that helper returns it self when passed to copy function."""
    context_ioresult: ContextIOResult = ContextIOResult()
    assert context_ioresult is copy(context_ioresult)


def test_requires_context_result_immutable_deepcopy():  # noqa: WPS118
    """Ensures that helper returns it self when passed to deepcopy function."""
    requires_context = RequiresContextIOResult.from_value(1)
    assert requires_context is deepcopy(requires_context)
