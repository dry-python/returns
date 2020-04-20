import pytest

from returns.io import IOFailure, IOSuccess
from returns.primitives.interfaces import (
    Altable,
    Bindable,
    Fixable,
    Mappable,
    Rescueable,
    Unifiable,
    Unitable,
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
    Unitable,
    Unifiable,
])
def test_protocols(container, protocol):
    """Ensures that RequiresContext has all the right protocols."""
    assert isinstance(container, protocol)
