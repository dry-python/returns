import pytest

from returns.future import Future
from returns.primitives.interfaces import Applicative, Bindable, Mappable


@pytest.mark.parametrize('container', [
    Future.from_value(''),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Applicative,
])
def test_protocols(container, protocol):
    """Ensures that Future has all the right protocols."""
    assert isinstance(container, protocol)
