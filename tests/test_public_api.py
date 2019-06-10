# -*- coding: utf-8 -*-

import pytest

import returns


@pytest.mark.parametrize('member', [
    'Result',
    'Success',
    'Failure',
    'is_successful',
    'safe',
    'pipeline',
    'raise_exception',
    'compose',
    'IO',
    'impure',
])
def test_public_api(member):
    """Ensures that all public API members are importable."""
    assert getattr(returns, member, None)
