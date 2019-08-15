# -*- coding: utf-8 -*-

import pytest

from returns.maybe import Maybe


@pytest.mark.parametrize('method_name', [
    'bind',
    'map',
    'rescue',
    'fix',
    'value_or',
])
def test_maybe_abstract_method(method_name):
    """Checks that Maybe itself contains abstract methods."""
    method = getattr(Maybe, method_name)
    with pytest.raises(NotImplementedError):
        method(object, lambda to_output: to_output)


@pytest.mark.parametrize('method_name', [
    'unwrap',
])
def test_maybe_abstract_method_single(method_name):
    """Checks that Maybe itself contains abstract methods."""
    method = getattr(Maybe, method_name)
    with pytest.raises(NotImplementedError):
        method(object)
