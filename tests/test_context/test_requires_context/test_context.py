# -*- coding: utf-8 -*-

import pytest

from returns.context import Context, RequiresContext
from returns.primitives.exceptions import ImmutableStateError
from returns.primitives.interfaces import Bindable, Instanceable, Mappable


@pytest.mark.parametrize('container', [
    RequiresContext(lambda deps: deps),
    RequiresContext.from_value(1),
    Context.ask(),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Instanceable,
])
def test_protocols(container, protocol):
    """Ensures that RequiresContext has all the right protocols."""
    assert isinstance(container, protocol)


def test_context_immutable():
    """Ensures that RequiresContext container supports ``.map()`` method."""
    with pytest.raises(ImmutableStateError):
        Context().abc = 1
