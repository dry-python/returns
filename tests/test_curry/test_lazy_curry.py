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

    # rewrite
    assert func(a=1)(a=2)() == 2


def test_two_args():
    @lazy_curry
    def func(a, b):
        return (a, b)

    assert func(1)(2)() == (1, 2)
    assert func(1, 2)() == (1, 2)

    assert func(1, b=2)() == (1, 2)
    assert func(a=1, b=2)() == (1, 2)
    assert func(b=1, a=2)() == (2, 1)

    assert func(b=1)(a=2)() == (2, 1)
    assert func(a=1)(b=2)() == (1, 2)
    assert func(1)(b=2)() == (1, 2)
    assert func(b=1)(2)() == (2, 1)

    with pytest.raises(TypeError):
        func(1, 2, 3)()
    with pytest.raises(TypeError):
        func(1, c=2)()
    with pytest.raises(TypeError):
        func(1)(c=2)()
    with pytest.raises(TypeError):
        func(1)(2)(3)()


def test_star_args():
    @lazy_curry
    def func(*args):
        return args

    assert func() == ()
    assert func(1)() == (1, )
    assert func(1, 2)() == (1, 2)
    assert func(1, 2, 3)() == (1, 2, 3)

    assert func(1)(2)() == (1, 2)
    assert func(1)(2)(3)() == (1, 2, 3)
    assert func(1)(2, 3)() == (1, 2, 3)
    assert func(1, 2)(3)() == (1, 2, 3)

    with pytest.raises(TypeError):
        func(a=1)()
    with pytest.raises(TypeError):
        func(1)(b=2)()


def test_star_kwargs():
    @lazy_curry
    def func(**kwargs):
        return sorted(kwargs.items())

    assert func() == []
    assert func(a=1)() == [('a', 1)]
    assert func(a=1, b=2)() == [('a', 1), ('b', 2)]
    assert func(a=1)(b=2)() == [('a', 1), ('b', 2)]
    assert func(a=1, b=2)(b=3)() == [('a', 1), ('b', 3)]
    assert func(b=2)(a=1)() == [('a', 1), ('b', 2)]


def test_arg_star_kwargs():
    @lazy_curry
    def func(a, **kwargs):
        return [('a', a)] + sorted(kwargs.items())

    assert func(1)() == [('a', 1)]
    assert func(a=1)() == [('a', 1)]
    assert func(1, b=2)() == [('a', 1), ('b', 2)]
    assert func(1)(b=2)() == [('a', 1), ('b', 2)]
    assert func(a=1)(b=2)() == [('a', 1), ('b', 2)]
    assert func(c=3, a=1)(b=2)() == [('a', 1), ('b', 2), ('c', 3)]

    with pytest.raises(TypeError):
        func()


def test_arg_names_conflict():
    @lazy_curry
    def func(first, self, args, kwargs):
        return (first, self, args, kwargs)

    assert type(func(1)) is partial
    assert type(func(1)(self=2)) is partial
    assert type(func(1)(self=2)(args=3)) is partial
    assert type(func(1)(self=2)(args=3)(kwargs=4)) is partial
    assert func(1)(self=2)(args=3)(kwargs=4)() == (1, 2, 3, 4)
