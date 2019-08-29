# -*- coding: utf-8 -*-

import pytest

from returns.maybe import Nothing, Some
from returns.primitives.exceptions import UnwrapFailedError


def test_unwrap_success():
    """Ensures that unwrap works for Some container."""
    assert Some(5).unwrap() == 5


def test_unwrap_failure():
    """Ensures that unwrap works for Nothing container."""
    with pytest.raises(UnwrapFailedError):
        assert Nothing.unwrap()


def test_unwrap_failure_from_success():
    """Ensures that failure works for Some container."""
    with pytest.raises(UnwrapFailedError):
        Some(5).failure()


def test_unwrap_failure_from_failure():
    """Ensures that failure works for Nothing container."""
    assert Nothing.failure() is None  # type: ignore
