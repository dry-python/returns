import copy
import sys
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from returns.primitives.container import BaseContainer

_replace = BaseContainer.__replace__


@given(
    st.one_of(
        st.integers(),
        st.floats(allow_nan=False),
        st.text(),
        st.booleans(),
    ),
)
def test_replace_produces_new_container(container_value: Any):
    """Ensures ``__replace__`` produces a new container with the given value."""
    original = BaseContainer(container_value)
    replaced = _replace(original, inner_value=42)
    assert replaced == BaseContainer(42)
    assert type(replaced) is type(original)


@given(
    st.one_of(
        st.integers(),
        st.floats(allow_nan=False),
        st.text(),
        st.booleans(),
    ),
)
def test_replace_preserves_value_when_no_kwargs(container_value: Any):
    """Ensures ``__replace__`` with no kwargs returns equal container."""
    original = BaseContainer(container_value)
    replaced = _replace(original)
    assert replaced == original
    assert replaced is not original


def test_replace_rejects_unknown_fields():
    """Ensures ``__replace__`` raises TypeError on unsupported fields."""
    container = BaseContainer(1)
    with pytest.raises(TypeError, match='Unsupported field names'):
        _replace(container, bad_field=99)


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason='copy.replace requires Python 3.13+',
)
def test_copy_replace():
    """Ensures ``copy.replace`` works on containers in Python 3.13+."""
    original = BaseContainer(10)
    replaced = copy.replace(original, inner_value=20)  # type: ignore[attr-defined]
    assert replaced == BaseContainer(20)
    assert type(replaced) is BaseContainer
