# -*- coding: utf-8 -*-

import pytest

from returns.functions import is_successful
from returns.maybe import Nothing, Some
from returns.result import Failure, Success


@pytest.mark.parametrize('container, correct_result', [
    (Some, True),
    (Success, True),
    (Nothing, False),
    (Failure, False),
])
def test_is_successful(container, correct_result):
    """Ensures that successful state works correctly."""
    assert is_successful(container('some value')) is correct_result
