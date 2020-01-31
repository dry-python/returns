# -*- coding: utf-8 -*-

import pytest

from returns.maybe import Nothing, Some, _Nothing
from returns.primitives.exceptions import ImmutableStateError
from returns.primitives.interfaces import Bindable, Mappable, Unwrapable


@pytest.mark.parametrize('container', [
    Nothing,
    Some(1),
])
@pytest.mark.parametrize('protocol', [
    Bindable,
    Mappable,
    Unwrapable,
])
def test_protocols(container, protocol):
    """Ensures that Maybe has all the right protocols."""
    assert isinstance(container, protocol)


def test_equality():
    """Ensures that containers can be compared."""
    assert Nothing is Nothing  # noqa: WPS312
    assert Nothing == _Nothing() == _Nothing(None) == Some(None)
    assert Some(5) == Some(5)
    assert hash(Some(1))
    assert hash(Nothing)


def test_nonequality():
    """Ensures that containers are not compared to regular values."""
    assert Nothing is not None
    assert Nothing != None  # noqa: E711
    assert _Nothing(None) is not None
    assert _Nothing(None) != None  # noqa: E711
    assert Some(5) != 5 and Some(3) is not Some(3)


def test_is_compare():
    """Ensures that `is` operator works correctly."""
    some_container = Some(1)

    assert Nothing.bind(lambda state: state) is Nothing
    assert some_container is not Some(1)


def test_immutability_failure():
    """Ensures that Failure container is immutable."""
    with pytest.raises(ImmutableStateError):
        Nothing._inner_state = 1  # noqa: WPS437

    with pytest.raises(ImmutableStateError):
        Nothing.missing = 2

    with pytest.raises(ImmutableStateError):
        del Nothing._inner_state  # type: ignore # noqa: WPS420, WPS437

    with pytest.raises(AttributeError):
        Nothing.missing  # type: ignore # noqa: WPS428


def test_immutability_success():
    """Ensures that Success container is immutable."""
    with pytest.raises(ImmutableStateError):
        Some(0)._inner_state = 1  # noqa: WPS437

    with pytest.raises(ImmutableStateError):
        Some(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Some(0)._inner_state  # type: ignore # noqa: WPS420, WPS437

    with pytest.raises(AttributeError):
        Some(1).missing  # type: ignore # noqa: WPS428
