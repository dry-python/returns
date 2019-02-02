# -*- coding: utf-8 -*-

import pytest

from returns.either import Left, Right
from returns.primitives.exceptions import ImmutableStateError


def test_nonequality():
    """Ensures that monads are not compared to regular values."""
    input_value = 5

    assert Left(input_value) != input_value
    assert Right(input_value) != input_value
    assert Left(input_value) != Right(input_value)


def test_is_compare():
    """Ensures that `is` operator works correctly."""
    left = Left(1)
    right = Right(1)

    assert left.bind(lambda state: state) is left
    assert right.ebind(lambda state: state) is right
    assert right is not Right(1)


def test_immutability_failure():
    """Ensures that Failure monad is immutable."""
    with pytest.raises(ImmutableStateError):
        Left(0)._inner_state = 1  # noqa: Z441

    with pytest.raises(ImmutableStateError):
        Left(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Left(0)._inner_state  # type: ignore # noqa: Z420, Z441

    with pytest.raises(AttributeError):
        Left(1).missing  # type: ignore # noqa: Z444


def test_immutability_success():
    """Ensures that Success monad is immutable."""
    with pytest.raises(ImmutableStateError):
        Right(0)._inner_state = 1  # noqa: Z441

    with pytest.raises(ImmutableStateError):
        Right(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Right(0)._inner_state  # type: ignore # noqa: Z420, Z441

    with pytest.raises(AttributeError):
        Right(1).missing  # type: ignore # noqa: Z444
