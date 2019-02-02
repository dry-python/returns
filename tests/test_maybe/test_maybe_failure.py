# -*- coding: utf-8 -*-

import pytest

from returns.maybe import Nothing, Some
from returns.primitives.exceptions import UnwrapFailedError


def test_unwrap_success():
    """Ensures that unwrap works for Some monad."""
    with pytest.raises(UnwrapFailedError):
        assert Some(1).failure()


def test_unwrap_failure():
    """Ensures that unwrap works for Nothing monad."""
    assert Nothing().failure() is None  # type: ignore
