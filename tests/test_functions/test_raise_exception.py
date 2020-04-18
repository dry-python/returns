from typing import Type

import pytest

from returns.functions import raise_exception
from returns.result import Failure, Success


class _CustomException(Exception):
    """Just for the test."""


@pytest.mark.parametrize('exception_type', [
    TypeError,
    ValueError,
    _CustomException,
])
def test_raise_regular_exception(exception_type: Type[Exception]):
    """Ensures that regular exception can be thrown."""
    with pytest.raises(exception_type):
        raise_exception(exception_type())


def test_failure_can_be_fixed():
    """Ensures that exceptions can work with Failures."""
    failure = Failure(ValueError('Message'))
    with pytest.raises(ValueError, match='Message'):
        failure.fix(raise_exception)


def test_success_is_not_touched():
    """Ensures that exceptions can work with Success."""
    assert Success(1).fix(raise_exception) == Success(1)
