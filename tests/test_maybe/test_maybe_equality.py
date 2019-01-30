# -*- coding: utf-8 -*-

import pytest

from dry_monads.maybe import Nothing, Some
from dry_monads.primitives.exceptions import ImmutableStateError


def test_nonequality():
    """Ensures that monads are not compared to regular values."""
    assert Nothing() is not None
    assert Nothing(None) is not None
    assert Some(5) != 5
    assert Some(None) != Nothing()


def test_is_compare():
    """Ensures that `is` operator works correctly."""
    nothing = Nothing()
    some_monad = Some(1)

    assert nothing.bind(lambda state: state) is nothing
    assert some_monad.ebind(lambda state: state) is some_monad
    assert some_monad is not Some(1)


def test_immutability_failure():
    """Ensures that Failure monad is immutable."""
    with pytest.raises(ImmutableStateError):
        Nothing()._inner_state = 1  # noqa: Z441

    with pytest.raises(ImmutableStateError):
        Nothing().missing = 2

    with pytest.raises(ImmutableStateError):
        del Nothing()._inner_state  # type: ignore # noqa: Z420, Z441

    with pytest.raises(AttributeError):
        Nothing().missing  # type: ignore # noqa: Z444


def test_immutability_success():
    """Ensures that Success monad is immutable."""
    with pytest.raises(ImmutableStateError):
        Some(0)._inner_state = 1  # noqa: Z441

    with pytest.raises(ImmutableStateError):
        Some(1).missing = 2

    with pytest.raises(ImmutableStateError):
        del Some(0)._inner_state  # type: ignore # noqa: Z420, Z441

    with pytest.raises(AttributeError):
        Some(1).missing  # type: ignore # noqa: Z444
