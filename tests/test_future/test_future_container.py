import pytest

from returns.future import Future
from returns.primitives.interfaces import Bindable, Instanceable, Mappable


@pytest.mark.parametrize('container', [
    Future.from_value(''),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Instanceable,
])
def test_protocols(container, protocol):
    """Ensures that Future has all the right protocols."""
    assert isinstance(container, protocol)
