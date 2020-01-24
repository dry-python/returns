# -*- coding: utf-8 -*-

from returns.result import Failure, ResultError, Success


def test_result_error_success():
    """Ensures that ResultError can be typecasted to success."""
    container: ResultError[int] = Success(1)
    assert container.unwrap() == 1


def test_result_error_failure():
    """Ensures that ResultError can be typecasted to failure."""
    container: ResultError[int] = Failure(ValueError('1'))
    assert str(container.failure()) == '1'
