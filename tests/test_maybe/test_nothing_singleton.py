from returns.maybe import _Nothing


def test_nothing_singleton():
    """Ensures `_Nothing` is a singleton."""
    assert _Nothing() is _Nothing()
