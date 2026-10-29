import copy
import sys
from typing import Any

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

from returns.io import IO
from returns.maybe import Maybe, Nothing, Some
from returns.primitives.container import BaseContainer
from returns.result import Failure, Result, Success


@given(st.integers(), st.integers())
def test_base_container_replace_inner_value(initial: int, new_val: int):
    """Ensures that __replace__ updates inner_value properly."""
    container = BaseContainer(initial)
    replaced = container.__replace__(inner_value=new_val)

    assert replaced != container or initial == new_val
    assert replaced._inner_value == new_val
    assert container._inner_value == initial
    assert isinstance(replaced, BaseContainer)


@given(st.text(), st.text())
def test_base_container_replace_underscore_inner_value(initial: str, new_val: str):
    """Ensures that __replace__ accepts _inner_value keyword argument."""
    container = BaseContainer(initial)
    replaced = container.__replace__(_inner_value=new_val)

    assert replaced._inner_value == new_val
    assert container._inner_value == initial


def test_base_container_replace_no_args():
    """Ensures that __replace__ without arguments returns an equal copy."""
    container = BaseContainer(42)
    replaced = container.__replace__()

    assert replaced == container
    assert replaced is not container


def test_base_container_replace_unexpected_kwarg():
    """Ensures that unexpected kwargs raise TypeError."""
    container = BaseContainer(42)
    with pytest.raises(TypeError, match="unexpected keyword argument 'invalid'"):
        container.__replace__(invalid=True)


def test_base_container_replace_multiple_values():
    """Ensures providing both inner_value and _inner_value raises TypeError."""
    container = BaseContainer(42)
    with pytest.raises(TypeError, match="multiple values for inner value"):
        container.__replace__(inner_value=1, _inner_value=2)


@pytest.mark.parametrize(
    ('container', 'new_value', 'expected'),
    [
        (Success(1), 2, Success(2)),
        (Failure('err1'), 'err2', Failure('err2')),
        (Some('a'), 'b', Some('b')),
        (IO(100), 200, IO(200)),
    ],
)
def test_concrete_containers_replace(container: Any, new_value: Any, expected: Any):
    """Ensures concrete containers support __replace__."""
    replaced = container.__replace__(inner_value=new_value)
    assert replaced == expected
    assert isinstance(replaced, type(container))


def test_nothing_replace():
    """Ensures Nothing supports __replace__ when value remains None."""
    assert Nothing.__replace__() is Nothing
    assert Nothing.__replace__(inner_value=None) is Nothing
    assert Nothing.__replace__(_inner_value=None) is Nothing

    with pytest.raises(TypeError, match="Cannot replace inner_value on Nothing"):
        Nothing.__replace__(inner_value=42)

    with pytest.raises(TypeError, match="Cannot replace _inner_value on Nothing"):
        Nothing.__replace__(_inner_value=42)


@pytest.mark.skipif(sys.version_info < (3, 13), reason="copy.replace was added in Python 3.13")
def test_copy_replace_standard_library():
    """Ensures stdlib copy.replace works seamlessly on Python 3.13+."""
    replace = getattr(copy, "replace")
    s = Success(1)
    replaced = replace(s, inner_value=2)
    assert replaced == Success(2)
