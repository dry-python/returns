# -*- coding: utf-8 -*-

import pytest

from returns.result import Result


@pytest.mark.parametrize('method_name', [
    'bind',
    'map',
    'rescue',
    'fix',
    'alt',
    'value_or',
])
def test_result_abstract_method(method_name):
    """Checks that Result itself contains abstract methods."""
    method = getattr(Result, method_name)
    with pytest.raises(NotImplementedError):
        method(object, lambda to_output: to_output)


@pytest.mark.parametrize('method_name', [
    'failure',
    'unwrap',
])
def test_result_abstract_method_single(method_name):
    """Checks that Result itself contains abstract methods."""
    method = getattr(Result, method_name)
    with pytest.raises(NotImplementedError):
        method(object)
