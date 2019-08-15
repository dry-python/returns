# -*- coding: utf-8 -*-

import pytest

from returns.converters import join
from returns.io import IO
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize(('container', 'merged'), [
    (IO(IO(1)), IO(1)),
    (Failure(Failure('a')), Failure('a')),
    (Success(Success({})), Success({})),
    (Some(Some(None)), Nothing),
    (Some(Some([])), Some([])),
])
def test_join(container, merged):
    """Ensures that `join` is always returning the correct type."""
    assert join(container) == merged
