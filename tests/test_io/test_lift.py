# -*- coding: utf-8 -*-

from returns.io import IO


def _first(argument: int) -> str:
    return str(argument + 1)


def test_lift_io():
    """Ensures that functions can be composed and return type is correct."""
    lifted = IO.lift(_first)

    assert lifted(IO(1)) == IO('2')
