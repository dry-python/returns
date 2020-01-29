# -*- coding: utf-8 -*-

import pytest

from returns.context import Context, RequiresContext
from returns.primitives.container import Bindable, Mappable


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


def test_context_map():
    """Ensures that RequiresContext container supports ``.map()`` method."""
    context: RequiresContext[int, str] = RequiresContext.from_value(
        1.0,
    ).map(
        str,
    )
    assert context(3) == RequiresContext.from_value(
        '1.0',
    )(RequiresContext.empty)


def test_context_bind():
    """Ensures that RequiresContext container supports ``.bind()`` method."""
    def factory(number: float) -> RequiresContext[int, str]:
        return RequiresContext(lambda deps: str(number + deps))

    context: RequiresContext[int, str] = RequiresContext.from_value(
        1.0,
    ).bind(
        factory,
    )
    assert context(3) == RequiresContext.from_value(
        '4.0',
    )(RequiresContext.empty)
