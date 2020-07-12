from copy import copy, deepcopy

import pytest

from returns.context import Context
from returns.primitives.exceptions import ImmutableStateError


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
