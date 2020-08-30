from returns.io import IO


def test_equals():
    """Ensures that ``.equals`` method works correctly."""
    assert IO(1).equals(IO(1))
    assert IO(1).equals(IO.from_value(1))


def test_not_equals():
    """Ensures that ``.equals`` method works correctly."""
    assert not IO(1).equals(IO('a'))


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
