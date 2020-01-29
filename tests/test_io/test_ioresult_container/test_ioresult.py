# -*- coding: utf-8 -*-

import pytest

from returns.io import IOFailure, IOSuccess
from returns.primitives.container import (
    Altable,
    Bindable,
    Fixable,
    Mappable,
    Rescueable,
    Unwrapable,
)


@pytest.mark.parametrize('container', [
    IOSuccess(1),
    IOFailure(1),
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
