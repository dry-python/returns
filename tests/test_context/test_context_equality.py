# -*- coding: utf-8 -*-

from typing import Callable

from returns.context import Context, RequiresContext


def _same_function(some_arg: int) -> Callable[[float], float]:
    return lambda other: other / some_arg


def test_equality():
    """Ensures that containers can be compared."""
    assert RequiresContext(_same_function) == RequiresContext(_same_function)
    assert Context[int].ask() == Context[int].ask()
    assert Context[int].ask() == Context.ask()
    assert Context.ask() == Context.ask()


def test_nonequality():
    """Ensures that containers can be compared."""
    assert RequiresContext(_same_function) != RequiresContext(str)
    assert Context[int].unit(1) != Context[int].unit(1)
    assert Context.unit(1) != Context[int].unit(1)
    assert Context.unit(1) != Context.unit(1)
