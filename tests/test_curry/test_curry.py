from inspect import getdoc
from typing import List, Tuple

import pytest

from returns.curry import curry


def test_docstring():
    """Ensures that we preserve docstrings from curried function."""

    @curry
    def factory(a, b):
        """Some docstring."""

    assert getdoc(factory) == 'Some docstring.'


def test_immutable():
    """Check that arguments from previous calls are immutable."""

    @curry
    def factory(a: int, b: int) -> Tuple[int, int]:
        return (a, b)

    cached = factory(a=1)
    assert cached(b=2) == (1, 2)
    assert cached(b=3) == (1, 3)


def test_no_args():
    """Ensures that it is possible to curry a function with empty args."""

    @curry
    def factory() -> int:
        return 1

    assert factory() == 1


def test_one_arg():
    """Ensures that it is possible to curry a function with one arg."""

    @curry
    def factory(a: int) -> int:
        return a

    assert factory(1) == 1
    assert factory(a=1) == 1
    with pytest.raises(TypeError):
        factory(b=2)  # type: ignore
    with pytest.raises(TypeError):
        factory(1, 2)  # type: ignore
    with pytest.raises(TypeError):
        factory(1)(2)  # type: ignore


def test_two_args():
    """Ensures that it is possible to curry a function with two args."""

    @curry
    def factory(a: int, b: int) -> Tuple[int, int]:
        return (a, b)

    assert factory(1)(2) == (1, 2)
    assert factory(1, 2) == (1, 2)

    assert factory(1, b=2) == (1, 2)
    assert factory(a=1, b=2) == (1, 2)
    assert factory(b=1, a=2) == (2, 1)

    assert factory(a=1)(b=2) == (1, 2)
    assert factory(1)(b=2) == (1, 2)

    with pytest.raises(TypeError):
        factory(1, 2, 3)  # type: ignore
    with pytest.raises(TypeError):
        factory(1, c=2)  # type: ignore
    with pytest.raises(TypeError):
        factory(1)(c=2)  # type: ignore
    with pytest.raises(TypeError):
        factory(1)(2)(3)  # type: ignore


def test_star_args():
    """Ensures that it is possible to curry a function with ``*args``."""

    @curry
    def factory(*args: int) -> int:
        return sum(args)

    assert factory() == 0
    assert factory(1) == 1
    assert factory(1, 2) == 3
    assert factory(1, 2, 3) == 6

    with pytest.raises(TypeError):
        factory(a=1)
    with pytest.raises(TypeError):
        factory(1, b=2)
    with pytest.raises(TypeError):
        factory(1)(2)


def test_arg_and_star_args():
    """Ensures that it is possible to curry a function with ``*args``."""

    @curry
    def factory(arg: int, *args: int) -> int:
        return arg + sum(args)

    assert factory(1) == 1
    assert factory(1, 2) == 3
    assert factory(1, 2, 3) == 6
    with pytest.raises(TypeError):
        assert factory(1)(2, 3) == 6


def test_star_kwargs():
    """Ensures that it is possible to curry a function with ``**kwargs``."""

    @curry
    def factory(**kwargs: int) -> List[Tuple[str, int]]:
        return sorted(kwargs.items())

    assert factory() == []
    assert factory(a=1) == [('a', 1)]
    assert factory(a=1, b=2) == [('a', 1), ('b', 2)]

    with pytest.raises(TypeError):
        factory(1)
    with pytest.raises(TypeError):
        factory(1, b=2)


def test_arg_star_kwargs():
    @curry
    def factory(a: int, **kwargs: int) -> List[Tuple[str, int]]:
        return [('a', a)] + sorted(kwargs.items())

    assert factory(1) == [('a', 1)]
    assert factory(1) == [('a', 1)]
    assert factory(a=1) == [('a', 1)]
    assert factory(a=1) == [('a', 1)]
    assert factory(1, b=2) == [('a', 1), ('b', 2)]
    assert factory(a=1, b=2) == [('a', 1), ('b', 2)]
    assert factory(c=3, a=1, b=2) == [('a', 1), ('b', 2), ('c', 3)]

    with pytest.raises(TypeError):
        factory(1, 2)
    with pytest.raises(TypeError):
        factory(1, a=2)
    with pytest.raises(TypeError):
        factory(1, 2, c=2)


def test_kwonly():
    @curry
    def factory(*args: int, by: int) -> Tuple[int, ...]:
        return args + (by, )

    assert factory(1, 2, 3)(by=10) == (1, 2, 3, 10)
    assert factory(by=10) == (10, )


def test_arg_names_conflict():
    """The decorator should use closures to avoid name conflicts."""
    @curry
    def factory(first, self, args, kwargs):
        return (first, self, args, kwargs)

    assert factory(1)(self=2)(args=3)(kwargs=4) == (1, 2, 3, 4)


def test_raises():
    """TypeError raised from the function must not be intercepted."""
    @curry
    def factory(a, b):
        msg = "f() missing 2 required positional arguments: 'a' and 'b'"
        raise TypeError(msg)

    with pytest.raises(TypeError):
        factory(1)(2)
    with pytest.raises(TypeError):
        factory(1, 2)
    with pytest.raises(TypeError):
        factory(1, 2, 3)  # type: ignore
