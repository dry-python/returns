# -*- coding: utf-8 -*-

import pytest

from dry_monads.maybe import Nothing, Some
from dry_monads.primitives.exceptions import UnwrapFailedError


def test_unwrap_success():
    """Ensures that unwrap works for Some monad."""
    assert Some(5).unwrap() == 5


def test_unwrap_failure():
    """Ensures that unwrap works for Nothing monad."""
    with pytest.raises(UnwrapFailedError):
        assert Nothing().unwrap()
