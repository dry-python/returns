from returns.io import IO


def test_equality():
    """Ensures that containers can be compared."""
    assert IO(1) == IO(1)
    assert str(IO(2)) == '<IO: 2>'
    assert hash(IO((1, 2, 3)))


def test_nonequality():
    """Ensures that containers are not compared to regular values."""
    assert IO(1) != 1
    assert IO(2) is not IO(2)
    assert IO('a') != IO('b')
