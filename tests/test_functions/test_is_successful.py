# -*- coding: utf-8 -*-

import pytest

from dry_monads.either import Failure, Success
from dry_monads.functions import is_successful
from dry_monads.maybe import Nothing, Some


@pytest.mark.parametrize('monad, correct_result', [
    (Some, True),
    (Success, True),
    (Nothing, False),
    (Failure, False),
])
def test_is_successful(monad, correct_result):
    """Ensures that successful state works correctly."""
    assert is_successful(monad(1)) is correct_result
