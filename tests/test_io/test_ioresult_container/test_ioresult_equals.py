from returns.io import IOFailure, IOSuccess


def test_equals():
    """Ensures that ``.equals`` method works correctly."""
    inner_value = 1

    assert IOSuccess(inner_value).equals(IOSuccess(inner_value))
    assert IOFailure(inner_value).equals(IOFailure(inner_value))


def test_not_equals():
    """Ensures that ``.equals`` method works correctly."""
    inner_value = 1

    assert not IOSuccess(inner_value).equals(IOFailure(inner_value))
    assert not IOSuccess(inner_value).equals(IOSuccess(0))
    assert not IOFailure(inner_value).equals(IOSuccess(inner_value))
    assert not IOFailure(inner_value).equals(IOFailure(0))
