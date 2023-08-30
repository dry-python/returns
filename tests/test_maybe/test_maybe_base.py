from returns.maybe import Some, _Nothing


def test_maybe_types():
    """Checks that we have correct types inside Maybe."""
    assert isinstance(Some, type)
    assert isinstance(_Nothing, type)
