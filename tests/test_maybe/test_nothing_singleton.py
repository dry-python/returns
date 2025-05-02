from returns.maybe import _Nothing  # noqa: PLC2701


def test_nothing_singleton():
    """Ensures `_Nothing` is a singleton."""
    assert _Nothing() is _Nothing()
