# -*- coding: utf-8 -*-

from typing import Any

from returns.result import Failure, Result, Success


def test_bind():
    """Ensures that bind works."""
    def factory(inner_value: int) -> Result[int, str]:
        if inner_value > 0:
            return Success(inner_value * 2)
        return Failure(str(inner_value))

    input_value = 5
    bound = Success(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == '<Success: 10>'

    input_value = 0
    bound = Success(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == '<Failure: 0>'


def test_left_identity_success():
    """Ensures that left identity works for Success container."""
    def factory(inner_value: int) -> Result[int, Any]:
        return Success(inner_value * 2)

    input_value = 5
    bound = Success(input_value).bind(factory)

    assert bound == factory(input_value)
    assert str(bound) == '<Success: 10>'


def test_left_identity_failure():
    """Ensures that left identity works for Failure container."""
    def factory(inner_value: int) -> Result[Any, TypeError]:
        return Failure(TypeError())

    input_value = 5
    bound = Failure(input_value).bind(factory)

    assert bound == Failure(input_value)
    assert str(bound) == '<Failure: 5>'


def test_rescue_success():
    """Ensures that rescue works for Success container."""
    def factory(inner_value: int) -> Result[int, Any]:
        return Success(inner_value * 2)

    bound = Success(5).rescue(factory)

    assert bound == Success(5)
    assert str(bound) == '<Success: 5>'


def test_rescue_failure():
    """Ensures that rescue works for Failure container."""
    def factory(inner_value: int) -> Result[Any, float]:
        return Failure(float(inner_value + 1))

    expected = 6.0
    bound = Failure(5).rescue(factory)

    assert bound == Failure(expected)
    assert str(bound) == '<Failure: 6.0>'
