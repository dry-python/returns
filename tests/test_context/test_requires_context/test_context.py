from copy import copy, deepcopy

import pytest

from returns.context import Context, RequiresContext
from returns.primitives.exceptions import ImmutableStateError
from returns.primitives.interfaces import Applicative, Bindable, Mappable


@pytest.mark.parametrize('container', [
    RequiresContext(lambda deps: deps),
    RequiresContext.from_value(1),
    Context.ask(),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Applicative,
])
def test_protocols(container, protocol):
    """Ensures that RequiresContext has all the right protocols."""
    assert isinstance(container, protocol)


def test_context_immutable():
    """Ensures that Context is immutable."""
    with pytest.raises(ImmutableStateError):
        Context().abc = 1


def test_context_immutable_copy():
    """Ensures that Context returns it self when passed to copy function."""
    context: Context = Context()
    assert context is copy(context)


def test_context_immutable_deepcopy():
    """Ensures that Context returns it self when passed to deepcopy function."""
    context: Context = Context()
    assert context is deepcopy(context)
