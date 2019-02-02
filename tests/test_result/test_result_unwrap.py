# -*- coding: utf-8 -*-

import pytest

from returns.primitives.exceptions import UnwrapFailedError
from returns.result import Failure, Success


def test_unwrap_success():
    """Ensures that unwrap works for Success monad."""
    assert Success(5).unwrap() == 5


def test_unwrap_failure():
    """Ensures that unwrap works for Failure monad."""
    with pytest.raises(UnwrapFailedError):
        assert Failure(5).unwrap()
