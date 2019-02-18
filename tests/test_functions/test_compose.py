# -*- coding: utf-8 -*-

from returns.functions import compose


def _first(a: int) -> str:
    return str(a)


def _second(b: str) -> bool:
    return bool(b)


def test_function_composition():
    """Ensures that functions can be composed and return type is correct."""
    second_after_first = compose(_first, _second)

    assert second_after_first(1) is True
    assert second_after_first(0) is True
