from copy import copy, deepcopy

import pytest

from returns.context import ContextIOResult, RequiresContextIOResult
from returns.io import IOFailure, IOSuccess
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
    RequiresContextIOResult(lambda _: IOSuccess(1)),
    RequiresContextIOResult(lambda _: IOFailure(1)),
    RequiresContextIOResult.from_value(1),
    RequiresContextIOResult.from_failure(1),
    RequiresContextIOResult.from_result(Success(1)),
    RequiresContextIOResult.from_result(Failure(1)),
    RequiresContextIOResult.from_ioresult(IOSuccess(1)),
    RequiresContextIOResult.from_ioresult(IOFailure(1)),
    ContextIOResult.ask(),
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
    context_i_o_result: ContextIOResult = ContextIOResult()
    assert context_i_o_result is copy(context_i_o_result)


def test_requires_context_result_immutable_deepcopy():  # noqa: WPS118
    """Ensures that helper returns it self when passed to deepcopy function."""
    requires_context = RequiresContextIOResult.from_value(1)
    assert requires_context is deepcopy(requires_context)
