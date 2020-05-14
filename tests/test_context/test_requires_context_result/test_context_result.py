from copy import copy, deepcopy

import pytest

from returns.context import ContextResult, RequiresContextResult
from returns.primitives.exceptions import ImmutableStateError
from returns.primitives.interfaces import (
    Altable,
    Bindable,
    Fixable,
    Mappable,
    Rescueable,
    Unitable,
    Unwrapable,
)
from returns.result import Failure, Success


@pytest.mark.parametrize('container', [
    RequiresContextResult(lambda _: Success(1)),
    RequiresContextResult(lambda _: Failure(1)),
    RequiresContextResult.from_value(1),
    RequiresContextResult.from_failure(1),
    RequiresContextResult.from_result(Success(1)),
    RequiresContextResult.from_result(Failure(1)),
    ContextResult.ask(),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Rescueable,
    Unwrapable,
    Altable,
    Fixable,
    Unitable,
])
def test_protocols(container, protocol):
    """Ensures that RequiresContext has all the right protocols."""
    assert isinstance(container, protocol)


def test_context_result_immutable():
    """Ensures that helper is immutable."""
    with pytest.raises(ImmutableStateError):
        ContextResult().abc = 1


def test_context_result_immutable_copy():
    """Ensures that helper returns it self when passed to copy function."""
    context_result: ContextResult = ContextResult()
    assert context_result is copy(context_result)


def test_context_result_immutable_deepcopy():
    """Ensures that helper returns it self when passed to deepcopy function."""
    context_result: ContextResult = ContextResult()
    assert context_result is deepcopy(context_result)


def test_requires_context_result_immutable():
    """Ensures that container is immutable."""
    with pytest.raises(ImmutableStateError):
        RequiresContextResult.from_value(1).abc = 1
