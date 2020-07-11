from returns.maybe import Maybe


def test_maybe_types():
    """Checks that we have correct types inside Maybe."""
    assert isinstance(Maybe.success_type, type)
    assert isinstance(Maybe.failure_type, type)
