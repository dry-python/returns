import pytest

from returns.io import IOFailure, IOSuccess
from returns.maybe import Nothing, Some
from returns.pipeline import is_successful
from returns.result import Failure, Success


@pytest.mark.parametrize(('container', 'correct_result'), [
    (Success('a'), True),
    (Failure('a'), False),

    (IOSuccess('a'), True),
    (IOFailure('a'), False),

    (Some('a'), True),
    (Some(None), False),
    (Nothing, False),
])
def test_is_successful(container, correct_result):
    """Ensures that successful state works correctly."""
    assert is_successful(container) is correct_result
