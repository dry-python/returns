# -*- coding: utf-8 -*-

import pytest

from returns.context import Context, RequiresContext
from returns.primitives.container import Bindable, Mappable
from returns.primitives.exceptions import ImmutableStateError


@pytest.mark.parametrize('container', [
    RequiresContext(lambda deps: deps),
    RequiresContext.from_value(1),
    Context.ask(),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
])
def test_protocols(container, protocol):
    """Ensures that RequiresContext has all the right protocols."""
    assert isinstance(container, protocol)


def test_context_immutable():
    """Ensures that RequiresContext container supports ``.map()`` method."""
    with pytest.raises(ImmutableStateError):
        Context().a = 1
