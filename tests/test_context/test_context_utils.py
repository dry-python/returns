# -*- coding: utf-8 -*-

from returns.context import Context


def test_context_ask():
    """Ensures that ``ask`` method works correctly."""
    assert Context[int].ask()(1) == 1
    assert Context[str].ask()('a') == 'a'


def test_context_unit():
    """Ensures that ``unit`` method works correctly."""
    assert Context.unit(1)(Context.Empty) == 1
    assert Context[int].unit(2)(1) == 2
