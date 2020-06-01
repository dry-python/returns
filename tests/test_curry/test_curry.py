from inspect import getdoc
from typing import List, Tuple

import pytest

from returns.curry import curry


def test_docstring():
    """Ensures that we preserve docstrings from curried function."""

    @curry
    def factory(arg: int, other: int) -> None:
        """Some docstring."""

    assert getdoc(factory) == 'Some docstring.'


def test_immutable():
    """Check that arguments from previous calls are immutable."""

    @curry
    def factory(arg: int, other: int) -> Tuple[int, int]:
        return (arg, other)

    cached = factory(arg=1)
    assert cached(other=2) == (1, 2)
    assert cached(other=3) == (1, 3)


def test_no_args():
    """Ensures that it is possible to curry a function with empty args."""

    @curry
    def factory() -> int:
        return 1

    assert factory() == 1


def test_one_arg():
    """Ensures that it is possible to curry a function with one arg."""

    @curry
    def factory(arg: int) -> int:
        return arg

    assert factory(1) == 1
    assert factory(arg=1) == 1
    with pytest.raises(TypeError):
        factory(other=2)  # type: ignore
    with pytest.raises(TypeError):
        factory(1, 2)  # type: ignore
    with pytest.raises(TypeError):
        factory(1)(2)  # type: ignore


def test_two_args():
    """Ensures that it is possible to curry a function with two args."""

    @curry
    def factory(arg: int, other: int) -> Tuple[int, int]:
        return (arg, other)

    assert factory(1)(2) == (1, 2)
    assert factory(1, 2) == (1, 2)

    assert factory(2, other=3) == (2, 3)
    assert factory(arg=2, other=3) == (2, 3)
    assert factory(other=3, arg=2) == (2, 3)

    assert factory(arg=0)(other=5) == (0, 5)
    assert factory(0)(other=5) == (0, 5)

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
        factory(arg=1)
    with pytest.raises(TypeError):
        factory(1, other=2)
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

    assert not factory()
    assert factory(arg=1) == [('arg', 1)]
    assert factory(arg=1, other=2) == [('arg', 1), ('other', 2)]

    with pytest.raises(TypeError):
        factory(1)
    with pytest.raises(TypeError):
        factory(1, other=2)


def test_arg_star_kwargs():
    """The decorator should work with ``kwargs``."""

    @curry
    def factory(first: int, **kwargs: int) -> List[Tuple[str, int]]:
        return [('first', first)] + sorted(kwargs.items())

    assert factory(1) == [('first', 1)]
    assert factory(1, arg=2) == [('first', 1), ('arg', 2)]
    assert factory(first=1, arg=2) == [('first', 1), ('arg', 2)]
    assert factory(1, arg=2, other=3) == [
        ('first', 1),
        ('arg', 2),
        ('other', 3),
    ]

    with pytest.raises(TypeError):
        factory(1, 2)
    with pytest.raises(TypeError):
        factory(1, first=2)
    with pytest.raises(TypeError):
        factory(1, 2, c=2)


def test_kwonly():
    """The decorator should work with kw-only args."""

    @curry
    def factory(*args: int, by: int) -> Tuple[int, ...]:
        return args + (by, )

    assert factory(1, 2, 3)(by=10) == (1, 2, 3, 10)
    assert factory(by=10) == (10, )


def test_raises():
    """Exception raised from the function must not be intercepted."""

    @curry
    def factory(arg: int, other: int) -> None:
        msg = "f() missing 2 required positional arguments: 'a' and 'b'"
        raise TypeError(msg)

    with pytest.raises(TypeError):
        factory(1)(2)
    with pytest.raises(TypeError):
        factory(1, 2)
    with pytest.raises(TypeError):
        factory(1, 2, 3)  # type: ignore
