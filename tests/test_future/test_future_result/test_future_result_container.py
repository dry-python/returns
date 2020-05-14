import pytest

from returns.future import FutureResult
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
    FutureResult.from_value(1),
    FutureResult.from_failure(1),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Rescueable,
    Altable,
    Fixable,
    Unwrapable,
    Unifiable,
    Unitable,
])
def test_protocols(container, protocol):
    """Ensures that Future has all the right protocols."""
    assert isinstance(container, protocol)
