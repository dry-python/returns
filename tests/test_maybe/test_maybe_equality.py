from copy import copy, deepcopy

import pytest

from returns.maybe import Nothing, Some, _Nothing  # noqa: PLC2701
from returns.primitives.exceptions import ImmutableStateError


def test_equals():
    """Ensures that ``.equals`` method works correctly."""
    inner_value = 1

    assert Some(inner_value).equals(Some(inner_value))
    assert Nothing.equals(Nothing)


def test_not_equals():
    """Ensures that ``.equals`` method works correctly."""
    assert not Some(1).equals(Nothing)
    assert not Some(1).equals(Some(0))
    assert not Nothing.equals(Some(1))


def test_equality():
    """Ensures that containers can be compared."""
    assert Nothing is Nothing  # noqa: PLR0124, WPS312
    assert Nothing == _Nothing() == _Nothing(None)
    assert Some(5) == Some(5)
    assert hash(Some(1))
    assert hash(Nothing)


def test_nonequality():
    """Ensures that containers are not compared to regular values."""
    assert Nothing is not None
    assert Nothing != None  # noqa: E711
    assert _Nothing(None) != None  # noqa: E711
    assert Some(5) != 5
    assert Some(3) is not Some(3)


def test_is_compare():
    """Ensures that `is` operator works correctly."""
    some_container = Some(1)

    assert Nothing.bind(lambda state: state) is Nothing
    assert some_container is not Some(1)


def test_immutability_failure():
    """Ensures that Failure container is immutable."""
    with pytest.raises(ImmutableStateError):
        Nothing._inner_state = 1  # noqa: SLF001

    with pytest.raises(ImmutableStateError):
        Nothing.missing = 2

    with pytest.raises(ImmutableStateError):
        del Nothing._inner_state  # type: ignore # noqa: SLF001, WPS420

    with pytest.raises(AttributeError):
        Nothing.missing  # type: ignore # noqa: B018


def test_immutability_success():
    """Ensures that Success container is immutable."""
    with pytest.raises(ImmutableStateError):
        Some(0)._inner_state = 1  # noqa: SLF001

    with pytest.raises(ImmutableStateError):
        Some(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Some(0)._inner_state  # type: ignore # noqa: SLF001, WPS420

    with pytest.raises(AttributeError):
        Some(1).missing  # type: ignore # noqa: B018


def test_success_immutable_copy():
    """Ensures that Success returns it self when passed to copy function."""
    some = Some(1)  # noqa: WPS110
    assert some is copy(some)


def test_success_immutable_deepcopy():
    """Ensures that Success returns it self when passed to deepcopy function."""
    some = Some(1)  # noqa: WPS110
    assert some is deepcopy(some)


def test_failure_immutable_copy():
    """Ensures that Failure returns it self when passed to copy function."""
    nothing = _Nothing()
    assert nothing is copy(nothing)


def test_failure_immutable_deepcopy():
    """Ensures that Failure returns it self when passed to deepcopy function."""
    nothing = _Nothing()
    assert nothing is deepcopy(nothing)
