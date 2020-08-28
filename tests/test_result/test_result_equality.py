from copy import copy, deepcopy

import pytest

from returns.primitives.exceptions import ImmutableStateError
from returns.result import Failure, Success


def test_equals():
    """Ensures that ``.equals`` method works correctly."""
    inner_value = 1

    assert Success(inner_value).equals(Success(inner_value))
    assert Failure(inner_value).equals(Failure(inner_value))


def test_not_equals():
    """Ensures that ``.equals`` method works correctly."""
    inner_value = 1

    assert not Success(inner_value).equals(Failure(inner_value))
    assert not Success(inner_value).equals(Success(0))
    assert not Failure(inner_value).equals(Success(inner_value))
    assert not Failure(inner_value).equals(Failure(0))


def test_non_equality():
    """Ensures that containers are not compared to regular values."""
    input_value = 5

    assert Failure(input_value) != input_value
    assert Success(input_value) != input_value
    assert Failure(input_value) != Success(input_value)
    assert hash(Failure(1))
    assert hash(Success(1))


def test_is_compare():
    """Ensures that `is` operator works correctly."""
    left = Failure(1)
    right = Success(1)

    assert left.bind(lambda state: state) is left  # type: ignore
    assert right.rescue(lambda state: state) is right  # type: ignore
    assert right is not Success(1)


def test_immutability_failure():
    """Ensures that Failure container is immutable."""
    with pytest.raises(ImmutableStateError):
        Failure(0)._inner_state = 1  # noqa: WPS437

    with pytest.raises(ImmutableStateError):
        Failure(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Failure(0)._inner_state  # type: ignore # noqa: WPS420, WPS437

    with pytest.raises(AttributeError):
        Failure(1).missing  # type: ignore # noqa: WPS428


def test_immutability_success():
    """Ensures that Success container is immutable."""
    with pytest.raises(ImmutableStateError):
        Success(0)._inner_state = 1  # noqa: WPS437

    with pytest.raises(ImmutableStateError):
        Success(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Success(0)._inner_state  # type: ignore # noqa: WPS420, WPS437

    with pytest.raises(AttributeError):
        Success(1).missing  # type: ignore # noqa: WPS428


def test_success_immutable_copy():
    """Ensures that Success returns it self when passed to copy function."""
    success = Success(1)
    assert success is copy(success)


def test_success_immutable_deepcopy():
    """Ensures that Success returns it self when passed to deepcopy function."""
    success = Success(1)
    assert success is deepcopy(success)


def test_failure_immutable_copy():
    """Ensures that Failure returns it self when passed to copy function."""
    failure = Failure(0)
    assert failure is copy(failure)


def test_failure_immutable_deepcopy():
    """Ensures that Failure returns it self when passed to deepcopy function."""
    failure = Failure(0)
    assert failure is deepcopy(failure)
