# -*- coding: utf-8 -*-

import pytest

from dry_monads.either import Left, Right
from dry_monads.primitives.exceptions import UnwrapFailedError


def test_unwrap_success():
    """Ensures that unwrap works for Right monad."""
    with pytest.raises(UnwrapFailedError):
        assert Right(5).failure()


def test_unwrap_failure():
    """Ensures that unwrap works for Left monad."""
    assert Left(5).failure() == 5
