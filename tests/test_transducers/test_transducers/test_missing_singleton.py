from returns.transducers.transducers import _Missing


def test_missing_singleton():
    """Ensures `_Missing` is a singleton."""
    assert _Missing() is _Missing()
