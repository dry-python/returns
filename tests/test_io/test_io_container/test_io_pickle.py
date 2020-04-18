from returns.io import IO


def test_io_pickle():
    """Tests how pickle protocol works for containers."""
    assert IO(1).__getstate__() == 1  # noqa: WPS609


def test_io_pickle_restore():
    """Ensures that object can be restored."""
    container = IO(2)
    container.__setstate__(1)  # noqa: WPS609
    assert container == IO(1)
