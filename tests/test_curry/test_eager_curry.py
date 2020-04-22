from functools import partial

import pytest

from returns.curry import eager_curry


PartialType = type(partial(lambda x: x))


def test_no_args():
    @eager_curry
    def func():
        return 1

    assert func() == 1


def test_one_arg():
    @eager_curry
    def func(a):
        return a

    assert type(func()) is PartialType
    assert func(1) == 1
    assert func()(1) == 1
    with pytest.raises(TypeError):
        func(1, 2)
    with pytest.raises(TypeError):
        func(1)(2)


def test_two_args():
    @eager_curry
    def func(a, b):
        return a + b

    assert type(func()) is PartialType
    assert type(func(1)) is PartialType
    assert func(1)(2) == 3
    assert func(1, 2) == 3
    assert func()(1)(2) == 3
    assert func()(1, 2) == 3
    assert func()(1, b=2) == 3
    assert func()(a=1, b=2) == 3
    assert func()(b=1, a=2) == 3
    with pytest.raises(TypeError):
        func(1, 2, 3)
    with pytest.raises(TypeError):
        func(1, c=2)
    with pytest.raises(TypeError):
        func(1)(c=2)
    with pytest.raises(TypeError):
        func(1)(2)(3)


def test_star_args():
    @eager_curry
    def func(*args):
        return sum(args)

    assert func() == 0
    assert func(1) == 1
    assert func(1, 2) == 3
    assert func(1, 2, 3) == 6

    with pytest.raises(TypeError):
        func(a=1)
    with pytest.raises(TypeError):
        func(1, b=2)


def test_arg_and_star_args():
    @eager_curry
    def func(arg, *args):
        return arg + sum(args)

    assert type(func()) is PartialType
    assert func(1) == 1
    assert func(1, 2) == 3
    assert func(1, 2, 3) == 6


def test_star_kwargs():
    @eager_curry
    def func(**kwargs):
        return sorted(kwargs.items())

    assert func() == []
    assert func(a=1) == [('a', 1)]
    assert func(a=1, b=2) == [('a', 1), ('b', 2)]

    with pytest.raises(TypeError):
        func(1)
    with pytest.raises(TypeError):
        func(1, b=2)
