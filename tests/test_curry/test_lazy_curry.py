from functools import partial
from inspect import getdoc

import pytest

from returns.curry import lazy_curry


def test_docstring():
    @lazy_curry
    def func(a, b):
        """Papa Emeritus II
        """
        return a + b

    assert getdoc(func).strip() == "Papa Emeritus II"


def test_immutable():
    """Check that arguments from previous calls are immutable
    """
    @lazy_curry
    def func(a, b):
        return (a, b)

    cached = func(a=1)
    assert cached(a=2, b=3)() == (2, 3)
    assert cached(b=3)() == (1, 3)


def test_no_args():
    @lazy_curry
    def func():
        return 1

    assert func() == 1


def test_one_arg():
    @lazy_curry
    def func(a):
        return a

    assert type(func(1)) is partial
    # no TypeErrors until the explicit call
    assert type(func(1, 2)) is partial
    assert type(func(1)(2)) is partial
    assert type(func(1, b=2)) is partial

    assert func(1)() == 1
    assert func(a=1)() == 1
    with pytest.raises(TypeError):
        func(1, 2)()
    with pytest.raises(TypeError):
        func(1)(2)()
