# -*- coding: utf-8 -*-

import pytest

import returns


@pytest.mark.parametrize('member', [
    # Functions:
    'compose',
    'raise_exception',

    # IO:
    'IO',
    'impure',

    # Maybe:
    'Some',
    'Nothing',
    'Maybe',
    'maybe',

    # Result:
    'safe',
    'Failure',
    'Result',
    'Success',
    'UnwrapFailedError',

    # pipeline:
    'is_successful',
    'pipeline',

    # Converters:
    'result_to_maybe',
    'maybe_to_result',
])
def test_public_api(member):
    """Ensures that all public API members are importable."""
    assert getattr(returns, member, None)
