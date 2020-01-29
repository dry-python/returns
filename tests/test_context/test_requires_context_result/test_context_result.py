# -*- coding: utf-8 -*-

import pytest

from returns.context import ContextResult, RequiresContextResult
from returns.primitives.container import (
    Altable,
    Bindable,
    Fixable,
    Mappable,
    Rescueable,
    Unwrapable,
)
from returns.primitives.exceptions import ImmutableStateError
from returns.result import Failure, Success


@pytest.mark.parametrize('container', [
    RequiresContextResult(lambda _: Success(1)),
    RequiresContextResult(lambda _: Failure(1)),
    RequiresContextResult.from_success(1),
    RequiresContextResult.from_failure(1),
    ContextResult.ask(),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Rescueable,
    Unwrapable,
    Altable,
    Fixable,
])
def test_protocols(container, protocol):
    """Ensures that RequiresContext has all the right protocols."""
    assert isinstance(container, protocol)


def test_context_result_immutable():
    """Ensures that RequiresContext container supports ``.map()`` method."""
    with pytest.raises(ImmutableStateError):
        ContextResult().a = 1
